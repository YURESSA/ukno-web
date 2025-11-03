from typing import Any

from flask import request
from flask_restx import Resource, fields
from sqlalchemy import func

from backend.admin.decorators import admin_required
from backend.core import db
from backend.core.models.auth_models import Role
from backend.core.models.event_models import FormatType, Category, AgeCategory, Event, EventSession
from backend.core.schemas.event_schemas import role_model
from backend.references import ref_ns

category_model = ref_ns.model('Category', {
    'name': fields.String(required=True, description='Название категории'),
})

format_type_model = ref_ns.model('FormatType', {
    'name': fields.String(required=True, description='Название типа формата'),
})

age_category_model = ref_ns.model('AgeCategory', {
    'name': fields.String(required=True, description='Название возрастной категории'),
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
        categories = Category.query.all()
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

        # Проверка на дубли
        if Category.query.filter_by(category_name=name).first():
            return {'message': 'Категория с таким именем уже существует'}, 400

        category = Category(category_name=name)
        db.session.add(category)
        db.session.commit()
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
        category = Category.query.get(id)
        if not category:
            return {'message': 'Категория не найдена'}, 404

        db.session.delete(category)
        db.session.commit()
        return {'message': 'Категория удалена'}, 200


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


@ref_ns.route('/roles')
class RoleList(Resource):
    @ref_ns.doc(description="Список всех ролей")
    def get(self) -> list[dict]:
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


@ref_ns.route('/excursion-stats')
class ExcursionStats(Resource):
    @ref_ns.doc(description="Получить статистику экскурсий: стоимость, время, расстояние, роли, возрастные категории,"
                            " форматы и категории")
    def get(self) -> tuple[dict, int]:
        """
        Получение сводной статистики для фильтров на фронтенде.

        Returns:
            dict: Статистика по экскурсиям и справочникам:
                - cost: минимальная и максимальная стоимость сессий
                - distance_to_center: минимальное и максимальное расстояние до центра
                - time_to_stop: минимальное и максимальное время до ближайшей остановки
                - roles: список ролей пользователей
                - age_categories: список возрастных категорий
                - format_types: список типов форматов экскурсий
                - categories: список категорий экскурсий
            int: HTTP статус код (200)
        """
        # Статистика по стоимости сессий
        min_cost, max_cost = db.session.query(
            func.min(EventSession.cost),
            func.max(EventSession.cost)
        ).first()

        # Статистика по расстоянию до центра
        min_center, max_center = db.session.query(
            func.min(Event.distance_to_center),
            func.max(Event.distance_to_center)
        ).filter(Event.is_active.is_(True)).first()

        # Статистика по времени до ближайшей остановки
        min_time, max_time = db.session.query(
            func.min(Event.time_to_nearest_stop),
            func.max(Event.time_to_nearest_stop)
        ).filter(Event.is_active.is_(True)).first()

        roles_data = [r.to_dict() for r in Role.query.all()]

        age_categories_data = [a.to_dict() for a in AgeCategory.query.all()]

        format_types_data = [f.to_dict() for f in FormatType.query.all()]

        categories_data = [c.to_dict() for c in Category.query.all()]

        return {
            "cost": {
                "min": float(min_cost) if min_cost is not None else None,
                "max": float(max_cost) if max_cost is not None else None
            },
            "distance_to_center": {
                "min": round(min_center, 2) if min_center is not None else None,
                "max": round(max_center, 2) if max_center is not None else None
            },
            "time_to_stop": {
                "min": round(min_time, 2) if min_time is not None else None,
                "max": round(max_time, 2) if max_time is not None else None
            },
            "roles": roles_data,
            "age_categories": age_categories_data,
            "format_types": format_types_data,
            "categories": categories_data
        }, 200
