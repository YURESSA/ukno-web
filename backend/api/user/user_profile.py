from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields

from backend.core.schemas.auth_schemas import change_password_model, edit_profile_model
from . import user_ns
from backend.core import db
from backend.core.services.email_service.email_service import send_reset_email

from backend.core.services.user_services.auth_service import change_profile_password
from ...core.services.user_services.user_service import get_user_by_email, update_profile
from backend.core.services.user_services.profile_service import get_profile, \
    get_user_info_response, delete_profile
from ...core.utilits.token_utils import verify_reset_token


@user_ns.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    @user_ns.doc(description="Получение информации о текущем пользователе")
    def get(self) -> tuple[dict, int]:
        """
        Получение профиля текущего пользователя.

        :return: Возвращает словарь с данными пользователя и HTTP-статус.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user)

    @jwt_required()
    @user_ns.expect(edit_profile_model)
    @user_ns.doc(description="Редактирование профиля текущего пользователя")
    def put(self) -> tuple[dict, int]:
        """
        Редактирование профиля текущего пользователя.

        :return: Возвращает обновлённые данные пользователя и HTTP-статус.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        data = request.get_json()
        response, status = update_profile(data)
        return response, status

    @jwt_required()
    @user_ns.doc(description="Удаление аккаунта текущего пользователя")
    def delete(self) -> tuple[dict, int]:
        """
        Удаление аккаунта текущего пользователя.

        :return: Возвращает сообщение об успешном удалении и HTTP-статус.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        response, status = delete_profile()
        return response, status


@user_ns.route('/profile/password')
class ChangePassword(Resource):
    @jwt_required()
    @user_ns.expect(change_password_model)
    @user_ns.doc(description="Смена пароля текущего пользователя")
    def put(self) -> tuple[dict, int]:
        """
        Смена пароля текущего пользователя.

        :return: Возвращает сообщение об успешной смене пароля и HTTP-статус.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        data = request.get_json()
        response, status = change_profile_password(data)
        return response, status


@user_ns.route('/password-reset-request')
class PasswordResetRequest(Resource):
    password_reset_request_model = user_ns.model(
        "PasswordResetRequest",
        {
            "email": fields.String(required=True, description="Email пользователя")
        }
    )

    @user_ns.expect(password_reset_request_model, validate=True)
    @user_ns.doc(description="Запрос на сброс пароля: отправка инструкции на email")
    def post(self) -> tuple[dict, int]:
        """
        Обрабатывает запрос на сброс пароля.

        Всегда возвращает успешный ответ, чтобы не раскрывать существование пользователя.

        :return: Словарь с сообщением об отправке инструкции и HTTP-статус.
        """
        data: dict = request.get_json() or {}
        email: str | None = data.get("email")

        user = get_user_by_email(email)
        if user:
            send_reset_email(user)

        return {
            "message": "Если пользователь существует, инструкция отправлена на почту"
        }, HTTPStatus.OK


@user_ns.route('/password-reset')
class PasswordReset(Resource):
    password_reset_model = user_ns.model(
        "PasswordReset",
        {
            "token": fields.String(required=True, description="Токен из email"),
            "new_password": fields.String(required=True, description="Новый пароль")
        }
    )

    @user_ns.expect(password_reset_model, validate=True)
    @user_ns.doc(description="Сброс пароля по токену, без авторизации JWT")
    def post(self) -> tuple[dict, int]:
        """
        Сбрасывает пароль пользователя по токену.

        :return: В случае успешного сброса — сообщение об успешной операции и HTTPStatus.OK.
                 Если токен недействителен — сообщение об ошибке и HTTPStatus.BAD_REQUEST.
                 Если пользователь не найден — сообщение об ошибке и HTTPStatus.NOT_FOUND.
        """
        data: dict = request.get_json() or {}
        token: str | None = data.get("token")
        new_password: str | None = data.get("new_password")

        email: str | None = verify_reset_token(token)
        if not email:
            return {"message": "Неверный или просроченный токен"}, HTTPStatus.BAD_REQUEST

        user = get_user_by_email(email)
        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

        user.set_password(new_password)
        db.session.commit()

        return {"message": "Пароль успешно сброшен"}, HTTPStatus.OK
