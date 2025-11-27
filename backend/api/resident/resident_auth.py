from flask import request
from flask_restx import Resource

from . import resident_ns
from .decorators import resident_required
from backend.core.schemas.auth_schemas import login_model, change_password_model
from backend.core.services.user_services.auth_service import change_profile_password, login_user
from backend.core.services.user_services.profile_service import get_profile, get_user_info_response, \
    delete_profile


@resident_ns.route('/login')
class ResidentLogin(Resource):
    @resident_ns.expect(login_model)
    @resident_ns.doc(description="Аутентификация резидента для получения токена доступа")
    def post(self) -> tuple[dict, int]:
        """
        Вход резидента и получение JWT-токена.

        :return: Словарь с JWT-токеном и HTTP-статус.
        """
        data: dict = request.get_json() or {}
        response, status = login_user("resident", data)
        return response, status


@resident_ns.route('/profile')
class ResidentProfile(Resource):
    @resident_required
    @resident_ns.doc(description="Получение информации о резиденте")
    def get(self) -> tuple[dict, int]:
        """
        Получение профиля текущего резидента.

        :return: Словарь с данными резидента и HTTP-статус.
                 В случае ошибки — словарь с сообщением и соответствующий статус.
        """
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user)

    @resident_required
    @resident_ns.expect(change_password_model, validate=True)
    @resident_ns.doc(description="Изменение пароля резидента")
    def put(self) -> tuple[dict, int]:
        """
        Смена пароля текущего резидента.

        :return: Словарь с результатом операции и HTTP-статус.
        """
        data: dict = request.get_json()
        response, status = change_profile_password(data)
        return response, status

    @resident_required
    @resident_ns.doc(description="Удаление аккаунта резидента")
    def delete(self) -> tuple[dict, int]:
        """
        Удаление аккаунта текущего резидента.

        :return: Словарь с результатом операции и HTTP-статус.
        """
        response, status = delete_profile()
        return response, status
