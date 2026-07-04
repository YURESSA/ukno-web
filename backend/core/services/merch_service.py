import json
import re
from decimal import Decimal
from http import HTTPStatus

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from backend.core import db
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
from backend.core.services.reservation_service.yookassa_service import create_yookassa_payment
from backend.core.services.user_services.user_service import get_user_by_email
from backend.core.utilits.file_utils import remove_file_if_exists, save_image


DELIVERY_PICKUP = "pickup"


def slugify(value):
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9а-яё]+", "-", value, flags=re.IGNORECASE)
    return value.strip("-") or "category"


def parse_json_payload(raw_data):
    if isinstance(raw_data, dict):
        return raw_data, None
    if not raw_data:
        return {}, None
    raw_data = raw_data.strip()
    if raw_data.startswith("Пример:"):
        raw_data = raw_data.split(":", 1)[1].strip()
    try:
        return json.loads(raw_data), None
    except json.JSONDecodeError:
        return None, "Invalid JSON payload"


def get_current_user(email):
    user = get_user_by_email(email)
    if not user:
        return None, ({"message": "User not found"}, HTTPStatus.UNAUTHORIZED)
    return user, None


def _bool_value(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes", "y"}


def _int_value(value, default=0):
    if value is None or value == "":
        return default
    return int(value)


def _decimal_value(value):
    return Decimal(str(value))


def list_banners(active_only=True):
    query = MerchBanner.query
    if active_only:
        query = query.filter_by(is_active=True)
    return query.order_by(MerchBanner.order_index.asc(), MerchBanner.banner_id.desc()).all()


def create_banner(data, image_file=None):
    image_path = data.get("image_path")
    if image_file:
        image_path = save_image(image_file, "merch/banners")
    if not image_path:
        return {"message": "image_path or image is required"}, HTTPStatus.BAD_REQUEST

    banner = MerchBanner(
        image_path=image_path,
        title=data.get("title"),
        description=data.get("description"),
        image_text=data.get("image_text"),
        link_url=data.get("link_url"),
        order_index=_int_value(data.get("order_index")),
        is_active=_bool_value(data.get("is_active"), True),
    )
    db.session.add(banner)
    db.session.commit()
    return {"banner": banner.to_dict()}, HTTPStatus.CREATED


def update_banner(banner_id, data, image_file=None):
    banner = db.session.get(MerchBanner, banner_id)
    if not banner:
        return {"message": "Banner not found"}, HTTPStatus.NOT_FOUND

    if image_file:
        remove_file_if_exists(banner.image_path)
        banner.image_path = save_image(image_file, "merch/banners")

    for field in ("title", "description", "image_text", "link_url"):
        if field in data:
            setattr(banner, field, data.get(field))
    if "image_path" in data:
        banner.image_path = data["image_path"]
    if "order_index" in data:
        banner.order_index = _int_value(data.get("order_index"))
    if "is_active" in data:
        banner.is_active = _bool_value(data.get("is_active"), True)

    db.session.commit()
    return {"banner": banner.to_dict()}, HTTPStatus.OK


def delete_banner(banner_id):
    banner = db.session.get(MerchBanner, banner_id)
    if not banner:
        return {"message": "Banner not found"}, HTTPStatus.NOT_FOUND
    remove_file_if_exists(banner.image_path)
    db.session.delete(banner)
    db.session.commit()
    return {"message": "Banner deleted"}, HTTPStatus.OK


def list_categories(active_only=True):
    query = MerchCategory.query
    if active_only:
        query = query.filter_by(is_active=True)
    return query.order_by(MerchCategory.order_index.asc(), MerchCategory.name.asc()).all()


def create_category(data):
    name = data.get("name")
    if not name:
        return {"message": "name is required"}, HTTPStatus.BAD_REQUEST
    slug = data.get("slug") or slugify(name)

    category = MerchCategory(
        name=name,
        slug=slug,
        description=data.get("description"),
        order_index=_int_value(data.get("order_index")),
        is_active=_bool_value(data.get("is_active"), True),
    )
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Category name or slug already exists"}, HTTPStatus.BAD_REQUEST
    return {"category": category.to_dict()}, HTTPStatus.CREATED


def update_category(category_id, data):
    category = db.session.get(MerchCategory, category_id)
    if not category:
        return {"message": "Category not found"}, HTTPStatus.NOT_FOUND

    for field in ("name", "slug", "description"):
        if field in data:
            setattr(category, field, data.get(field))
    if "name" in data and "slug" not in data:
        category.slug = slugify(data["name"])
    if "order_index" in data:
        category.order_index = _int_value(data.get("order_index"))
    if "is_active" in data:
        category.is_active = _bool_value(data.get("is_active"), True)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Category name or slug already exists"}, HTTPStatus.BAD_REQUEST
    return {"category": category.to_dict()}, HTTPStatus.OK


def delete_category(category_id):
    category = db.session.get(MerchCategory, category_id)
    if not category:
        return {"message": "Category not found"}, HTTPStatus.NOT_FOUND
    if category.products:
        return {"message": "Category has products"}, HTTPStatus.BAD_REQUEST
    if category.image_path:
        remove_file_if_exists(category.image_path)
    db.session.delete(category)
    db.session.commit()
    return {"message": "Category deleted"}, HTTPStatus.OK


def list_products(category_id=None, active_only=True, user_id=None):
    query = MerchProduct.query
    if active_only:
        query = query.filter_by(is_active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    products = query.order_by(MerchProduct.created_at.desc()).all()
    favorite_ids = set()
    if user_id:
        favorite_ids = {
            row.product_id
            for row in MerchFavorite.query.filter_by(user_id=user_id).all()
        }
    return [product.to_list_dict(is_favorite=product.product_id in favorite_ids) for product in products]


def get_product_detail(product_id, user_id=None, active_only=True):
    product = db.session.get(MerchProduct, product_id)
    if not product or (active_only and not product.is_active):
        return None
    is_favorite = False
    if user_id:
        is_favorite = MerchFavorite.query.filter_by(user_id=user_id, product_id=product_id).first() is not None
    return product.to_detail_dict(is_favorite=is_favorite)


def create_product(data, image_files=None):
    required = ("category_id", "name", "price")
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        return {"message": f"Missing fields: {', '.join(missing)}"}, HTTPStatus.BAD_REQUEST
    category = db.session.get(MerchCategory, data["category_id"])
    if not category:
        return {"message": "Category not found"}, HTTPStatus.NOT_FOUND

    product = MerchProduct(
        category_id=data["category_id"],
        name=data["name"],
        description=data.get("description"),
        price=_decimal_value(data["price"]),
        collection=data.get("collection"),
        is_active=_bool_value(data.get("is_active"), True),
    )
    db.session.add(product)
    db.session.flush()

    for index, image_file in enumerate(image_files or []):
        product.images.append(
            MerchProductImage(image_path=save_image(image_file, "merch/products"), order_index=index)
        )
    for image in data.get("images", []):
        if not image.get("image_path"):
            continue
        product.images.append(
            MerchProductImage(
                image_path=image.get("image_path"),
                order_index=_int_value(image.get("order_index"), len(product.images)),
            )
        )
    _sync_colors(product, data.get("colors", []))
    _sync_variants(product, _collect_variants(product, data))

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Product data conflicts with existing records"}, HTTPStatus.BAD_REQUEST
    return {"product": product.to_detail_dict()}, HTTPStatus.CREATED


def update_product(product_id, data, image_files=None):
    product = db.session.get(MerchProduct, product_id)
    if not product:
        return {"message": "Product not found"}, HTTPStatus.NOT_FOUND

    if "category_id" in data:
        category = db.session.get(MerchCategory, data["category_id"])
        if not category:
            return {"message": "Category not found"}, HTTPStatus.NOT_FOUND
        product.category_id = data["category_id"]
    for field in ("name", "description", "collection"):
        if field in data:
            setattr(product, field, data.get(field))
    if "price" in data:
        product.price = _decimal_value(data["price"])
    if "is_active" in data:
        product.is_active = _bool_value(data.get("is_active"), True)

    if image_files:
        start_index = len(product.images)
        for offset, image_file in enumerate(image_files):
            product.images.append(
                MerchProductImage(
                    image_path=save_image(image_file, "merch/products"),
                    order_index=start_index + offset,
                )
            )
    if "colors" in data:
        _sync_colors(product, data.get("colors", []), remove_missing=False)
    if "colors" in data or "variants" in data:
        _sync_variants(product, _collect_variants(product, data))

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Product data conflicts with existing records"}, HTTPStatus.BAD_REQUEST
    return {"product": product.to_detail_dict()}, HTTPStatus.OK


def add_product_color(product_id, data):
    product = db.session.get(MerchProduct, product_id)
    if not product:
        return {"message": "Product not found"}, HTTPStatus.NOT_FOUND
    if not data.get("name"):
        return {"message": "Color name is required"}, HTTPStatus.BAD_REQUEST

    color = _find_product_color(product, color_id=data.get("color_id"), color_name=data.get("name"))
    if color:
        color.name = data.get("name", color.name)
        color.hex_code = data.get("hex_code", color.hex_code)
    else:
        color = MerchProductColor(product=product, name=data.get("name"), hex_code=data.get("hex_code"))
        db.session.add(color)
    db.session.flush()

    try:
        sizes = data.get("sizes", [])
        for size_item in sizes:
            _upsert_product_variant(product, {**size_item, "color_id": color.color_id})
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return {"message": str(exc)}, HTTPStatus.BAD_REQUEST
    except IntegrityError:
        db.session.rollback()
        return {"message": "Product color or size conflicts with existing records"}, HTTPStatus.BAD_REQUEST
    return {"color": color.to_dict(), "product": product.to_detail_dict()}, HTTPStatus.CREATED


def add_product_color_size(product_id, color_id, data):
    product = db.session.get(MerchProduct, product_id)
    if not product:
        return {"message": "Product not found"}, HTTPStatus.NOT_FOUND

    color = _find_product_color(product, color_id=color_id)
    if not color:
        return {"message": "Color not found"}, HTTPStatus.NOT_FOUND

    try:
        variant = _upsert_product_variant(product, {**data, "color_id": color.color_id})
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return {"message": str(exc)}, HTTPStatus.BAD_REQUEST
    except IntegrityError:
        db.session.rollback()
        return {"message": "Product size conflicts with existing records"}, HTTPStatus.BAD_REQUEST
    return {"variant": variant.to_dict(), "color": color.to_dict()}, HTTPStatus.CREATED


def delete_product(product_id):
    product = db.session.get(MerchProduct, product_id)
    if not product:
        return {"message": "Product not found"}, HTTPStatus.NOT_FOUND
    for image in product.images:
        remove_file_if_exists(image.image_path)
    db.session.delete(product)
    db.session.commit()
    return {"message": "Product deleted"}, HTTPStatus.OK


def delete_product_image(product_id, image_id):
    image = MerchProductImage.query.filter_by(product_id=product_id, image_id=image_id).first()
    if not image:
        return {"message": "Image not found"}, HTTPStatus.NOT_FOUND
    remove_file_if_exists(image.image_path)
    db.session.delete(image)
    db.session.commit()
    return {"message": "Image deleted"}, HTTPStatus.OK


def list_product_images(product_id):
    product = db.session.get(MerchProduct, product_id)
    if not product:
        return {"message": "Product not found"}, HTTPStatus.NOT_FOUND
    images = sorted(product.images, key=lambda image: image.order_index)
    return {"images": [image.to_dict() for image in images]}, HTTPStatus.OK


def add_product_images(product_id, image_files, order_indexes=None):
    product = db.session.get(MerchProduct, product_id)
    if not product:
        return {"message": "Product not found"}, HTTPStatus.NOT_FOUND
    if not image_files:
        return {"message": "At least one image is required"}, HTTPStatus.BAD_REQUEST

    start_index = len(product.images)
    for offset, image_file in enumerate(image_files):
        order_index = start_index + offset
        if order_indexes and offset < len(order_indexes):
            order_index = _int_value(order_indexes[offset], order_index)
        product.images.append(
            MerchProductImage(
                image_path=save_image(image_file, "merch/products"),
                order_index=order_index,
            )
        )
    db.session.commit()
    images = sorted(product.images, key=lambda image: image.order_index)
    return {"images": [image.to_dict() for image in images]}, HTTPStatus.CREATED


def update_product_image(product_id, image_id, data, image_file=None):
    image = MerchProductImage.query.filter_by(product_id=product_id, image_id=image_id).first()
    if not image:
        return {"message": "Image not found"}, HTTPStatus.NOT_FOUND

    if "order_index" in data:
        image.order_index = _int_value(data.get("order_index"))
    if image_file:
        remove_file_if_exists(image.image_path)
        image.image_path = save_image(image_file, "merch/products")

    db.session.commit()
    return {"image": image.to_dict()}, HTTPStatus.OK


def _sync_colors(product, colors, remove_missing=True):
    existing = {color.color_id: color for color in product.colors}
    existing_by_name = {color.name.lower(): color for color in product.colors}
    seen_ids = set()
    for item in colors:
        if not item.get("name"):
            raise ValueError("Color name is required")
        color_id = item.get("color_id")
        if color_id and color_id in existing:
            color = existing[color_id]
            color.name = item.get("name", color.name)
            color.hex_code = item.get("hex_code", color.hex_code)
            seen_ids.add(color_id)
        elif item.get("name").lower() in existing_by_name:
            color = existing_by_name[item.get("name").lower()]
            color.hex_code = item.get("hex_code", color.hex_code)
            seen_ids.add(color.color_id)
        else:
            product.colors.append(
                MerchProductColor(name=item.get("name"), hex_code=item.get("hex_code"))
            )
    for color_id, color in existing.items():
        if remove_missing and color_id not in seen_ids and not color.variants:
            db.session.delete(color)
    db.session.flush()


def _sync_variants(product, variants):
    for item in variants:
        _upsert_product_variant(product, item)


def _upsert_product_variant(product, item):
    variant_id = item.get("variant_id")
    variant = db.session.get(MerchProductVariant, variant_id) if variant_id else None
    if variant and variant.product_id != product.product_id:
        raise ValueError("Variant belongs to another product")
    size_id = _resolve_variant_size(item, variant)
    color_id = _resolve_variant_color(product, item)
    if color_id:
        color = db.session.get(MerchProductColor, color_id)
        if not color or color.product_id != product.product_id:
            raise ValueError("Valid color_id is required for variant")
    if variant and color_id and variant.color_id != color_id:
        raise ValueError("Variant belongs to another color")
    if not variant:
        variant = MerchProductVariant.query.filter_by(
            product_id=product.product_id,
            size_id=size_id,
            color_id=color_id,
        ).first()
    is_new = variant is None
    if not variant:
        variant = MerchProductVariant(product_id=product.product_id)
        db.session.add(variant)
    variant.size_id = size_id
    variant.color_id = color_id
    if "stock" in item or is_new:
        variant.stock = _int_value(item.get("stock"), 0)
    if "is_active" in item or is_new:
        variant.is_active = _bool_value(item.get("is_active"), True)
    return variant


def _collect_variants(product, data):
    variants = list(data.get("variants", []))
    for color_item in data.get("colors", []):
        color_sizes = color_item.get("sizes", [])
        if not color_sizes:
            continue

        color_id = color_item.get("color_id")
        color_name = color_item.get("name")
        color = _find_product_color(product, color_id=color_id, color_name=color_name)
        if not color:
            raise ValueError("Valid color is required for color sizes")

        for size_item in color_sizes:
            variant_data = {
                **size_item,
                "color_id": color.color_id,
            }
            variants.append(variant_data)
    return variants


def _find_product_color(product, color_id=None, color_name=None):
    if color_id:
        for color in product.colors:
            if color.color_id == color_id:
                return color
    if color_name:
        normalized = color_name.lower()
        for color in product.colors:
            if color.name.lower() == normalized:
                return color
    return None


def _resolve_variant_size(item, variant=None):
    size_name = str(item.get("size_name") or "").strip()
    if size_name:
        size = MerchSize.query.filter(MerchSize.name.ilike(size_name)).first()
        if size:
            return size.size_id

        next_order = (db.session.query(func.coalesce(func.max(MerchSize.order_index), 0)).scalar() or 0) + 1
        size = MerchSize(name=size_name, order_index=next_order, is_active=True)
        db.session.add(size)
        db.session.flush()
        return size.size_id

    size_id = item.get("size_id")
    if size_id:
        size = db.session.get(MerchSize, size_id)
        if not size:
            raise ValueError("Valid size_id is required for each variant")
        return size.size_id

    if variant:
        return variant.size_id

    raise ValueError("size_name is required for each variant")


def _resolve_variant_color(product, item):
    color_id = item.get("color_id")
    if color_id:
        return color_id
    color_name = item.get("color_name")
    if not color_name:
        return None
    for color in product.colors:
        if color.name.lower() == color_name.lower():
            return color.color_id
    color = MerchProductColor(
        product_id=product.product_id,
        name=color_name,
        hex_code=item.get("hex_code"),
    )
    db.session.add(color)
    db.session.flush()
    return color.color_id


def toggle_favorite(user_email, product_id):
    user, error = get_current_user(user_email)
    if error:
        return error
    product = db.session.get(MerchProduct, product_id)
    if not product or not product.is_active:
        return {"message": "Product not found"}, HTTPStatus.NOT_FOUND

    favorite = MerchFavorite.query.filter_by(user_id=user.user_id, product_id=product_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return {"is_favorite": False}, HTTPStatus.OK

    db.session.add(MerchFavorite(user_id=user.user_id, product_id=product_id))
    db.session.commit()
    return {"is_favorite": True}, HTTPStatus.CREATED


def list_favorites(user_email):
    user, error = get_current_user(user_email)
    if error:
        return error
    favorites = MerchFavorite.query.filter_by(user_id=user.user_id).order_by(MerchFavorite.created_at.desc()).all()
    return {
        "favorites": [favorite.to_dict() for favorite in favorites]
    }, HTTPStatus.OK


def get_cart(user_email):
    user, error = get_current_user(user_email)
    if error:
        return error
    favorite_ids = {
        row.product_id
        for row in MerchFavorite.query.filter_by(user_id=user.user_id).all()
    }
    items = MerchCartItem.query.filter_by(user_id=user.user_id).all()
    total = sum((item.subtotal() for item in items), Decimal("0"))
    return {
        "items": [
            item.to_dict(is_favorite=item.variant.product_id in favorite_ids if item.variant else False)
            for item in items
        ],
        "total_price": str(total),
    }, HTTPStatus.OK


def upsert_cart_item(user_email, variant_id, quantity):
    user, error = get_current_user(user_email)
    if error:
        return error
    variant = db.session.get(MerchProductVariant, variant_id)
    if not variant or not variant.is_active or not variant.product.is_active:
        return {"message": "Variant not found"}, HTTPStatus.NOT_FOUND
    quantity = _int_value(quantity, 1)
    if quantity < 1:
        return {"message": "quantity must be greater than zero"}, HTTPStatus.BAD_REQUEST
    if quantity > variant.stock:
        return {
            "message": "Not enough stock",
            "available": variant.stock,
        }, HTTPStatus.BAD_REQUEST

    item = MerchCartItem.query.filter_by(user_id=user.user_id, variant_id=variant_id).first()
    if item:
        item.quantity = quantity
    else:
        item = MerchCartItem(user_id=user.user_id, variant_id=variant_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    return {"item": item.to_dict()}, HTTPStatus.OK


def delete_cart_item(user_email, cart_item_id):
    user, error = get_current_user(user_email)
    if error:
        return error
    item = MerchCartItem.query.filter_by(user_id=user.user_id, cart_item_id=cart_item_id).first()
    if not item:
        return {"message": "Cart item not found"}, HTTPStatus.NOT_FOUND
    db.session.delete(item)
    db.session.commit()
    return {"message": "Cart item deleted"}, HTTPStatus.OK


def create_order(user_email, data):
    user, error = get_current_user(user_email)
    if error:
        return error

    for field in ("last_name", "first_name", "contact_channel"):
        if not data.get(field):
            return {"message": f"{field} is required"}, HTTPStatus.BAD_REQUEST
    delivery_method = data.get("delivery_method", DELIVERY_PICKUP)
    if delivery_method != DELIVERY_PICKUP:
        return {"message": "Only pickup delivery is supported"}, HTTPStatus.BAD_REQUEST
    if "pay_by_card" not in data:
        return {"message": "pay_by_card is required"}, HTTPStatus.BAD_REQUEST
    pay_by_card = _bool_value(data.get("pay_by_card"), False)

    cart_items = MerchCartItem.query.filter_by(user_id=user.user_id).all()
    if not cart_items:
        return {"message": "Cart is empty"}, HTTPStatus.BAD_REQUEST

    total = Decimal("0")
    for item in cart_items:
        if not item.variant or not item.variant.is_active or not item.variant.product.is_active:
            return {"message": "Cart contains unavailable products"}, HTTPStatus.BAD_REQUEST
        if item.quantity > item.variant.stock:
            return {
                "message": "Not enough stock",
                "variant_id": item.variant_id,
                "available": item.variant.stock,
            }, HTTPStatus.BAD_REQUEST
        total += item.subtotal()

    order = MerchOrder(
        user_id=user.user_id,
        last_name=data["last_name"],
        first_name=data["first_name"],
        patronymic=data.get("patronymic"),
        contact_channel=data["contact_channel"],
        delivery_method=delivery_method,
        pay_by_card=pay_by_card,
        status="awaiting_payment" if pay_by_card else "new",
        total_price=total,
    )
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        variant = item.variant
        product = variant.product
        unit_price = product.price
        variant.stock -= item.quantity
        db.session.add(
            MerchOrderItem(
                order_id=order.order_id,
                variant_id=variant.variant_id,
                product_name=product.name,
                color_name=variant.color.name if variant.color else None,
                size_name=variant.size.name,
                unit_price=unit_price,
                quantity=item.quantity,
                total_price=unit_price * item.quantity,
            )
        )
        db.session.delete(item)

    if pay_by_card and total > 0:
        try:
            payment = create_yookassa_payment(
                amount=float(total),
                email=user.email,
                description=f"Оплата заказа мерча UKNO №{order.order_id}",
                quantity=1,
                metadata={
                    "type": "merch_order",
                    "merch_order_id": order.order_id,
                    "email": user.email,
                },
            )
        except Exception:
            db.session.rollback()
            return {"message": "Failed to create payment"}, HTTPStatus.BAD_GATEWAY
        order.payment_id = payment.id
        order.payment_url = payment.confirmation.confirmation_url

    db.session.commit()
    return {"order": order.to_dict()}, HTTPStatus.CREATED


def list_orders(user_email=None):
    query = MerchOrder.query
    if user_email:
        user, error = get_current_user(user_email)
        if error:
            return error
        query = query.filter_by(user_id=user.user_id)
    orders = query.order_by(MerchOrder.created_at.desc()).all()
    return {"orders": [order.to_dict() for order in orders]}, HTTPStatus.OK


def get_home(user_email=None):
    user_id = None
    if user_email:
        user = get_user_by_email(user_email)
        user_id = user.user_id if user else None
    return {
        "banners": [banner.to_dict() for banner in list_banners(active_only=True)],
        "categories": [category.to_dict() for category in list_categories(active_only=True)],
        "products": list_products(active_only=True, user_id=user_id),
    }, HTTPStatus.OK
