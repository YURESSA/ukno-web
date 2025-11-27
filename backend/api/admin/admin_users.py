from http import HTTPStatus
from typing import Dict, Any, List, Tuple

from flask import request
from flask_jwt_extended import get_jwt
from flask_restx import Resource

from backend.core.services.user_services.profile_service import get_user_info_response
from ...core.services.user_services.auth_service import register_user
from . import admin_ns
from .decorators import admin_required
from backend.core.messages import AuthMessages
from backend.core.schemas.admin_schemas import update_user_model
from backend.core.schemas.auth_schemas import user_model
from ...core.services.user_services.user_service import get_user_by_email, get_all_users, delete_user, update_user


@admin_ns.route('/users')
class AdminUserList(Resource):

    @admin_required
    def get(self) -> Tuple[List[Dict[str, Any]], int]:
        """
        Получение списка всех пользователей с возможностью фильтрации по роли (только для администратора)
        """
        role_filter: str | None = request.args.get('role')
        users: list = get_all_users(role_filter)
        user_list: List[Dict[str, Any]] = [get_user_info_response(u)[0] for u in users]
        return user_list, HTTPStatus.OK

    @admin_required
    @admin_ns.expect(user_model)
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Создание нового пользователя (или резидента) от лица администратора
        """
        current_role: str = get_jwt().get('role', '')
        data: Dict[str, Any] = request.get_json() or {}
        response, status = register_user("user", data, current_role)
        return response, status


@admin_ns.route('/users/detail/<string:email>')
class AdminUserDetail(Resource):
    @admin_required
    @admin_ns.doc(description="Получение информации о пользователе по email (только для администратора)")
    def get(self, email: str) -> Tuple[dict, int]:
        """
        Получение информации о пользователе по email
        """
        user = get_user_by_email(email)
        if user:
            return get_user_info_response(user)
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

    @admin_required
    @admin_ns.doc(description="Удаление пользователя по email (только для администратора)")
    def delete(self, email: str) -> Tuple[dict, int]:
        """
        Удаление пользователя по email
        """
        if delete_user(email):
            return {"message": AuthMessages.USER_DELETED}, HTTPStatus.OK
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

    @admin_required
    @admin_ns.doc(description="Редактирование пользователя по email (только для администратора)")
    @admin_ns.expect(update_user_model)
    def put(self, email: str) -> tuple[dict, int]:
        """
        Редактирование полей пользователя:
        - full_name
        - email
        - phone
        - password
        - role_name
        """
        data: dict = request.get_json() or {}
        if not data:
            return {"message": "Пустой JSON"}, HTTPStatus.BAD_REQUEST

        user = get_user_by_email(email)
        if not user:
            return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

        try:
            updated_user = update_user(email, data)
        except ValueError as e:
            return {"message": str(e)}, HTTPStatus.BAD_REQUEST

        return get_user_info_response(updated_user), HTTPStatus.OK
