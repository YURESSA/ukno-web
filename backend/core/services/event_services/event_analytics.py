from typing import Dict, Any

from sqlalchemy import func

from backend.core import db
from backend.core.models.event_models import Event, Reservation, EventSession


def get_resident_event_analytics(resident_id: int) -> Dict[str, Any]:
    """
    Получает аналитику по экскурсиям конкретного резидента.

    Считает количество сессий, общее число участников и определяет самую популярную экскурсию.

    :param resident_id: ID резидента
    :return: Словарь с общей статистикой и деталями по каждой экскурсии
    """
    events = db.session.query(Event).filter_by(created_by=resident_id).all()

    if not events:
        return {"message": "У вас пока нет экскурсий", "stats": []}

    result = []
    total_visitors = 0
    most_popular = None
    max_participants = 0

    for event in events:
        session_count = len(event.sessions)
        excursion_total_participants = db.session.query(
            func.coalesce(func.sum(Reservation.participants_count), 0)
        ).join(EventSession).filter(
            EventSession.event_id == event.event_id,
            ~Reservation.is_cancelled
        ).scalar()

        if excursion_total_participants > max_participants:
            most_popular = event
            max_participants = excursion_total_participants

        total_visitors += excursion_total_participants

        result.append({
            "excursion_id": event.event_id,
            "title": event.title,
            "session_count": session_count,
            "total_participants": excursion_total_participants,
        })

    return {
        "total_excursions": len(events),
        "total_visitors": total_visitors,
        "most_popular_excursion": {
            "title": most_popular.title,
            "total_participants": max_participants
        } if most_popular else None,
        "details": result
    }
