import json
from datetime import datetime
from http import HTTPStatus
from typing import Optional, List, Tuple, Dict, Any

from flask import request
from flask_jwt_extended import get_jwt_identity

from backend.core.models.event_models import Event
from backend.core.services.event_services.event_crud import create_event
from backend.core.services.event_services.event_filters import apply_category_filters, apply_format_filters, \
    apply_age_filters, apply_tag_filters, apply_numeric_filters, apply_date_filters, filter_by_title, filter_sessions, \
    build_event_session_subquery
from backend.core.services.event_services.event_sorting import apply_sorting


def list_events(filters: Dict[str, Any], sort_key: Optional[str] = None) -> List[Event]:
    """
    Получает список экскурсий с применением фильтров и сортировки.

    :param filters: Словарь фильтров. Возможные ключи:
        - category, format_type, age_category, tags
        - min_duration, max_duration
        - min_distance_to_center, max_distance_to_center
        - min_distance_to_stop, max_distance_to_stop
        - min_price, max_price
        - start_date, end_date
        - title
    :param sort_key: Ключ сортировки. Можно с "-", например: "-price", "-time".
    :return: Список объектов Event, удовлетворяющих фильтрам.
    """
    now = datetime.now()
    subquery = build_event_session_subquery(now)
    query = Event.query.join(subquery, Event.event_id == subquery.c.event_id)

    query = apply_category_filters(query, filters)
    query = apply_format_filters(query, filters)
    query = apply_age_filters(query, filters)
    query = apply_tag_filters(query, filters)
    query = apply_numeric_filters(query, filters, subquery)
    query = apply_date_filters(query, filters, subquery)
    query = apply_sorting(query, sort_key, subquery)

    events = query.all()
    events = filter_by_title(events, filters)
    events = filter_sessions(events, now)

    return events


def handle_create_event(
        data_field: str = 'data',
        files_field: str = 'photos',
        creator_email: Optional[str] = None
) -> Tuple[Dict, int]:
    """
    Обрабатывает создание экскурсии через POST-запрос с multipart/form-data.

    Ожидается JSON в поле формы `data_field` и файлы в `files_field`.

    :param data_field: имя поля формы с JSON-данными экскурсии (по умолчанию 'data')
    :param files_field: имя поля формы с файлами фото (по умолчанию 'photos')
    :param creator_email: email создателя; если None, берется из JWT
    :return: кортеж (словарь с результатом, HTTP-статус)
    """
    if data_field not in request.form:
        return {"message": f"Поле '{data_field}' обязательно"}, HTTPStatus.BAD_REQUEST

    try:
        data = json.loads(request.form[data_field])
    except json.JSONDecodeError as e:
        return {"message": f"Неверный JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST

    files = request.files.getlist(files_field)
    creator = creator_email or get_jwt_identity()

    event, error, status = create_event(data, creator, files)
    if error:
        return error, status

    return {"message": "Событие создано", "event_id": event.event_id}, HTTPStatus.CREATED
