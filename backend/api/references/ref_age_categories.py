from http import HTTPStatus
from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core.services.ref_service.age_category_service import get_all_age_categories, get_age_category_by_name, \
    create_age_category, get_age_category_by_id, delete_age_category

age_category_model = ref_ns.model('AgeCategory', {
    'name': fields.String(required=True, description='Название возрастной категории'),
})


@ref_ns.route('/age-categories')
class AgeCategoryList(Resource):
    @ref_ns.doc(description="Список всех возрастных категорий экскурсий")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех возрастных категорий экскурсий.

        Returns:
            list[dict]: Список возрастных категорий в виде словарей.
        """
        age_categories = get_all_age_categories()
        return [a.to_dict() for a in age_categories], HTTPStatus.OK

    @admin_required
    @ref_ns.expect(age_category_model)
    @ref_ns.doc(description="Создание новой возрастной категории")
    def post(self) -> tuple[dict, int]:
        """
        Создание новой возрастной категории экскурсий.

        JSON body:
            name (str): Название возрастной категории (обязательно).

        Returns:
            dict: Информация о созданной категории или сообщение об ошибке.
            int: HTTP статус код.
        """
        data = request.json or {}
        name = data.get('name')
        if not name:
            return {'message': 'Поле name обязательно'}, HTTPStatus.BAD_REQUEST

        if get_age_category_by_name(name):
            return {'message': 'Возрастная категория с таким именем уже существует'}, HTTPStatus.BAD_REQUEST

        age_category = create_age_category(name)
        return age_category.to_dict(), HTTPStatus.CREATED


@ref_ns.route('/age-categories/<int:id>')
class AgeCategoryResource(Resource):
    @admin_required
    @ref_ns.doc(description="Удаление возрастной категории по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление возрастной категории по ID.

        Args:
            id (int): ID возрастной категории для удаления.

        Returns:
            dict: Сообщение об успешном удалении или ошибке.
            int: HTTP статус код.
        """
        age_category = get_age_category_by_id(id)
        if not age_category:
            return {'message': 'Возрастная категория не найдена'}, HTTPStatus.NOT_FOUND

        delete_age_category(age_category)
        return {'message': 'Возрастная категория удалена'}, HTTPStatus.OK
