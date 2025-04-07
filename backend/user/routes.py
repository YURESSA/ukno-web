from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from backend.core.services.common_endpoints import *
from backend.core.messages import AuthMessages
from backend.core.schemas.auth_schemas import login_model, user_model, change_password_model
from . import user_ns


@user_ns.route('/register')
class UserRegister(Resource):
    @user_ns.expect(user_model)
    @user_ns.doc(description="Регистрация обычного пользователя (роль автоматически 'user')")
    def post(self):
        data = request.get_json()
        return register_user("user", data)


@user_ns.route('/login')
class UserLogin(Resource):
    @user_ns.expect(login_model)
    @user_ns.doc(description="Аутентификация обычного пользователя для получения токена доступа")
    def post(self):
        data = request.get_json()
        token = login_user("user", data)
        if token:
            return {"access_token": token}, HTTPStatus.OK
        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@user_ns.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    @user_ns.doc(description="Получение информации о пользователе")
    def get(self):
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user)

    @jwt_required()
    @user_ns.expect(change_password_model)
    @user_ns.doc(description="Изменение пароля")
    def put(self):
        data = request.get_json()
        return change_profile_password(data)

    @jwt_required()
    @user_ns.doc(description="Удаление аккаунта")
    def delete(self):
        return delete_profile()
