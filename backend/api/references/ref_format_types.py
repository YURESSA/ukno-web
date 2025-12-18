from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core.models.event_models import FormatType
from backend.core.services.ref_service.format_type_service import get_all_format_types, create_format_type, \
    delete_format_type

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
        items = get_all_format_types()
        return [f.to_dict() for f in items], 200

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
        try:
            format_type = create_format_type(data.get('name'))
        except ValueError as e:
            return {'message': str(e)}, 400

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

        delete_format_type(format_type)
        return {'message': 'Тип формата удалён'}, 200
