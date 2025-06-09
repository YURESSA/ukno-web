from flask_restx import Resource
from sqlalchemy import func

from backend.core import db
from backend.core.models.excursion_models import FormatType, Category, AgeCategory, Excursion, ExcursionSession
from backend.references import ref_ns


@ref_ns.route('/categories')
class CategoryList(Resource):
    @ref_ns.doc(description="Список всех категорий экскурсий")
    def get(self):
        categories = Category.query.all()
        return [c.to_dict() for c in categories], 200


@ref_ns.route('/format-types')
class FormatTypeList(Resource):
    @ref_ns.doc(description="Список всех типов форматов экскурсий")
    def get(self):
        format_types = FormatType.query.all()
        return [f.to_dict() for f in format_types], 200


@ref_ns.route('/age-categories')
class AgeCategoryList(Resource):
    @ref_ns.doc(description="Список всех возрастных категорий экскурсий")
    def get(self):
        age_categories = AgeCategory.query.all()
        return [a.to_dict() for a in age_categories], 200


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
