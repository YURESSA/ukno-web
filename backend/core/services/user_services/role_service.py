from typing import Optional

from backend.core.models.auth_models import Role


def get_role_by_name(role_name: str) -> Optional[Role]:
    """
    Получение роли по имени.

    :param role_name: Название роли
    :return: Объект Role или None, если роль не найдена
    """
    return Role.query.filter_by(role_name=role_name).first()
