from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from flask_restx import Resource, fields

from . import user_ns
from backend.core.services.merch_service import (
    create_order,
    delete_cart_item,
    get_cart,
    get_home,
    get_product_detail,
    list_categories,
    list_favorites,
    list_orders,
    list_products,
    toggle_favorite,
    upsert_cart_item,
)
from backend.core.services.user_services.user_service import get_user_by_email


cart_item_model = user_ns.model(
    "MerchCartItemInput",
    {
        "variant_id": fields.Integer(
            required=True,
            description="ID варианта из colors[].sizes[].variant_id",
            example=1,
        ),
        "quantity": fields.Integer(
            required=True,
            description="Выбранное количество товара",
            example=2,
        ),
    },
)

cart_quantity_model = user_ns.model(
    "MerchCartQuantityInput",
    {
        "quantity": fields.Integer(
            required=True,
            description="Новое количество товара в корзине",
            example=1,
        ),
    },
)

order_model = user_ns.model(
    "MerchOrderInput",
    {
        "last_name": fields.String(required=True, description="Фамилия покупателя", example="Иванов"),
        "first_name": fields.String(required=True, description="Имя покупателя", example="Иван"),
        "patronymic": fields.String(required=False, description="Отчество покупателя", example="Иванович"),
        "contact_channel": fields.String(
            required=True,
            description="Канал связи: телефон, Telegram, email или другой контакт",
            example="@ivanov",
        ),
        "delivery_method": fields.String(
            required=False,
            default="pickup",
            description="Способ доставки. Сейчас поддерживается только pickup",
            example="pickup",
        ),
        "pay_by_card": fields.Boolean(
            required=True,
            description="true - оплата картой онлайн, false - наличными при получении",
            example=True,
        ),
    },
)


def optional_user_id():
    try:
        verify_jwt_in_request(optional=True)
    except Exception:
        return None
    email = get_jwt_identity()
    user = get_user_by_email(email) if email else None
    return user.user_id if user else None


def optional_user_email():
    try:
        verify_jwt_in_request(optional=True)
    except Exception:
        return None
    return get_jwt_identity()


@user_ns.route("/merch")
class MerchHome(Resource):
    @user_ns.doc(description="Главная страница мерча: рекламные баннеры, категории и лента товаров")
    def get(self):
        """
        Получение главной страницы магазина мерча.
        """
        response, status = get_home(optional_user_email())
        return response, status


@user_ns.route("/merch/categories")
class MerchCategories(Resource):
    @user_ns.doc(description="Получение публичного списка активных категорий товаров мерча")
    def get(self):
        """
        Получение категорий товаров мерча.
        """
        return {
            "categories": [category.to_dict() for category in list_categories(active_only=True)]
        }, HTTPStatus.OK


@user_ns.route("/merch/products")
class MerchProducts(Resource):
    @user_ns.doc(
        description="Получение публичной ленты активных товаров мерча с фильтром по категории",
        params={"category_id": "Необязательный ID категории для фильтрации товаров"},
    )
    @user_ns.doc(params={
        "search": "Search by product name, category, or collection",
    })
    def get(self):
        """
        Получение ленты товаров мерча.
        """
        category_id = request.args.get("category_id", type=int)
        search = request.args.get("search") or request.args.get("q")
        return {
            "products": list_products(
                category_id=category_id,
                active_only=True,
                user_id=optional_user_id(),
                search=search,
            )
        }, HTTPStatus.OK


@user_ns.route("/merch/products/<int:product_id>")
class MerchProductDetail(Resource):
    @user_ns.doc(description="Получение детальной карточки товара мерча: фото, цвета, размеры и остатки")
    def get(self, product_id):
        """
        Детальная карточка товара мерча.
        """
        product = get_product_detail(product_id, user_id=optional_user_id(), active_only=True)
        if not product:
            return {"message": "Product not found"}, HTTPStatus.NOT_FOUND
        return product, HTTPStatus.OK


@user_ns.route("/merch/products/<int:product_id>/favorite")
class MerchFavoriteToggle(Resource):
    @jwt_required()
    @user_ns.doc(description="Добавление товара мерча в избранное или удаление из избранного повторным вызовом")
    def post(self, product_id):
        """
        Переключение избранного для товара мерча.
        """
        return toggle_favorite(get_jwt_identity(), product_id)


@user_ns.route("/merch/favorites")
class MerchFavorites(Resource):
    @jwt_required()
    @user_ns.doc(description="Получение списка избранных товаров мерча текущего пользователя")
    def get(self):
        """
        Получение избранных товаров мерча.
        """
        return list_favorites(get_jwt_identity())


@user_ns.route("/merch/cart")
class MerchCart(Resource):
    @jwt_required()
    @user_ns.doc(description="Получение корзины мерча текущего пользователя с общей стоимостью")
    def get(self):
        """
        Получение корзины мерча.
        """
        return get_cart(get_jwt_identity())

    @jwt_required()
    @user_ns.expect(cart_item_model, validate=True)
    @user_ns.doc(
        description="Добавление выбранного цвета и размера товара в корзину или обновление количества",
        body=cart_item_model,
        responses={200: "Позиция корзины обновлена", 400: "Недостаточно остатка или ошибка в данных"},
    )
    def post(self):
        """
        Добавление товара в корзину.

        Пример JSON:
        {
          "variant_id": 1,
          "quantity": 2
        }
        """
        data = request.get_json() or {}
        return upsert_cart_item(
            get_jwt_identity(),
            data.get("variant_id"),
            data.get("quantity"),
        )


@user_ns.route("/merch/cart/<int:cart_item_id>")
class MerchCartItem(Resource):
    @jwt_required()
    @user_ns.expect(cart_quantity_model, validate=True)
    @user_ns.doc(
        description="Изменение количества конкретной позиции корзины мерча",
        body=cart_quantity_model,
        responses={200: "Количество обновлено", 400: "Недостаточно остатка или ошибка в данных"},
    )
    def put(self, cart_item_id):
        """
        Изменение количества товара в корзине.

        Пример JSON:
        {
          "quantity": 1
        }
        """
        data = request.get_json() or {}
        cart_response, status = get_cart(get_jwt_identity())
        if status != HTTPStatus.OK:
            return cart_response, status
        current_item = next(
            (item for item in cart_response["items"] if item["cart_item_id"] == cart_item_id),
            None,
        )
        if not current_item:
            return {"message": "Cart item not found"}, HTTPStatus.NOT_FOUND
        return upsert_cart_item(
            get_jwt_identity(),
            current_item["variant_id"],
            data.get("quantity"),
        )

    @jwt_required()
    @user_ns.doc(description="Удаление позиции из корзины мерча")
    def delete(self, cart_item_id):
        """
        Удаление позиции из корзины.
        """
        return delete_cart_item(get_jwt_identity(), cart_item_id)


@user_ns.route("/merch/orders")
class MerchOrders(Resource):
    @jwt_required()
    @user_ns.doc(description="Получение заказов мерча текущего пользователя")
    def get(self):
        """
        Получение своих заказов мерча.
        """
        return list_orders(get_jwt_identity())

    @jwt_required()
    @user_ns.expect(order_model, validate=True)
    @user_ns.doc(
        description=(
            "Оформление заказа мерча из текущей корзины. "
            "Остатки проверяются и списываются при создании заказа."
        ),
        body=order_model,
        responses={201: "Заказ создан", 400: "Корзина пуста, недостаточно остатка или ошибка в данных"},
    )
    def post(self):
        """
        Оформление заказа мерча.

        Пример JSON:
        {
          "last_name": "Иванов",
          "first_name": "Иван",
          "patronymic": "Иванович",
          "contact_channel": "@ivanov",
          "delivery_method": "pickup",
          "pay_by_card": true
        }
        """
        data = request.get_json() or {}
        return create_order(get_jwt_identity(), data)
