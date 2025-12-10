from typing import Optional, Tuple, Dict

from backend.core.models.auth_models import RoleEnum


def parse_user_data(
        data: Dict,
        default_role: RoleEnum
) -> Tuple[
    Optional[str],
    Optional[str],
    Optional[str],
    Optional[str],
    RoleEnum
]:
    """
    Извлекает данные пользователя из словаря и подставляет роль по умолчанию, если не указана.

    :param data: Словарь с данными пользователя
    :param default_role: Роль по умолчанию (RoleEnum)
    :return: Кортеж (email, password, full_name, phone, role_enum)
    """
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    phone = data.get("phone")

    # Получаем роль из данных или ставим default
    role_name = data.get("role_name")
    if role_name:
        try:
            role_enum = RoleEnum(role_name.lower())
        except ValueError:
            role_enum = default_role  # fallback на default, если передано некорректно
    else:
        role_enum = default_role

    return email, password, full_name, phone, role_enum
