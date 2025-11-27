from http import HTTPStatus
from typing import Dict, Tuple, Optional

from flask_jwt_extended import get_jwt_identity

from backend.core.messages import AuthMessages
from backend.core.models.auth_models import User
from backend.core.services.user_services.user_service import get_user_by_email, delete_user


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
