from http import HTTPStatus

import pytest
from flask import Flask

from backend.core import db
from backend.core.models import auth_models, event_models, merch_models, news_models, ref_models  # noqa: F401
from backend.core.models.auth_models import RoleEnum, User
from backend.core.models.merch_models import MerchCartItem, MerchFavorite, MerchProduct
from backend.core.services import merch_service


@pytest.fixture(scope="module")
def merch_app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def clean_merch_db(merch_app):
    with merch_app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield
        db.session.rollback()


def test_complete_merch_customer_flow(clean_merch_db, monkeypatch):
    user = User(
        full_name="Иванов Иван",
        email="buyer@example.test",
        password_hash="hash",
        role=RoleEnum.USER,
    )
    db.session.add(user)
    db.session.commit()

    category_response, status = merch_service.create_category(
        {"name": "Hoodies", "description": "Warm clothes", "order_index": 2}
    )
    assert status == HTTPStatus.CREATED
    category_id = category_response["category"]["category_id"]

    banner_response, status = merch_service.create_banner(
        {"image_path": "media/banner.jpg", "title": "Drop", "is_active": True}
    )
    assert status == HTTPStatus.CREATED
    assert banner_response["banner"]["title"] == "Drop"

    product_data = {
        "category_id": category_id,
        "name": "Black Hoodie",
        "description": "Oversize hoodie",
        "price": "3500.00",
        "collection": "Summer",
        "images": [{"image_path": "media/hoodie.jpg", "order_index": 0}],
        "colors": [{
            "name": "Black",
            "hex_code": "#000000",
            "sizes": [{"size_name": "M", "stock": 4, "is_active": True}],
        }],
    }
    product_response, status = merch_service.create_product(product_data)
    assert status == HTTPStatus.CREATED
    product_id = product_response["product"]["product_id"]
    variant_id = product_response["product"]["colors"][0]["sizes"][0]["variant_id"]

    assert merch_service.list_products(search="hoodie")[0]["product_id"] == product_id
    assert merch_service.list_products(search="summer")[0]["product_id"] == product_id
    assert merch_service.list_products(search="hoodies")[0]["product_id"] == product_id
    assert merch_service.list_products(search="missing") == []
    assert merch_service.get_product_detail(product_id)["available"] == 4

    favorite_response, status = merch_service.toggle_favorite(user.email, product_id)
    assert (favorite_response, status) == ({"is_favorite": True}, HTTPStatus.CREATED)
    assert merch_service.list_products(user_id=user.user_id)[0]["is_favorite"] is True
    assert merch_service.list_favorites(user.email)[0]["favorites"][0]["product"]["product_id"] == product_id

    cart_response, status = merch_service.upsert_cart_item(user.email, variant_id, 2)
    assert status == HTTPStatus.OK
    assert cart_response["item"]["quantity"] == 2
    cart, status = merch_service.get_cart(user.email)
    assert status == HTTPStatus.OK
    assert cart["total_price"] == "7000.00"

    cart_response, status = merch_service.upsert_cart_item(user.email, variant_id, 3)
    assert status == HTTPStatus.OK
    assert cart_response["item"]["quantity"] == 3

    order_payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "contact_channel": "@ivan",
        "delivery_method": "pickup",
        "pay_by_card": False,
    }
    order_response, status = merch_service.create_order(user.email, order_payload)
    assert status == HTTPStatus.CREATED
    assert order_response["order"]["total_price"] == "10500.00"
    assert order_response["order"]["status"] == "new"
    assert merch_service.get_cart(user.email)[0]["items"] == []
    assert merch_service.list_orders(user.email)[0]["orders"][0]["order_id"] == order_response["order"]["order_id"]

    product = db.session.get(MerchProduct, product_id)
    assert product.variants[0].stock == 1
    updated, status = merch_service.update_product(product_id, {"price": "3700", "collection": "Autumn"})
    assert status == HTTPStatus.OK
    assert updated["product"]["price"] == "3700.00"

    favorite_response, status = merch_service.toggle_favorite(user.email, product_id)
    assert (favorite_response, status) == ({"is_favorite": False}, HTTPStatus.OK)


def test_delete_cart_item_and_soft_delete_product(clean_merch_db):
    user = User(full_name="User", email="user@example.test", password_hash="hash", role=RoleEnum.USER)
    db.session.add(user)
    category, _ = merch_service.create_category({"name": "Caps"})
    product, _ = merch_service.create_product({
        "category_id": category["category"]["category_id"], "name": "Cap", "price": 1000,
        "colors": [{"name": "Red", "sizes": [{"size_name": "One", "stock": 2}]}],
    })
    product_id = product["product"]["product_id"]
    variant_id = product["product"]["colors"][0]["sizes"][0]["variant_id"]
    item, _ = merch_service.upsert_cart_item(user.email, variant_id, 1)
    cart_item_id = item["item"]["cart_item_id"]

    assert merch_service.delete_cart_item(user.email, 999)[1] == HTTPStatus.NOT_FOUND
    assert merch_service.delete_cart_item(user.email, cart_item_id) == (
        {"message": "Cart item deleted"}, HTTPStatus.OK
    )
    merch_service.toggle_favorite(user.email, product_id)
    assert MerchFavorite.query.count() == 1

    assert merch_service.delete_product(product_id) == ({"message": "Product deleted"}, HTTPStatus.OK)
    assert db.session.get(MerchProduct, product_id).is_deleted is True
    assert MerchFavorite.query.count() == 0
    assert MerchCartItem.query.count() == 0
    assert merch_service.get_product_detail(product_id) is None
