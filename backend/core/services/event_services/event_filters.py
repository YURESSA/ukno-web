from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy import Subquery, Selectable, func
from sqlalchemy.orm import Query, aliased

from backend.core import db
from backend.core.models.event_models import Category, FormatType, AgeCategory, Event, Tag, EventSession


def apply_category_filters(query: Query, filters: Dict[str, Any]) -> Query:
    """
    Применяет фильтр по категории к SQLAlchemy-запросу событий.

    :param query: Исходный SQLAlchemy Query объект для модели Event
    :param filters: Словарь фильтров, может содержать ключ 'category' с
                    строкой категорий, разделенных запятыми
    :return: Обновленный Query с примененным фильтром по категории
    """
    if category := filters.get("category"):
        category_list = [c.strip() for c in category.split(",") if c.strip()]
        if category_list:
            query = query.join(Category).filter(Category.category_name.in_(category_list))
    return query


def apply_format_filters(query: Query, filters: Dict[str, Any]) -> Query:
    """
    Применяет фильтр по типу формата к SQLAlchemy-запросу событий.

    :param query: Исходный SQLAlchemy Query объект для модели Event
    :param filters: Словарь фильтров, может содержать ключ 'format_type' с
                    строкой форматов, разделенных запятыми
    :return: Обновленный Query с примененным фильтром по формату
    """
    if format_type := filters.get("format_type"):
        format_type_list = [f.strip() for f in format_type.split(",") if f.strip()]
        if format_type_list:
            query = query.join(FormatType).filter(FormatType.format_type_name.in_(format_type_list))
    return query


def apply_age_filters(query: Query, filters: Dict[str, Any]) -> Query:
    """
    Применяет фильтр по возрастной категории к SQLAlchemy-запросу событий.

    :param query: Исходный SQLAlchemy Query объект для модели Event
    :param filters: Словарь фильтров, может содержать ключ 'age_category' с
                    строкой возрастных категорий, разделенных запятыми
    :return: Обновленный Query с примененным фильтром по возрастной категории
    """
    if age_category := filters.get("age_category"):
        age_category_list = [a.strip() for a in age_category.split(",") if a.strip()]
        if age_category_list:
            query = query.join(AgeCategory).filter(AgeCategory.age_category_name.in_(age_category_list))
    return query


def apply_tag_filters(query: Query, filters: Dict[str, Any]) -> Query:
    """
    Применяет фильтр по тегам к SQLAlchemy-запросу событий.

    :param query: SQLAlchemy Query объект для модели Event
    :param filters: Словарь фильтров, может содержать ключ 'tags' с
                    строкой тегов, разделенных запятыми
    :return: Обновленный Query с примененным фильтром по тегам
    """
    if tags := filters.get("tags"):
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            query = query.filter(Event.tags.any(Tag.name.in_(tag_list)))
    return query


def apply_numeric_filters(query: Query, filters: Dict[str, Any], subquery: Subquery) -> Query:
    """
    Применяет числовые фильтры к SQLAlchemy-запросу событий.

    :param query: SQLAlchemy Query объект для модели Event
    :param filters: Словарь фильтров, может содержать числовые параметры:
                    'min_duration', 'max_duration',
                    'min_distance_to_center', 'max_distance_to_center',
                    'min_distance_to_stop', 'max_distance_to_stop',
                    'min_price', 'max_price'
    :param subquery: Подзапрос с агрегированными значениями (например, min_cost)
    :return: Обновленный Query с примененными числовыми фильтрами
    """
    try:
        if min_duration := filters.get("min_duration"):
            query = query.filter(Event.duration >= int(min_duration))
        if max_duration := filters.get("max_duration"):
            query = query.filter(Event.duration <= int(max_duration))
        if min_center_distance := filters.get("min_distance_to_center"):
            query = query.filter(Event.distance_to_center >= float(min_center_distance))
        if max_center_distance := filters.get("max_distance_to_center"):
            query = query.filter(Event.distance_to_center <= float(max_center_distance))
        if min_type_to_stop := filters.get("min_distance_to_stop"):
            query = query.filter(Event.time_to_nearest_stop >= float(min_type_to_stop))
        if max_type_to_stop := filters.get("max_distance_to_stop"):
            query = query.filter(Event.time_to_nearest_stop <= float(max_type_to_stop))
        if min_price := filters.get("min_price"):
            query = query.filter(subquery.c.min_cost >= float(min_price))
        if max_price := filters.get("max_price"):
            query = query.filter(subquery.c.min_cost <= float(max_price))
    except ValueError:
        pass
    return query


def apply_date_filters(query: Query, filters: Dict[str, Any], subquery: Subquery) -> Query:
    """
    Применяет фильтры по дате к SQLAlchemy-запросу событий.

    :param query: SQLAlchemy Query объект для модели Event
    :param filters: Словарь фильтров, может содержать ключи:
                    'start_date' и 'end_date' в формате ISO (YYYY-MM-DD или YYYY-MM-DDTHH:MM:SS)
    :param subquery: Подзапрос с агрегированными значениями (например, min_date)
    :return: Обновленный Query с примененными фильтрами по дате
    """
    try:
        if start_date := filters.get("start_date"):
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(subquery.c.min_date >= start_dt)
        if end_date := filters.get("end_date"):
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(subquery.c.min_date <= end_dt)
    except ValueError:
        pass
    return query


def filter_by_title(events: List[Any], filters: Dict[str, str]) -> List[Any]:
    """
    Фильтрует список событий по ключевому слову в названии.

    :param events: Список объектов Event
    :param filters: Словарь фильтров, ожидается ключ 'title' для поиска
    :return: Отфильтрованный список событий, содержащих подстроку в названии
    """
    if title := filters.get("title"):
        clean_title = title.strip().lower()
        return [event for event in events if clean_title in event.title.lower()]
    return events


def filter_sessions(events: List[Any], now: datetime) -> List[Any]:
    """
    Фильтрует сессии каждого события, оставляя только будущие сессии.

    :param events: Список объектов Event, у которых есть атрибут sessions (список EventSession)
    :param now: Текущая дата и время для фильтрации
    :return: Список событий с обновленным списком будущих сессий
    """
    for event in events:
        event.sessions = [s for s in event.sessions if s.start_datetime > now]
    return events


def build_event_session_subquery(now: datetime) -> Selectable:
    """
    Создает подзапрос для агрегирования сессий событий (экскурсий) с будущими датами.

    :param now: Текущая дата и время. Используется для фильтрации будущих сессий.
    :return: SQLAlchemy подзапрос с колонками:
             - event_id
             - min_cost (минимальная стоимость сессии)
             - min_date (дата ближайшей сессии)
    """
    session_alias = aliased(EventSession)
    return (
        db.session.query(
            session_alias.event_id,
            func.min(session_alias.cost).label("min_cost"),
            func.min(session_alias.start_datetime).label("min_date")
        )
        .filter(session_alias.start_datetime > now)
        .group_by(session_alias.event_id)
        .subquery()
    )
