from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core.services.ref_service.category_service import get_all_categories, get_category_by_name, \
    create_category, delete_category, get_category_by_id

category_model = ref_ns.model('Category', {
    'name': fields.String(required=True, description='Название категории'),
})


@ref_ns.route('/categories')
class CategoryList(Resource):
    @ref_ns.doc(description="Список всех категорий экскурсий")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех категорий экскурсий.

        Returns:
            list[dict]: Список категорий в виде словарей.
        """
        categories = get_all_categories()
        return [c.to_dict() for c in categories], 200

    @admin_required
    @ref_ns.expect(category_model)
    @ref_ns.doc(description="Создание новой категории")
    def post(self) -> tuple[dict, int]:
        """
        Создание новой категории экскурсий.

        JSON body:
            name (str): Название категории (обязательно).

        Returns:
            dict: Информация о созданной категории или сообщение об ошибке.
            int: HTTP статус код.
        """
        data = request.json or {}
        name = data.get('name')
        if not name:
            return {'message': 'Поле name обязательно'}, 400

        if get_category_by_name(name):
            return {'message': 'Категория с таким именем уже существует'}, 400

        category = create_category(name)
        return category.to_dict(), 201


@ref_ns.route('/categories/<int:id>')
class CategoryResource(Resource):
    @admin_required
    @ref_ns.doc(description="Удаление категории по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление категории по ID.

        Args:
            id (int): ID категории для удаления.

        Returns:
            dict: Сообщение об успешном удалении или ошибке.
            int: HTTP статус код.
        """
        category = get_category_by_id(id)
        if not category:
            return {'message': 'Категория не найдена'}, 404

        delete_category(category)
        return {'message': 'Категория удалена'}, 200
