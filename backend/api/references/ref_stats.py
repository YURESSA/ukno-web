from flask_restx import Resource
from sqlalchemy import func

from backend.core import db
from backend.core.models.auth_models import Role
from backend.core.models.event_models import FormatType, Category, AgeCategory, Event, EventSession
from backend.api.references import ref_ns


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
