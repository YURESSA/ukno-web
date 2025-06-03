from flask import request
from flask_restx import Resource, fields
from sqlalchemy import func

from backend.core import db
from backend.core.models.auth_models import Role
from backend.core.models.excursion_models import FormatType, Category, AgeCategory, Excursion, ExcursionSession
from backend.core.schemas.excursion_schemas import role_model
from backend.references import ref_ns

# Для валидации и автодокументации сделаем модели (пример)
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
    def get(self):
        categories = Category.query.all()
        return [c.to_dict() for c in categories], 200

    @ref_ns.expect(category_model)
    @ref_ns.doc(description="Создание новой категории")
    def post(self):
        data = request.json
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
    @ref_ns.doc(description="Удаление категории по ID")
    def delete(self, id):
        category = Category.query.get(id)
        if not category:
            return {'message': 'Категория не найдена'}, 404
        db.session.delete(category)
        db.session.commit()
        return {'message': 'Категория удалена'}, 200


@ref_ns.route('/format-types')
class FormatTypeList(Resource):
    @ref_ns.doc(description="Список всех типов форматов экскурсий")
    def get(self):
        format_types = FormatType.query.all()
        return [f.to_dict() for f in format_types], 200

    @ref_ns.expect(format_type_model)
    @ref_ns.doc(description="Создание нового типа формата")
    def post(self):
        data = request.json
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
    @ref_ns.doc(description="Удаление типа формата по ID")
    def delete(self, id):
        format_type = FormatType.query.get(id)
        if not format_type:
            return {'message': 'Тип формата не найден'}, 404
        db.session.delete(format_type)
        db.session.commit()
        return {'message': 'Тип формата удалён'}, 200


@ref_ns.route('/age-categories')
class AgeCategoryList(Resource):
    @ref_ns.doc(description="Список всех возрастных категорий экскурсий")
    def get(self):
        age_categories = AgeCategory.query.all()
        return [a.to_dict() for a in age_categories], 200

    @ref_ns.expect(age_category_model)
    @ref_ns.doc(description="Создание новой возрастной категории")
    def post(self):
        data = request.json
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
    @ref_ns.doc(description="Удаление возрастной категории по ID")
    def delete(self, id):
        age_category = AgeCategory.query.get(id)
        if not age_category:
            return {'message': 'Возрастная категория не найдена'}, 404
        db.session.delete(age_category)
        db.session.commit()
        return {'message': 'Возрастная категория удалена'}, 200




@ref_ns.route('/roles')
class RoleList(Resource):
    @ref_ns.doc(description="Список всех ролей")
    def get(self):
        roles = Role.query.all()
        return [r.to_dict() for r in roles], 200

    @ref_ns.expect(role_model)
    @ref_ns.doc(description="Создание новой роли")
    def post(self):
        data = request.json
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
    @ref_ns.doc(description="Удаление роли по ID")
    def delete(self, id):
        role = Role.query.get(id)
        if not role:
            return {'message': 'Роль не найдена'}, 404
        db.session.delete(role)
        db.session.commit()
        return {'message': 'Роль удалена'}, 200




@ref_ns.route('/excursion-stats')
class ExcursionStats(Resource):
    @ref_ns.doc(description="Получить минимальные и максимальные значения по цене, расстоянию до центра и остановки")
    def get(self):
        # Стоимость
        min_cost, max_cost = db.session.query(
            func.min(ExcursionSession.cost),
            func.max(ExcursionSession.cost)
        ).first()

        # Расстояние до центра
        min_center, max_center = db.session.query(
            func.min(Excursion.distance_to_center),
            func.max(Excursion.distance_to_center)
        ).filter(Excursion.is_active == True).first()

        # Расстояние до остановки
        min_time, max_time = db.session.query(
            func.min(Excursion.time_to_nearest_stop),
            func.max(Excursion.time_to_nearest_stop)
        ).filter(Excursion.is_active == True).first()

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
            }
        }, 200
