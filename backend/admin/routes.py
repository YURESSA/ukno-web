from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx import Resource

from backend.core.services.profile_service import *
from . import admin_ns
from ..core.messages import AuthMessages
from ..core.schemas.auth_schemas import login_model, change_password_model, user_model


def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return False
    return True


@admin_ns.route('/login')
class AdminLogin(Resource):
    @admin_ns.expect(login_model)
    @admin_ns.doc(description="Аутентификация администратора для получения токена доступа")
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        user = get_user_by_username(username)
        if not user or not user.check_password(password) or user.role.role_name != "admin":
            return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED

        access_token = authenticate_user(username, password)
        if access_token:
            return {"access_token": access_token}, HTTPStatus.OK
        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@admin_ns.route('/profile')
class AdminProfile(Resource):
    @jwt_required()
    @admin_ns.doc(description="Получение информации о пользователе (только для администратора)")
    def get(self):
        if not admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        current_username = get_jwt_identity()
        user = get_user_by_username(current_username)
        return get_user_info_response(user)

    @jwt_required()
    @admin_ns.expect(change_password_model)
    @admin_ns.doc(description="Изменение пароля администратора")
    def put(self):
        if not admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        current_username = get_jwt_identity()
        data = request.get_json()
        if change_password(current_username, data.get("old_password"), data.get("new_password")):
            return {"message": AuthMessages.PASSWORD_CHANGED}, HTTPStatus.OK
        return {"message": AuthMessages.PASSWORD_INVALID_OLD}, HTTPStatus.BAD_REQUEST


@admin_ns.route('/users')
class AdminUserList(Resource):
    @jwt_required()
    @admin_ns.doc(
        description="Получение списка всех пользователей с возможностью фильтрации по роли (только для администратора)")
    @admin_ns.param('role', 'Фильтрация пользователей по роли')
    def get(self):
        if not admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        role_filter = request.args.get('role')
        users = get_all_users(role_filter)

        user_list = [get_user_info_response(u)[0] for u in users]

        return user_list, HTTPStatus.OK

    @jwt_required()
    @admin_ns.expect(user_model)
    @admin_ns.doc(description="Создание нового пользователя (или резидента) от лица администратора")
    def post(self):
        if not admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        current_role = get_jwt().get('role')
        data = request.get_json()
        return register_user("user", data, current_role)


@admin_ns.route('/users/detail/<string:username>')
class AdminUserDetail(Resource):
    @jwt_required()
    @admin_ns.doc(description="Получение информации о пользователе по username (только для администратора)")
    def get(self, username):
        if not admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        user = get_user_by_username(username)
        if user:
            return get_user_info_response(user)
        return {
            "message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

    @jwt_required()
    @admin_ns.doc(description="Удаление пользователя по username (только для администратора)")
    def delete(self, username):
        if not admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        if delete_user(username):
            return {"message": AuthMessages.USER_DELETED}, HTTPStatus.OK
        return {
            "message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND
