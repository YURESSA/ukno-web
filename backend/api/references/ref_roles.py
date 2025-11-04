from typing import Any

from flask import request
from flask_restx import Resource

from backend.api.admin.decorators import admin_required
from backend.core import db
from backend.core.models.auth_models import Role
from backend.core.schemas.event_schemas import role_model
from backend.api.references import ref_ns


@ref_ns.route('/roles')
class RoleList(Resource):
    @ref_ns.doc(description="Список всех ролей")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех ролей пользователей.

        Returns:
            list[dict]: Список ролей в виде словарей.
        """
        roles = Role.query.all()
        return [r.to_dict() for r in roles], 200

    @admin_required
    @ref_ns.expect(role_model)
    @ref_ns.doc(description="Создание новой роли")
    def post(self) -> tuple[dict, int]:
        """
        Создание новой роли пользователя.

        JSON body:
            name (str): Название роли (обязательно).

        Returns:
            dict: Информация о созданной роли или сообщение об ошибке.
            int: HTTP статус код.
        """
        data = request.json or {}
        name = data.get('name')
        if not name:
            return {'message': 'Поле name обязательно'}, 400

        if Role.query.filter_by(role_name=name).first():
            return {'message': 'Роль с таким именем уже существует'}, 400

        role = Role(role_name=name)
        db.session.add(role)
        db.session.commit()
        return role.to_dict(), 201


@ref_ns.route('/roles/<int:id>')
class RoleResource(Resource):
    @admin_required
    @ref_ns.doc(description="Удаление роли по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление роли пользователя по ID.

        Args:
            id (int): ID роли для удаления.

        Returns:
            dict: Сообщение об успешном удалении или ошибке.
            int: HTTP статус код.
        """
        role = Role.query.get(id)
        if not role:
            return {'message': 'Роль не найдена'}, 404

        db.session.delete(role)
        db.session.commit()
        return {'message': 'Роль удалена'}, 200
