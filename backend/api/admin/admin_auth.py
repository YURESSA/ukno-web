from http import HTTPStatus
from typing import Dict, Any, Tuple

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource

from backend.core.services.user_services.profile_service import get_user_info_response
from ...core.services.user_services.auth_service import login_user
from . import admin_ns
from .decorators import admin_required
from backend.core.messages import AuthMessages
from backend.core.schemas.admin_schemas import admin_login
from backend.core.schemas.auth_schemas import change_password_model
from ...core.services.user_services.user_service import get_user_by_email, change_password


@admin_ns.route('/login')
class AdminLogin(Resource):
    @admin_ns.expect(admin_login)
    @admin_ns.doc(description="Аутентификация администратора для получения токена доступа")
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Авторизация администратора для получения JWT токена.
        """
        data: Dict[str, Any] = request.get_json() or {}
        response, status = login_user("admin", data)
        return response, status


@admin_ns.route('/profile')
class AdminProfile(Resource):

    @admin_required
    def get(self) -> Tuple[Dict[str, Any], int]:
        """
        Получение информации о текущем администраторе.
        """
        current_email = get_jwt_identity()
        user = get_user_by_email(current_email)
        return get_user_info_response(user)

    @admin_required
    @admin_ns.expect(change_password_model)
    def put(self) -> Tuple[Dict[str, str], int]:
        """
        Изменение пароля администратора.
        """
        current_email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json() or {}

        old_password: str | None = data.get("old_password")
        new_password: str | None = data.get("new_password")

        if not old_password or not new_password:
            return {"message": "Старый и новый пароль обязательны"}, HTTPStatus.BAD_REQUEST

        if change_password(current_email, old_password, new_password):
            return {"message": AuthMessages.PASSWORD_CHANGED}, HTTPStatus.OK

        return {"message": AuthMessages.PASSWORD_INVALID_OLD}, HTTPStatus.BAD_REQUEST
