from sqlalchemy import func

from backend.core import db
from backend.core.models.auth_models import RoleEnum
from backend.core.models.event_models import (
    Event,
    EventSession,
    AgeCategory,
    FormatType,
    Category
)


def get_excursion_stats() -> dict:
    # Стоимость сессий
    min_cost, max_cost = db.session.query(
        func.min(EventSession.cost),
        func.max(EventSession.cost)
    ).first()

    # Расстояние до центра
    min_center, max_center = db.session.query(
        func.min(Event.distance_to_center),
        func.max(Event.distance_to_center)
    ).filter(Event.is_active.is_(True)).first()

    # Время до остановки
    min_time, max_time = db.session.query(
        func.min(Event.time_to_nearest_stop),
        func.max(Event.time_to_nearest_stop)
    ).filter(Event.is_active.is_(True)).first()

    return {
        "cost": {
            "min": float(min_cost) if min_cost is not None else 0,
            "max": float(max_cost) if max_cost is not None else 0
        },
        "distance_to_center": {
            "min": round(min_center, 2) if min_center is not None else 0,
            "max": round(max_center, 2) if max_center is not None else 0
        },
        "time_to_stop": {
            "min": round(min_time, 2) if min_time is not None else 0,
            "max": round(max_time, 2) if max_time is not None else 0
        },
        "roles": [role.to_dict() for role in RoleEnum],
        "age_categories": [a.to_dict() for a in AgeCategory.query.all()],
        "format_types": [f.to_dict() for f in FormatType.query.all()],
        "categories": [c.to_dict() for c in Category.query.all()],
    }
