from http import HTTPStatus

from flask import request
from flask_restx import Resource

from backend.core.schemas.auth_schemas import login_model
from backend.core.services.user_services.user_service import get_user_by_email, authenticate_user
from backend.api.login import login_ns


@login_ns.route('/login')
class UniversalLogin(Resource):
    @login_ns.expect(login_model)
    @login_ns.doc(description="Аутентификация пользователя (роль определяется автоматически)")
    def post(self):
        """
        Вход пользователя и получение JWT токена. Роль определяется автоматически по базе.
        """
        data = request.get_json() or {}
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not email or not password:
            return {"message": "Необходимо указать email и пароль"}, HTTPStatus.BAD_REQUEST

        user = get_user_by_email(email)
        if not user:
            return {"message": f"Пользователь с email {email} не найден"}, HTTPStatus.UNAUTHORIZED

        if not user.check_password(password):
            return {"message": "Неверный пароль"}, HTTPStatus.UNAUTHORIZED

        role = user.role.role_name.lower()

        token = authenticate_user(email, password)
        if not token:
            return {"message": "Ошибка при генерации токена"}, HTTPStatus.INTERNAL_SERVER_ERROR

        return {
            "access_token": token,
            "role": role,
            "message": f"Добро пожаловать, {user.full_name or 'пользователь'}!"
        }, HTTPStatus.OK
