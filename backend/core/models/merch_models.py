from datetime import datetime
from decimal import Decimal

from backend.core import db


class MerchBanner(db.Model):
    __tablename__ = "merch_banners"

    banner_id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_text = db.Column(db.String(255), nullable=True)
    button_text = db.Column(db.String(100), nullable=True)
    link_url = db.Column(db.String(500), nullable=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        return {
            "banner_id": self.banner_id,
            "image_path": self.image_path,
            "title": self.title,
            "description": self.description,
            "image_text": self.image_text,
            "button_text": self.button_text,
            "link_url": self.link_url,
            "order_index": self.order_index,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


class MerchCategory(db.Model):
    __tablename__ = "merch_categories"

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    products = db.relationship("MerchProduct", back_populates="category", lazy=True)

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "order_index": self.order_index,
            "is_active": self.is_active,
        }


class MerchSize(db.Model):
    __tablename__ = "merch_sizes"

    size_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    variants = db.relationship("MerchProductVariant", back_populates="size", lazy=True)

    def to_dict(self):
        return {
            "size_id": self.size_id,
            "name": self.name,
            "order_index": self.order_index,
            "is_active": self.is_active,
        }


class MerchProduct(db.Model):
    __tablename__ = "merch_products"

    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("merch_categories.category_id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    collection = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    category = db.relationship("MerchCategory", back_populates="products")
    images = db.relationship(
        "MerchProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True,
    )
    colors = db.relationship(
        "MerchProductColor",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True,
    )
    variants = db.relationship(
        "MerchProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def available_quantity(self):
        return sum(variant.stock for variant in self.variants if variant.is_active)

    def sorted_images(self):
        return sorted(self.images, key=lambda image: image.order_index)

    def to_list_dict(self, is_favorite=False, include_images=False):
        data = {
            "product_id": self.product_id,
            "category": self.category.to_dict() if self.category else None,
            "name": self.name,
            "price": str(self.price),
            "collection": self.collection,
            "is_active": self.is_active,
            "is_favorite": is_favorite,
            "available": self.available_quantity(),
        }
        if include_images:
            data["images"] = [image.to_dict() for image in self.sorted_images()]
        return data

    def to_detail_dict(self, is_favorite=False):
        data = self.to_list_dict(is_favorite=is_favorite)
        data.update(
            {
                "description": self.description,
                "images": [image.to_dict() for image in self.sorted_images()],
                "colors": self.color_options(),
                "created_at": self.created_at.isoformat(),
            }
        )
        return data

    def color_options(self):
        options = []
        for color in self.colors:
            variants = [
                variant
                for variant in self.variants
                if variant.color_id == color.color_id and variant.is_active
            ]
            options.append(
                {
                    **color.to_dict(),
                    "available": sum(variant.stock for variant in variants),
                    "sizes": [
                        {
                            "variant_id": variant.variant_id,
                            "size": variant.size.to_dict() if variant.size else None,
                            "stock": variant.stock,
                            "is_active": variant.is_active,
                            "price": str(self.price),
                        }
                        for variant in sorted(variants, key=lambda item: item.size.order_index if item.size else 0)
                    ],
                }
            )
        return options


class MerchProductImage(db.Model):
    __tablename__ = "merch_product_images"

    image_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("merch_products.product_id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship("MerchProduct", back_populates="images")

    def to_dict(self):
        return {
            "image_id": self.image_id,
            "product_id": self.product_id,
            "image_path": self.image_path,
            "order_index": self.order_index,
        }


class MerchProductColor(db.Model):
    __tablename__ = "merch_product_colors"

    color_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("merch_products.product_id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hex_code = db.Column(db.String(20), nullable=True)

    product = db.relationship("MerchProduct", back_populates="colors")
    variants = db.relationship("MerchProductVariant", back_populates="color", lazy=True)

    def to_dict(self):
        return {
            "color_id": self.color_id,
            "product_id": self.product_id,
            "name": self.name,
            "hex_code": self.hex_code,
        }


class MerchProductVariant(db.Model):
    __tablename__ = "merch_product_variants"
    __table_args__ = (
        db.UniqueConstraint("product_id", "size_id", "color_id", name="uq_merch_variant_product_size_color"),
    )

    variant_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("merch_products.product_id"), nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey("merch_sizes.size_id"), nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey("merch_product_colors.color_id"), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    product = db.relationship("MerchProduct", back_populates="variants")
    size = db.relationship("MerchSize", back_populates="variants")
    color = db.relationship("MerchProductColor", back_populates="variants")

    def to_dict(self):
        return {
            "variant_id": self.variant_id,
            "product_id": self.product_id,
            "size": self.size.to_dict() if self.size else None,
            "color": self.color.to_dict() if self.color else None,
            "stock": self.stock,
            "is_active": self.is_active,
            "price": str(self.product.price) if self.product else None,
        }


class MerchFavorite(db.Model):
    __tablename__ = "merch_favorites"
    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_merch_favorite_user_product"),
    )

    favorite_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("merch_products.product_id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", backref=db.backref("merch_favorites", cascade="all, delete-orphan", lazy=True))
    product = db.relationship("MerchProduct")

    def to_dict(self):
        return {
            "favorite_id": self.favorite_id,
            "user_id": self.user_id,
            "product": self.product.to_list_dict(is_favorite=True) if self.product else None,
            "created_at": self.created_at.isoformat(),
        }


class MerchCartItem(db.Model):
    __tablename__ = "merch_cart_items"
    __table_args__ = (
        db.UniqueConstraint("user_id", "variant_id", name="uq_merch_cart_user_variant"),
    )

    cart_item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("merch_product_variants.variant_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    user = db.relationship("User", backref=db.backref("merch_cart_items", cascade="all, delete-orphan", lazy=True))
    variant = db.relationship("MerchProductVariant")

    def subtotal(self):
        if not self.variant or not self.variant.product:
            return Decimal("0")
        return self.variant.product.price * self.quantity

    def to_dict(self, is_favorite=False):
        product = self.variant.product if self.variant else None
        return {
            "cart_item_id": self.cart_item_id,
            "variant_id": self.variant_id,
            "quantity": self.quantity,
            "available": self.variant.stock if self.variant else 0,
            "subtotal": str(self.subtotal()),
            "product": product.to_list_dict(is_favorite=is_favorite) if product else None,
            "size": self.variant.size.to_dict() if self.variant and self.variant.size else None,
            "color": self.variant.color.to_dict() if self.variant and self.variant.color else None,
        }


class MerchOrder(db.Model):
    __tablename__ = "merch_orders"

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100), nullable=True)
    contact_channel = db.Column(db.String(255), nullable=False)
    delivery_method = db.Column(db.String(50), nullable=False, default="pickup")
    pay_by_card = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(50), nullable=False, default="new")
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    payment_id = db.Column(db.String(100), nullable=True)
    payment_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", backref=db.backref("merch_orders", cascade="all, delete-orphan", lazy=True))
    items = db.relationship("MerchOrderItem", back_populates="order", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "patronymic": self.patronymic,
            "contact_channel": self.contact_channel,
            "delivery_method": self.delivery_method,
            "pay_by_card": self.pay_by_card,
            "status": self.status,
            "total_price": str(self.total_price),
            "payment_id": self.payment_id,
            "payment_url": self.payment_url,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat(),
        }


class MerchOrderItem(db.Model):
    __tablename__ = "merch_order_items"

    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("merch_orders.order_id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("merch_product_variants.variant_id"), nullable=True)
    product_name = db.Column(db.String(255), nullable=False)
    color_name = db.Column(db.String(100), nullable=True)
    size_name = db.Column(db.String(100), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("MerchOrder", back_populates="items")
    variant = db.relationship("MerchProductVariant")

    def to_dict(self):
        return {
            "order_item_id": self.order_item_id,
            "variant_id": self.variant_id,
            "product_name": self.product_name,
            "color_name": self.color_name,
            "size_name": self.size_name,
            "unit_price": str(self.unit_price),
            "quantity": self.quantity,
            "total_price": str(self.total_price),
        }
