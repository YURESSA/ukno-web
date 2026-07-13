from http import HTTPStatus

from flask import request
from flask_restx import Resource, fields, reqparse
from werkzeug.datastructures import FileStorage

from . import admin_ns
from .decorators import admin_required
from backend.core import db
from backend.core.services.merch_service import (
    add_product_color,
    add_product_color_size,
    create_banner,
    create_category,
    create_product,
    add_product_images,
    delete_banner,
    delete_category,
    delete_product,
    delete_product_image,
    list_banners,
    list_categories,
    list_orders,
    list_product_images,
    parse_json_payload,
    update_banner,
    update_category,
    update_product_image,
    update_product,
)


BANNER_DATA_EXAMPLE = """{
  "title": "Главный баннер мерча",
  "description": "Новая коллекция уже доступна",
  "image_text": "UKNO MERCH",
  "button_text": "Купить",
  "link_url": "/merch/products",
  "order_index": 0,
  "is_active": true
}"""

CATEGORY_DATA_EXAMPLE = """{
  "name": "Футболки",
  "slug": "tshirts",
  "description": "Футболки и лонгсливы",
  "order_index": 0,
  "is_active": true
}"""

PRODUCT_DATA_EXAMPLE = """{
  "category_id": 1,
  "name": "Футболка UKNO",
  "description": "Черная футболка с принтом",
  "price": 2500,
  "collection": "Summer 2026",
  "is_active": true,
  "colors": [
    {
      "name": "Черный",
      "hex_code": "#000000",
      "sizes": [
        {
          "size_name": "52",
          "stock": 10,
          "is_active": true
        },
        {
          "size_name": "54",
          "stock": 7,
          "is_active": true
        }
      ]
    },
    {
      "name": "Белый",
      "hex_code": "#ffffff",
      "sizes": [
        {
          "size_name": "52",
          "stock": 4,
          "is_active": true
        }
      ]
    }
  ]
}"""

PRODUCT_FORM_PARAMS = {
    "data": {
        "in": "formData",
        "type": "string",
        "required": True,
        "description": (
            "JSON с данными товара, цветами, размерами и остатками. "
            f"Пример: {PRODUCT_DATA_EXAMPLE}"
        ),
    },
    "images": {
        "in": "formData",
        "type": "file",
        "required": False,
        "multiple": True,
        "description": "Файлы фотографий товара.",
    },
}

PRODUCT_IMAGES_FORM_PARAMS = {
    "images": {
        "in": "formData",
        "type": "file",
        "required": True,
        "multiple": True,
        "description": "Файлы фотографий товара.",
    },
    "order_indexes": {
        "in": "formData",
        "type": "string",
        "required": False,
        "description": "Порядок загруженных фотографий: [0,1,2] или 0,1,2.",
    },
}

PRODUCT_IMAGE_UPDATE_PARAMS = {
    "order_index": {
        "in": "formData",
        "type": "integer",
        "required": False,
        "description": "Порядок показа фотографии товара",
    },
    "image": {
        "in": "formData",
        "type": "file",
        "required": False,
        "description": "Файл фотографии товара",
    },
}


category_model = admin_ns.model(
    "MerchCategoryInput",
    {
        "name": fields.String(required=True, description="Название категории", example="Футболки"),
        "slug": fields.String(required=False, description="Код категории. Если не передать, создастся из name", example="tshirts"),
        "description": fields.String(required=False, description="Описание категории", example="Футболки и лонгсливы"),
        "order_index": fields.Integer(required=False, description="Порядок сортировки", example=0),
        "is_active": fields.Boolean(required=False, description="Показывать категорию публично", example=True),
    },
)

product_color_size_model = admin_ns.model(
    "MerchProductColorSizeInput",
    {
        "size_name": fields.String(required=False, description="Название размера", example="54"),
        "stock": fields.Integer(required=False, description="Остаток варианта товара", example=7),
        "is_active": fields.Boolean(required=False, description="Активность варианта товара", example=True),
    },
)

product_color_model = admin_ns.model(
    "MerchProductColorInput",
    {
        "name": fields.String(required=True, description="Название цвета", example="Белый"),
        "hex_code": fields.String(required=False, description="HEX цвета", example="#ffffff"),
        "sizes": fields.List(
            fields.Nested(product_color_size_model),
            required=False,
            description="Размеры и остатки для этого цвета",
        ),
    },
)


def build_banner_parser(image_required: bool) -> reqparse.RequestParser:
    parser = reqparse.RequestParser()
    parser.add_argument(
        "data",
        type=str,
        location="form",
        required=True,
        help=f"JSON с полями баннера. Пример: {BANNER_DATA_EXAMPLE}",
    )
    parser.add_argument(
        "image",
        type=FileStorage,
        location="files",
        required=image_required,
        help="Файл изображения баннера",
    )
    return parser


def build_product_parser() -> reqparse.RequestParser:
    parser = reqparse.RequestParser()
    parser.add_argument(
        "data",
        type=str,
        location="form",
        required=True,
        help=(
            "JSON с данными товара, цветами, размерами и остатками. "
            f"Пример: {PRODUCT_DATA_EXAMPLE}"
        ),
    )
    parser.add_argument(
        "images",
        type=FileStorage,
        location="files",
        action="append",
        required=False,
        help="Файлы фотографий товара. Можно добавить любое количество файлов.",
    )
    return parser


banner_create_parser = build_banner_parser(image_required=True)
banner_update_parser = build_banner_parser(image_required=False)
product_form_parser = build_product_parser()


def request_data():
    if request.content_type and request.content_type.startswith("application/x-www-form-urlencoded"):
        raw_data = request.get_data(as_text=True, cache=True).strip()
        if raw_data.startswith("{"):
            payload, error = parse_json_payload(raw_data)
            if error:
                return None, error
            if isinstance(payload, dict) and "data" in payload:
                return parse_json_payload(payload.get("data"))
            return payload, None

    if "data" in request.form:
        data, error = parse_json_payload(request.form.get("data", "{}"))
        return data, error
    json_data = request.get_json(silent=True) or {}
    if isinstance(json_data, dict) and "data" in json_data:
        data, error = parse_json_payload(json_data.get("data"))
        return data, error
    return json_data, None


def request_images(field_name="images"):
    images = []
    images.extend(request.files.getlist(field_name))
    images.extend(request.files.getlist("image"))
    images.extend(request.files.getlist("image_2"))
    images.extend(request.files.getlist("image_3"))
    return images


def request_order_indexes():
    value = request.form.get("order_indexes")
    if not value:
        return None

    parsed, error = parse_json_payload(value)
    if not error and isinstance(parsed, list):
        return parsed
    return [item.strip() for item in value.split(",") if item.strip()]


@admin_ns.route("/merch/banners")
class AdminMerchBanners(Resource):
    @admin_required
    @admin_ns.doc(description="Получение всех рекламных баннеров мерча для админки")
    def get(self):
        """Получение всех рекламных баннеров мерча."""
        return {"banners": [banner.to_dict() for banner in list_banners(active_only=False)]}, HTTPStatus.OK

    @admin_required
    @admin_ns.expect(banner_create_parser)
    @admin_ns.doc(
        description=(
            "Создание рекламного баннера мерча. Данные баннера передаются JSON в поле data. "
            "Изображение загружается файлом в поле image."
        ),
        responses={201: "Баннер создан", 400: "Ошибка в данных"},
    )
    def post(self):
        """
        Создание рекламного баннера мерча.
        """
        data, error = request_data()
        if error:
            return {"message": error}, HTTPStatus.BAD_REQUEST
        return create_banner(data, request.files.get("image"))


@admin_ns.route("/merch/banners/<int:banner_id>")
class AdminMerchBannerDetail(Resource):
    @admin_required
    @admin_ns.expect(banner_update_parser)
    @admin_ns.doc(
        description=(
            "Обновление рекламного баннера мерча. Данные баннера передаются JSON в поле data. "
            "Изображение загружается файлом в поле image."
        ),
        responses={200: "Баннер обновлен", 404: "Баннер не найден"},
    )
    def put(self, banner_id):
        """Обновление рекламного баннера мерча."""
        data, error = request_data()
        if error:
            return {"message": error}, HTTPStatus.BAD_REQUEST
        return update_banner(banner_id, data, request.files.get("image"))

    @admin_required
    @admin_ns.doc(description="Удаление рекламного баннера мерча")
    def delete(self, banner_id):
        """Удаление рекламного баннера мерча."""
        return delete_banner(banner_id)


@admin_ns.route("/merch/categories")
class AdminMerchCategories(Resource):
    @admin_required
    @admin_ns.doc(description="Получение всех категорий товаров мерча для админки")
    def get(self):
        """Получение всех категорий товаров мерча."""
        return {"categories": [category.to_dict() for category in list_categories(active_only=False)]}, HTTPStatus.OK

    @admin_required
    @admin_ns.expect(category_model, validate=True)
    @admin_ns.doc(
        description="Создание категории товаров мерча. Категория не содержит изображения.",
        responses={201: "Категория создана", 400: "Ошибка в данных"},
    )
    def post(self):
        """
        Создание категории товаров мерча.

        JSON:
        {
          "name": "Футболки",
          "slug": "tshirts",
          "description": "Футболки и лонгсливы",
          "order_index": 0,
          "is_active": true
        }
        """
        return create_category(request.get_json() or {})


@admin_ns.route("/merch/categories/<int:category_id>")
class AdminMerchCategoryDetail(Resource):
    @admin_required
    @admin_ns.expect(category_model, validate=True)
    @admin_ns.doc(
        description="Обновление категории товаров мерча. Категория не содержит изображения.",
        responses={200: "Категория обновлена", 404: "Категория не найдена"},
    )
    def put(self, category_id):
        """Обновление категории товаров мерча."""
        return update_category(category_id, request.get_json() or {})

    @admin_required
    @admin_ns.doc(description="Удаление категории товаров мерча")
    def delete(self, category_id):
        """Удаление категории товаров мерча."""
        return delete_category(category_id)


@admin_ns.route("/merch/products")
class AdminMerchProducts(Resource):
    @admin_required
    @admin_ns.doc(
        description="Получение всех товаров мерча для админки",
        params={"category_id": "Фильтр по ID категории"},
    )
    @admin_ns.doc(params={
        "search": "Search by product name, category, or collection",
    })
    def get(self):
        """Получение всех товаров мерча."""
        category_id = request.args.get("category_id", type=int)
        search = request.args.get("search") or request.args.get("q")
        from backend.core.services.merch_service import list_products

        return {"products": list_products(category_id=category_id, active_only=False, search=search)}, HTTPStatus.OK

    @admin_required
    @admin_ns.doc(
        description=(
            "Создание товара мерча. Данные товара, цвета, размеры и остатки передаются JSON в поле data. "
            "Фотографии товара загружаются файлами в поле images."
        ),
        params=PRODUCT_FORM_PARAMS,
        consumes=["multipart/form-data"],
        responses={201: "Товар создан", 400: "Ошибка в данных"},
    )
    def post(self):
        """
        Создание товара мерча.
        """
        data, error = request_data()
        if error:
            return {"message": error}, HTTPStatus.BAD_REQUEST
        try:
            return create_product(data, request_images())
        except ValueError as exc:
            db.session.rollback()
            return {"message": str(exc)}, HTTPStatus.BAD_REQUEST


@admin_ns.route("/merch/products/<int:product_id>")
class AdminMerchProductDetail(Resource):
    @admin_required
    @admin_ns.doc(description="Получение детальной информации о товаре мерча для админки")
    def get(self, product_id):
        """Получение детальной информации о товаре мерча."""
        from backend.core.services.merch_service import get_product_detail

        product = get_product_detail(product_id, active_only=False)
        if not product:
            return {"message": "Product not found"}, HTTPStatus.NOT_FOUND
        return product, HTTPStatus.OK

    @admin_required
    @admin_ns.doc(
        description=(
            "Обновление товара мерча. Данные товара передаются JSON в поле data. "
            "Фотографии товара загружаются файлами в поле images."
        ),
        params=PRODUCT_FORM_PARAMS,
        consumes=["multipart/form-data"],
        responses={200: "Товар обновлен", 404: "Товар не найден"},
    )
    def put(self, product_id):
        """Обновление товара мерча."""
        data, error = request_data()
        if error:
            return {"message": error}, HTTPStatus.BAD_REQUEST
        try:
            return update_product(product_id, data, request_images())
        except ValueError as exc:
            db.session.rollback()
            return {"message": str(exc)}, HTTPStatus.BAD_REQUEST

    @admin_required
    @admin_ns.doc(description="Удаление товара мерча")
    def delete(self, product_id):
        """Удаление товара мерча."""
        return delete_product(product_id)


@admin_ns.route("/merch/products/<int:product_id>/colors")
class AdminMerchProductColors(Resource):
    @admin_required
    @admin_ns.expect(product_color_model, validate=True)
    @admin_ns.doc(
        description=(
            "Добавление цвета товара мерча. "
            "Размеры и остатки передаются в поле sizes."
        ),
        responses={201: "Цвет добавлен", 400: "Ошибка в данных", 404: "Товар не найден"},
    )
    def post(self, product_id):
        """
        Добавление цвета товара мерча.
        """
        return add_product_color(product_id, request.get_json() or {})


@admin_ns.route("/merch/products/<int:product_id>/colors/<int:color_id>/sizes")
class AdminMerchProductColorSizes(Resource):
    @admin_required
    @admin_ns.expect(product_color_size_model, validate=True)
    @admin_ns.doc(
        description=(
            "Добавление или обновление размера цвета товара мерча."
        ),
        responses={201: "Размер цвета добавлен или обновлен", 400: "Ошибка в данных", 404: "Товар или цвет не найден"},
    )
    def post(self, product_id, color_id):
        """
        Добавление или обновление размера цвета товара мерча.
        """
        return add_product_color_size(product_id, color_id, request.get_json() or {})


@admin_ns.route("/merch/products/<int:product_id>/images")
class AdminMerchProductImages(Resource):
    @admin_required
    @admin_ns.doc(description="Получение всех фотографий товара мерча")
    def get(self, product_id):
        """Получение всех фотографий товара мерча."""
        return list_product_images(product_id)

    @admin_required
    @admin_ns.doc(
        description="Добавление фотографий к товару мерча",
        params=PRODUCT_IMAGES_FORM_PARAMS,
        consumes=["multipart/form-data"],
        responses={201: "Фотографии добавлены", 400: "Файлы не переданы"},
    )
    def post(self, product_id):
        """
        Добавление фотографий к товару мерча.
        """
        return add_product_images(product_id, request_images(), request_order_indexes())


@admin_ns.route("/merch/products/<int:product_id>/images/<int:image_id>")
class AdminMerchProductImage(Resource):
    @admin_required
    @admin_ns.doc(
        description="Обновление фотографии товара мерча",
        params=PRODUCT_IMAGE_UPDATE_PARAMS,
        consumes=["multipart/form-data"],
        responses={200: "Фотография обновлена", 404: "Фотография не найдена"},
    )
    def put(self, product_id, image_id):
        """Обновление фотографии товара мерча."""
        data = {}
        if "order_index" in request.form:
            data["order_index"] = request.form.get("order_index")
        return update_product_image(product_id, image_id, data, request.files.get("image"))

    @admin_required
    @admin_ns.doc(description="Удаление фотографии товара мерча")
    def delete(self, product_id, image_id):
        """Удаление фотографии товара мерча."""
        return delete_product_image(product_id, image_id)


@admin_ns.route("/merch/orders")
class AdminMerchOrders(Resource):
    @admin_required
    @admin_ns.doc(description="Получение всех заказов мерча для админки")
    def get(self):
        """Получение всех заказов мерча."""
        return list_orders()
