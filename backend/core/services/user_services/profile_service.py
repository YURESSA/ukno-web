from http import HTTPStatus
from typing import Dict, Tuple, Optional

from flask_jwt_extended import get_jwt_identity

from backend.core import db
from backend.core.messages import AuthMessages
from backend.core.models.auth_models import User, Role
from backend.core.services.user_services.auth_service import create_user, authenticate_user, change_password, \
    delete_user, get_user_by_email


def parse_user_data(data: Dict, default_role: str) \
        -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], str]:
    """
    Извлекает данные пользователя из словаря и подставляет роль по умолчанию, если не указана.

    :param data: Словарь с данными пользователя
    :param default_role: Значение роли по умолчанию
    :return: Кортеж из (email, password, full_name, phone, role_name)
    """
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    phone = data.get("phone")
    role_name = data.get("role_name", default_role)
    return email, password, full_name, phone, role_name


def register_user(default_role: str, data: Dict, current_user_role: str = "user") -> Tuple[Dict, int]:
    """
    Регистрирует нового пользователя с указанной ролью.
    Если текущий пользователь не админ, роль игнорируется и используется default_role.

    :param default_role: Роль по умолчанию для нового пользователя
    :param data: Словарь с данными пользователя (email, password, full_name, phone, role_name)
    :param current_user_role: Роль текущего пользователя, совершающего регистрацию
    :return: Кортеж из словаря с сообщением и HTTP-статуса
    """
    email, password, full_name, phone, role_name = parse_user_data(data, default_role)

    if current_user_role != "admin":
        role_name = default_role

    new_user = create_user(email, password, full_name, phone, role_name)
    if not new_user:
        return {"message": AuthMessages.USER_ALREADY_EXISTS}, HTTPStatus.CONFLICT
    return {"message": AuthMessages.USER_CREATED}, HTTPStatus.CREATED


def login_user(role: str, data: dict) -> Tuple[Dict, int]:
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

    if user.role.role_name.lower() != role.lower():
        return {"message": "Доступ запрещён для этой роли"}, HTTPStatus.FORBIDDEN

    token = authenticate_user(email, password)
    if not token:
        return {"message": "Ошибка при генерации токена"}, HTTPStatus.INTERNAL_SERVER_ERROR

    return {
        "access_token": token,
        "role": role,
        "message": f"Добро пожаловать, {user.full_name or 'пользователь'}!"
    }, HTTPStatus.OK


def get_profile() -> Tuple[Optional['User'], Optional[Dict], Optional[int]]:
    """
    Получение текущего пользователя (резидента) по JWT-токену.

    :return: Кортеж (user, error, status)
             - user: объект User, если найден, иначе None
             - error: словарь с сообщением об ошибке, если пользователь не найден, иначе None
             - status: HTTP-статус, если есть ошибка, иначе None
    """
    current_email = get_jwt_identity()
    user = get_user_by_email(current_email)
    if not user:
        return None, {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND
    return user, None, None


def change_profile_password(data: dict) -> Tuple[Dict, int]:
    """
    Изменение пароля текущего пользователя.

    :param data: словарь с ключами "old_password" и "new_password"
    :return: Кортеж (response_dict, http_status)
    """
    current_email = get_jwt_identity()
    if change_password(current_email, data.get("old_password"), data.get("new_password")):
        return {"message": AuthMessages.PASSWORD_CHANGED}, HTTPStatus.OK
    return {"message": AuthMessages.PASSWORD_INVALID_OLD}, HTTPStatus.BAD_REQUEST


def delete_profile() -> Tuple[Dict, int]:
    """
    Удаление аккаунта текущего пользователя.

    :return: Кортеж (response_dict, http_status)
    """
    current_email = get_jwt_identity()
    if delete_user(current_email):
        return {"message": AuthMessages.USER_DELETED_SELF}, HTTPStatus.OK
    return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND


def get_user_info_response(user: Optional['User']) -> Tuple[Dict, int]:
    """
    Формирование словаря с данными пользователя для ответа API.

    :param user: объект User или None
    :return: Кортеж (response_dict, http_status)
    """
    if not user:
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND
    return {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role.role_name
    }, HTTPStatus.OK


def update_user(email: str, data: dict) -> Optional['User']:
    """
    Обновление данных пользователя.

    :param email: текущий email пользователя для поиска
    :param data: словарь с полями для обновления. Возможные ключи:
                 - email
                 - full_name
                 - phone
                 - password
                 - role_name
    :return: объект User после обновления, либо None, если пользователь не найден
    :raises ValueError: если новый email уже используется или роль не найдена
    """
    user = get_user_by_email(email)
    if not user:
        return None

    if 'email' in data and data['email'] != user.email:
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            raise ValueError("Email уже используется другим пользователем")
        user.email = data['email']

    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    if 'role_name' in data:
        role_name = data['role_name']
        role = Role.query.filter_by(role_name=role_name).first()
        if not role:
            raise ValueError(f"Роль '{role_name}' не найдена")
        user.role_id = role.role_id

    db.session.commit()
    return user
