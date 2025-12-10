from typing import Any

from flask_restx import Resource

from backend.api.references import ref_ns
from backend.core.models.auth_models import RoleEnum


@ref_ns.route('/roles')
class RoleList(Resource):
    @ref_ns.doc(description="Список всех ролей")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех ролей пользователей.

        Returns:
            list[dict]: Список ролей в виде словарей.
        """
        roles = [role.to_dict() for role in RoleEnum]
        return roles, 200
