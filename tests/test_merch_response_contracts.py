import json
from datetime import datetime
from decimal import Decimal

from backend.core.models import auth_models, event_models, merch_models, news_models, ref_models  # noqa: F401
from backend.core.models.merch_models import (
    MerchBanner,
    MerchCartItem,
    MerchCategory,
    MerchFavorite,
    MerchOrder,
    MerchOrderItem,
    MerchProduct,
    MerchProductColor,
    MerchProductImage,
    MerchProductVariant,
    MerchSize,
)


REMOVED_FIELDS = {"payment_method", "sku"}


def assert_removed_fields_absent(payload):
    if isinstance(payload, dict):
        assert not (REMOVED_FIELDS & payload.keys())
        for value in payload.values():
            assert_removed_fields_absent(value)
    elif isinstance(payload, list):
        for item in payload:
            assert_removed_fields_absent(item)


def make_product_graph():
    category = MerchCategory(
        category_id=1,
        name="Shirts",
        slug="shirts",
        description="Printed shirts",
        order_index=1,
        is_active=True,
    )
    product = MerchProduct(
        product_id=10,
        category=category,
        name="UKNO Shirt",
        description="Black shirt",
        price=Decimal("2500.00"),
        collection="Summer 2026",
        is_active=True,
        created_at=datetime(2026, 7, 1, 12, 0, 0),
    )
    image = MerchProductImage(
        image_id=100,
        product=product,
        product_id=product.product_id,
        image_path="media/uploads/merch/products/shirt.jpg",
        order_index=0,
    )
    color = MerchProductColor(
        color_id=20,
        product=product,
        product_id=product.product_id,
        name="Black",
        hex_code="#000000",
    )
    size = MerchSize(size_id=30, name="L", order_index=1, is_active=True)
    variant = MerchProductVariant(
        variant_id=40,
        product=product,
        product_id=product.product_id,
        color=color,
        color_id=color.color_id,
        size=size,
        size_id=size.size_id,
        stock=7,
        is_active=True,
    )
    product.images = [image]
    product.colors = [color]
    product.variants = [variant]
    return product, variant


def assert_json_contract(payload):
    assert_removed_fields_absent(payload)
    encoded = json.dumps(payload, ensure_ascii=False)
    for field in REMOVED_FIELDS:
        assert field not in encoded


def test_merch_catalog_and_cart_responses_do_not_expose_removed_fields():
    product, variant = make_product_graph()
    cart_item = MerchCartItem(
        cart_item_id=50,
        user_id=1,
        variant=variant,
        variant_id=variant.variant_id,
        quantity=2,
    )
    favorite = MerchFavorite(
        favorite_id=60,
        user_id=1,
        product=product,
        product_id=product.product_id,
        created_at=datetime(2026, 7, 1, 13, 0, 0),
    )
    banner = MerchBanner(
        banner_id=70,
        image_path="media/uploads/merch/banners/main.jpg",
        title="Main",
        description="New collection",
        image_text="UKNO MERCH",
        link_url="/merch/products",
        order_index=0,
        is_active=True,
        created_at=datetime(2026, 7, 1, 14, 0, 0),
    )

    payloads = [
        banner.to_dict(),
        product.category.to_dict(),
        product.to_list_dict(is_favorite=True),
        product.to_detail_dict(is_favorite=True),
        cart_item.to_dict(is_favorite=True),
        favorite.to_dict(),
    ]

    for payload in payloads:
        assert_json_contract(payload)

    detail = product.to_detail_dict()
    assert detail["colors"][0]["sizes"][0]["variant_id"] == variant.variant_id
    assert "variant_id" in cart_item.to_dict()


def test_merch_order_responses_use_current_payment_and_variant_fields():
    _, variant = make_product_graph()
    order = MerchOrder(
        order_id=80,
        user_id=1,
        last_name="Ivanov",
        first_name="Ivan",
        patronymic=None,
        contact_channel="@ivanov",
        delivery_method="pickup",
        pay_by_card=True,
        status="awaiting_payment",
        total_price=Decimal("2500.00"),
        payment_id="pay_123",
        payment_url="https://example.test/pay",
        created_at=datetime(2026, 7, 1, 15, 0, 0),
    )
    order.items = [
        MerchOrderItem(
            order_item_id=90,
            order=order,
            order_id=order.order_id,
            variant=variant,
            variant_id=variant.variant_id,
            product_name="UKNO Shirt",
            color_name="Black",
            size_name="L",
            unit_price=Decimal("2500.00"),
            quantity=1,
            total_price=Decimal("2500.00"),
        )
    ]

    payload = {"order": order.to_dict(), "orders": [order.to_dict()]}

    assert_json_contract(payload)
    assert payload["order"]["pay_by_card"] is True
    assert payload["order"]["payment_id"] == "pay_123"
    assert payload["order"]["payment_url"] == "https://example.test/pay"
    assert payload["order"]["items"][0]["variant_id"] == variant.variant_id
