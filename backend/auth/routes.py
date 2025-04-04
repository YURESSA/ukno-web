from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_restx import Resource, fields

from backend.auth import auth_ns
from backend.core import api
from backend.models.models import User
from .services import create_user, authenticate_user, change_password, delete_user
from ..core.messages import AuthMessages

user_model = api.model('User', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'email': fields.String(required=True, description='Электронная почта пользователя'),
    'password': fields.String(required=True, description='Пароль пользователя'),
    'full_name': fields.String(required=True, description='Полное имя пользователя'),
    'phone': fields.String(required=True, description='Телефон пользователя'),
    'role_name': fields.String(required=False, description='Роль пользователя', default="Пользователь")
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'password': fields.String(required=True, description='Пароль пользователя')
})

change_password_model = api.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Старый пароль'),
    'new_password': fields.String(required=True, description='Новый пароль')
})


def parse_user_data(data):
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    phone = data.get("phone")
    role_name = data.get("role_name", "Пользователь")
    return username, email, password, full_name, phone, role_name


@auth_ns.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.doc(description="Аутентификация пользователя для получения токена доступа")
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        access_token = authenticate_user(username, password)
        if access_token:
            return {"access_token": access_token}, HTTPStatus.OK

        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@auth_ns.route('/users')
class Users(Resource):
    @api.doc(description="Получить список всех пользователей (только для администратора)")
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if claims.get("role") != "Администратор":
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        users = User.query.all()
        return [
            {
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "role": user.role.role_name
            }
            for user in users
        ], HTTPStatus.OK

    @api.expect(user_model)
    @api.doc(description="Регистрация нового пользователя. Если роль отличается от 'Пользователь', "
                         "создание может выполнить только администратор.")
    @jwt_required(optional=True)
    def post(self):
        data = request.get_json()
        username, email, password, full_name, phone, role_name = parse_user_data(data)

        if role_name != "Пользователь":
            claims = get_jwt()
            if not claims or claims.get("role") != "Администратор":
                return {"message": AuthMessages.ROLE_CHANGE_FORBIDDEN}, HTTPStatus.FORBIDDEN

        new_user = create_user(username, email, password, full_name, phone, role_name)
        if not new_user:
            return {"message": AuthMessages.USER_ALREADY_EXISTS}, HTTPStatus.CONFLICT

        return {"message": AuthMessages.USER_CREATED}, HTTPStatus.CREATED


@auth_ns.route('/users/<string:username>')
class UserDetails(Resource):
    @api.doc(description="Получить информацию о пользователе")
    @jwt_required()
    def get(self, username):
        current_username = get_jwt_identity()
        if current_username != username:
            claims = get_jwt()
            if claims.get("role") != "Администратор":
                return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        user = User.query.filter_by(username=username).first()
        if not user:
            return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

        return {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role.role_name
        }, HTTPStatus.OK

    @api.expect(change_password_model)
    @api.doc(description="Изменить пароль пользователя (можно изменить только свой пароль)")
    @jwt_required()
    def put(self, username):
        current_username = get_jwt_identity()
        if username != current_username:
            return {"message": AuthMessages.PASSWORD_CHANGE_FORBIDDEN}, HTTPStatus.FORBIDDEN

        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if change_password(username, old_password, new_password):
            return {"message": AuthMessages.PASSWORD_CHANGED}, HTTPStatus.OK
        return {"message": AuthMessages.PASSWORD_INVALID_OLD}, HTTPStatus.BAD_REQUEST

    @api.doc(description="Удалить пользователя (только для администратора или для самого себя)")
    @jwt_required()
    def delete(self, username):
        current_username = get_jwt_identity()
        claims = get_jwt()

        if current_username == username:
            if delete_user(username):
                return {"message": AuthMessages.USER_DELETED_SELF}, HTTPStatus.OK
            return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

        if claims.get("role") != "Администратор":
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        if delete_user(username):
            return {"message": AuthMessages.USER_DELETED}, HTTPStatus.OK
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND


@auth_ns.route('/protected')
class Protected(Resource):
    @jwt_required()
    @api.doc(description="Доступ к защищенному ресурсу. Требуется авторизация.")
    def get(self):
        return {"message": AuthMessages.PROTECTED_RESOURCE}, HTTPStatus.OK
