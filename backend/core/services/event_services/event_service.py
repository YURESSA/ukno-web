import json
from datetime import datetime
from http import HTTPStatus
from typing import Optional, List, Union, Tuple, Iterable, Dict, Any
from urllib.parse import quote

from flask import make_response, request, Response
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import aliased, Query
from sqlalchemy.sql.selectable import Selectable, Subquery
from werkzeug.datastructures import FileStorage

from backend.core import db
from backend.core.models.event_models import Event, Category, FormatType, AgeCategory, Tag, Reservation, \
    EventSession
from backend.core.services.email_service import send_event_deletion_email
from backend.core.services.event_services.event_photo_service import process_photos, add_photos
from backend.core.services.event_services.event_session_service import clear_sessions_and_schedules, \
    add_sessions, delete_event_session
from backend.core.services.user_services.auth_service import get_user_by_email
from backend.core.services.utilits import get_model_by_name, generate_reservations_csv, remove_file_if_exists


def get_event(event_id: int, resident_id: Optional[int] = None) -> Optional[Event]:
    """
    Возвращает объект экскурсии по её ID.

    :param event_id: ID экскурсии (события)
    :param resident_id: ID резидента (опционально). Если указан, будет выполнена проверка,
                        что экскурсия принадлежит именно этому резиденту.
    :return: Объект Event, если найден, иначе None.
    """
    query = Event.query.filter_by(event_id=event_id)
    if resident_id is not None:
        query = query.filter_by(created_by=resident_id)
    return query.first()


def get_all_events() -> List[Event]:
    """
    Возвращает список всех экскурсий (событий).

    :return: Список объектов Event.
    """
    return Event.query.all()


def get_events_for_resident(resident_id: int) -> List[Event]:
    """
    Возвращает список всех экскурсий, созданных указанным резидентом.

    :param resident_id: ID резидента (создателя экскурсий)
    :return: Список объектов Event, принадлежащих данному резиденту.
    """
    return Event.query.filter_by(created_by=resident_id).all()


def delete_event(event_id: int, resident, return_csv: bool = False) -> Union[tuple[dict, int], Response]:
    """
    Удаляет экскурсию вместе со всеми её сессиями и фотографиями.

    Если у экскурсии были активные бронирования, пользователям отправляются уведомления,
    а резиденту (удаляющему экскурсию) — CSV-файл со списком отменённых броней.

    :param event_id: ID экскурсии для удаления.
    :param resident: Объект резидента (создатель экскурсии), от имени которого выполняется удаление.
    :param return_csv: Если True — возвращает HTTP-ответ с файлом CSV.
    :return: Кортеж (словарь ответа, HTTP-статус) или Flask Response с CSV-файлом.
    """
    event = Event.query.filter_by(event_id=event_id).first()
    if not event:
        return {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND

    all_reservations = []
    sessions = event.sessions[:]

    for session in sessions:
        result, status = delete_event_session(event_id, session.session_id, notify_resident=False)
        if status >= 400:
            db.session.rollback()
            return {
                "message": f"Ошибка при удалении сессии ID {session.session_id}: {result.get('message', '')}"
            }, status
        all_reservations.extend(result.get("cancelled_reservations", []))

    try:
        for photo in event.photos:
            remove_file_if_exists(photo.photo_url)
            db.session.delete(photo)
        db.session.delete(event)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"message": f"Ошибка при удалении экскурсии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR

    if all_reservations:
        csv_data = generate_reservations_csv(all_reservations)

        send_event_deletion_email(resident, event, csv_data)

        if return_csv:
            response = make_response(csv_data)
            filename = f"отменённые_бронирования_экскурсия_{event.event_id}.csv"
            encoded_filename = quote(filename)
            response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
            response.headers["Content-Type"] = "text/csv; charset=utf-8"
            return response

    return {"message": "Экскурсия и все связанные сессии удалены"}, HTTPStatus.NO_CONTENT


def create_event(
        data: dict,
        email: str,
        files: Optional[list[FileStorage]] = None
) -> Tuple[Optional[Event], dict, Optional[int]]:
    """
    Создаёт новое событие (экскурсию) с сессиями, тегами и фото.

    :param data: Словарь с данными события.
    :param email: Email пользователя (создателя события).
    :param files: Список загруженных файлов для фото экскурсии.
    :return: Кортеж (созданное событие или None, сообщение/данные, HTTP-статус ошибки или None)
             Если всё прошло успешно, HTTP-статус будет None.
    """
    try:
        category = get_model_by_name(Category, "category_name", data.get("category"), "Категория не найдена")
        format_type = get_model_by_name(FormatType, "format_type_name", data.get("format_type"),
                                        "Формат мероприятия не найден")
        age_category = get_model_by_name(AgeCategory, "age_category_name", data.get("age_category"),
                                         "Возрастная категория не найдена")

        if not data.get("place"):
            return None, {"message": "Место проведения обязательно"}, HTTPStatus.BAD_REQUEST

        user = get_user_by_email(email)

        event = Event(
            title=data.get("title"),
            description=data.get("description"),
            duration=data.get("duration"),
            category_id=category.category_id,
            format_type_id=format_type.format_type_id,
            age_category_id=age_category.age_category_id,
            place=data["place"],
            conducted_by=data.get("conducted_by"),
            is_active=data.get("is_active", True),
            working_hours=data.get("working_hours"),
            contact_email=data.get("contact_email"),
            iframe_url=data.get("iframe_url"),
            telegram=data.get("telegram"),
            vk=data.get("vk"),
            created_by=user.user_id,
            distance_to_center=data.get("distance_to_center"),
            time_to_nearest_stop=data.get("time_to_nearest_stop")
        )

        db.session.add(event)
        db.session.flush()

        photos = process_photos(files or [])
        add_photos(event, photos)

        clear_sessions_and_schedules(event)
        add_sessions(event, data.get("sessions", []))

        add_tags(event, data.get("tags", []))

        db.session.commit()
        return event, {"message": "Событие создано", "excursion_id": event.event_id}, None

    except ValueError as ve:
        db.session.rollback()
        return None, {"message": str(ve)}, HTTPStatus.BAD_REQUEST
    except Exception as e:
        db.session.rollback()
        return None, {"message": f"Ошибка при создании экскурсии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


def update_event(event_id: int, data: dict) -> Tuple[Optional[Event], dict, int]:
    """
    Обновляет поля существующей экскурсии.

    :param event_id: ID экскурсии для обновления.
    :param data: Словарь с данными для обновления.
                 Допустимые поля: title, description, duration, place, conducted_by,
                 is_active, working_hours, contact_email, iframe_url, telegram, vk,
                 distance_to_center, time_to_nearest_stop, category, format_type, age_category
    :return: Кортеж (обновленный объект Event или None, словарь с сообщением/данными, HTTP-статус)
    """
    event = db.session.get(Event, event_id)

    if not event:
        return None, {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND

    allowed_fields = [
        'title', 'description', 'duration', 'place', 'conducted_by',
        'is_active', 'working_hours', 'contact_email', 'iframe_url',
        'telegram', 'vk', 'distance_to_center', 'time_to_nearest_stop'
    ]

    for field in allowed_fields:
        if field in data:
            setattr(event, field, data[field])

    if 'category' in data:
        category = Category.query.filter_by(category_name=data['category']).first()
        if not category:
            return None, {"message": f"Категория '{data['category']}' не найдена"}, HTTPStatus.BAD_REQUEST
        event.category = category

    if 'format_type' in data:
        format_type = FormatType.query.filter_by(format_type_name=data['format_type']).first()
        if not format_type:
            return None, {"message": f"Формат '{data['format_type']}' не найден"}, HTTPStatus.BAD_REQUEST
        event.format_type = format_type

    if 'age_category' in data:
        age_category = AgeCategory.query.filter_by(age_category_name=data['age_category']).first()
        if not age_category:
            return None, {
                "message": f"Возрастная категория '{data['age_category']}' не найдена"}, HTTPStatus.BAD_REQUEST
        event.age_category = age_category

    try:
        db.session.commit()
        return event, None, HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return None, {"message": f"Ошибка при обновлении экскурсии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


def add_tags(event: Event, tag_names: Iterable[str]) -> None:
    """
    Добавляет теги к экскурсии. Существующие теги повторно не добавляются.
    Новые теги создаются в базе данных.

    :param event: Объект экскурсии (Event), к которому добавляются теги.
    :param tag_names: Итерация строк с именами тегов.
    :return: None
    """
    for raw in tag_names or []:
        name = raw.strip()
        if not name:
            continue
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.flush()
        if tag not in event.tags:
            event.tags.append(tag)


def verify_resident_owns_event(resident_id: int, event_id: int) -> Tuple[
    Optional[Event], Optional[dict], Optional[int]]:
    """
    Проверяет, принадлежит ли экскурсия конкретному резиденту.

    :param resident_id: ID резидента.
    :param event_id: ID экскурсии.
    :return: Кортеж из трёх элементов:
             - event: объект Event, если проверка успешна, иначе None
             - error: словарь с сообщением об ошибке, если проверка не пройдена, иначе None
             - status: HTTP-статус ошибки, если проверка не пройдена, иначе None
    """
    event = db.session.get(Event, event_id)
    if not event:
        return None, {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND
    if event.created_by != resident_id:
        return None, {"message": "У вас нет доступа к этой экскурсии"}, HTTPStatus.FORBIDDEN
    return event, None, None


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


def apply_sorting(query: Query, sort_key: Optional[str], subquery: Subquery) -> Query:
    """
    Применяет сортировку к SQLAlchemy Query по указанным полям.

    :param query: SQLAlchemy Query объект для модели Event
    :param sort_key: Строка с полями для сортировки, разделёнными запятыми.
                     Можно использовать '-' для сортировки по убыванию (например, "-price").
                     Поддерживаются поля Event и агрегированные значения из subquery: 'price', 'time'.
    :param subquery: Подзапрос с агрегированными значениями (например, min_cost, min_date)
    :return: Обновленный Query с примененной сортировкой
    """
    if not sort_key:
        return query

    sort_fields = [s.strip() for s in sort_key.split(",") if s.strip()]
    order_criteria = []

    for field in sort_fields:
        is_desc = field.startswith("-")
        field_name = field.lstrip("-")

        if field_name == "price":
            order = desc(subquery.c.min_cost) if is_desc else asc(subquery.c.min_cost)
        elif field_name == "time":
            order = desc(subquery.c.min_date) if is_desc else asc(subquery.c.min_date)
        elif hasattr(Event, field_name):
            column = getattr(Event, field_name)
            order = desc(column) if is_desc else asc(column)
        else:
            continue

        order_criteria.append(order)

    if order_criteria:
        query = query.order_by(*order_criteria)

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
