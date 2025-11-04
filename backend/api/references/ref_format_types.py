from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.core import db
from backend.core.models.event_models import FormatType
from backend.api.references import ref_ns

format_type_model = ref_ns.model('FormatType', {
    'name': fields.String(required=True, description='Название типа формата'),
})


@ref_ns.route('/format-types')
class FormatTypeList(Resource):
    @ref_ns.doc(description="Список всех типов форматов экскурсий")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех типов форматов экскурсий.

        Returns:
            list[dict]: Список типов форматов в виде словарей.
        """
        format_types = FormatType.query.all()
        return [f.to_dict() for f in format_types], 200

    @admin_required
    @ref_ns.expect(format_type_model)
    @ref_ns.doc(description="Создание нового типа формата")
    def post(self) -> tuple[dict, int]:
        """
        Создание нового типа формата экскурсий.

        JSON body:
            name (str): Название типа формата (обязательно).

        Returns:
            dict: Информация о созданном типе формата или сообщение об ошибке.
            int: HTTP статус код.
        """
        data = request.json or {}
        name = data.get('name')
        if not name:
            return {'message': 'Поле name обязательно'}, 400

        if FormatType.query.filter_by(format_type_name=name).first():
            return {'message': 'Тип формата с таким именем уже существует'}, 400

        format_type = FormatType(format_type_name=name)
        db.session.add(format_type)
        db.session.commit()
        return format_type.to_dict(), 201


@ref_ns.route('/format-types/<int:id>')
class FormatTypeResource(Resource):
    @admin_required
    @ref_ns.doc(description="Удаление типа формата по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление типа формата по ID.

        Args:
            id (int): ID типа формата для удаления.

        Returns:
            dict: Сообщение об успешном удалении или ошибке.
            int: HTTP статус код.
        """
        format_type = FormatType.query.get(id)
        if not format_type:
            return {'message': 'Тип формата не найден'}, 404

        db.session.delete(format_type)
        db.session.commit()
        return {'message': 'Тип формата удалён'}, 200
