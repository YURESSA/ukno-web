from flask import request
from flask_restx import Resource

from backend.core.schemas.auth_schemas import user_model
from . import user_ns
from backend.core.schemas.user_schemas import user_login
from ...core.services.user_services.auth_service import register_user, login_user


@user_ns.route('/register')
class UserRegister(Resource):
    @user_ns.expect(user_model)
    @user_ns.doc(description="Регистрация обычного пользователя (роль автоматически 'user')")
    def post(self) -> tuple[dict, int]:
        """
        Регистрация нового пользователя.

        :return: Возвращает словарь с данными зарегистрированного пользователя и статус HTTP.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        data = request.get_json()
        return register_user("user", data)


@user_ns.route('/login')
class UserLogin(Resource):
    @user_ns.expect(user_login)
    @user_ns.doc(description="Аутентификация обычного пользователя для получения токена доступа")
    def post(self) -> tuple[dict, int]:
        """
        Вход пользователя и получение JWT-токена.

        :return: Возвращает словарь с JWT-токеном и статус HTTP.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        data = request.get_json() or {}
        response, status = login_user("user", data)
        return response, status
