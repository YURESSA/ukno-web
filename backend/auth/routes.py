from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields

from backend.auth import auth_ns
from backend.core import api
from .services import create_user, authenticate_user

user_model = api.model('User', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'email': fields.String(required=True, description='Электронная почта пользователя'),
    'password': fields.String(required=True, description='Пароль пользователя')
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'password': fields.String(required=True, description='Пароль пользователя')
})


@auth_ns.route('/register')
class Register(Resource):
    @api.expect(user_model)
    @api.doc(description="Регистрация нового пользователя")
    def post(self):
        data = request.json
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        new_user = create_user(username, email, password)

        if not new_user:
            return {"message": "User with this username or email already exists"}, HTTPStatus.CONFLICT

        return {"message": "User registered successfully"}, HTTPStatus.CREATED


@auth_ns.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.doc(description="Аутентификация пользователя для получения токена доступа")
    def post(self):
        data = request.json
        username = data.get("username")
        password = data.get("password")

        access_token = authenticate_user(username, password)

        if access_token:
            return {"access_token": access_token}, HTTPStatus.OK

        return {"message": "Invalid credentials"}, HTTPStatus.UNAUTHORIZED


@auth_ns.route('/protected')
class Protected(Resource):
    @jwt_required()
    @api.doc(description="Доступ к защищенному ресурсу. Требуется авторизация.")
    def get(self):
        return {"message": "This is a protected resource"}, HTTPStatus.OK
