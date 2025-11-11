from typing import Optional, Tuple, Dict


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
