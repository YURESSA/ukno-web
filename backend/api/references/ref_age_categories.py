from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.core import db
from backend.core.models.event_models import AgeCategory
from backend.api.references import ref_ns

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
        age_categories = AgeCategory.query.all()
        return [a.to_dict() for a in age_categories], 200

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
            return {'message': 'Поле name обязательно'}, 400

        if AgeCategory.query.filter_by(age_category_name=name).first():
            return {'message': 'Возрастная категория с таким именем уже существует'}, 400

        age_category = AgeCategory(age_category_name=name)
        db.session.add(age_category)
        db.session.commit()
        return age_category.to_dict(), 201


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
        age_category = AgeCategory.query.get(id)
        if not age_category:
            return {'message': 'Возрастная категория не найдена'}, 404

        db.session.delete(age_category)
        db.session.commit()
        return {'message': 'Возрастная категория удалена'}, 200
