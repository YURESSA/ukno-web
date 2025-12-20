from http import HTTPStatus
from typing import Tuple, Dict

from flask_jwt_extended import get_jwt_identity

from backend.core import db
from backend.core.messages import AuthMessages
from backend.core.models.auth_models import User, RoleEnum
from backend.core.services.user_services.user_service import create_user, get_user_by_email, authenticate_user
from backend.core.utilits.user_utils import parse_user_data


def change_profile_password(data: dict) -> Tuple[Dict, int]:
    """
    Изменение пароля текущего пользователя.

    :param data: Словарь с полями 'old_password' и 'new_password'
    :return: Словарь с сообщением и HTTP-статус
    """
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return {"message": "Оба поля обязательны"}, HTTPStatus.BAD_REQUEST

    if not user.check_password(old_password):
        return {"message": "Неверный текущий пароль"}, HTTPStatus.UNAUTHORIZED

    user.set_password(new_password)
    db.session.commit()

    return {"message": "Пароль успешно изменён"}, HTTPStatus.OK


def register_user(default_role: RoleEnum, data: Dict, current_user_role: RoleEnum = RoleEnum.USER) -> Tuple[Dict, int]:
    """
    Регистрирует нового пользователя с указанной ролью.
    Если текущий пользователь не админ, роль игнорируется и используется default_role.
    """

    is_admin = current_user_role == RoleEnum.ADMIN
    email, password, full_name, phone, role_enum = parse_user_data(data, default_role)

    if not is_admin:
        role_enum = default_role

    new_user = create_user(email, password, full_name, phone, role_enum)
    if not new_user:
        return {"message": AuthMessages.USER_ALREADY_EXISTS}, HTTPStatus.CONFLICT
    return {"message": AuthMessages.USER_CREATED}, HTTPStatus.CREATED


def login_user(role: RoleEnum, data: dict) -> Tuple[Dict, int]:
    """
    Универсальная функция авторизации пользователя по роли.

    :param role: Роль, под которую выполняется вход (например, 'resident' или 'admin')
    :param data: Словарь с полями 'email' и 'password'
    :return: Кортеж (response_dict, http_status)
             response_dict содержит сообщение, токен и роль при успешном входе
    """
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return {"message": "Необходимо указать и email, и пароль"}, HTTPStatus.BAD_REQUEST

    user = get_user_by_email(email)
    if not user:
        return {"message": f"Пользователь с email {email} не найден"}, HTTPStatus.UNAUTHORIZED

    if not user.check_password(password):
        return {"message": "Неверный пароль"}, HTTPStatus.UNAUTHORIZED

    if user.role != role:
        return {"message": "Доступ запрещён для этой роли"}, HTTPStatus.FORBIDDEN

    token = authenticate_user(email, password)
    if not token:
        return {"message": "Ошибка при генерации токена"}, HTTPStatus.INTERNAL_SERVER_ERROR

    return {
        "access_token": token,
        "role": user.role.value,
        "message": f"Добро пожаловать, {user.full_name or 'пользователь'}!"
    }, HTTPStatus.OK
