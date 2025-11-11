from http import HTTPStatus
from typing import Optional, List, Union, Tuple, Iterable
from urllib.parse import quote

from flask import Response, make_response
from werkzeug.datastructures import FileStorage

from backend.core import db
from backend.core.models.event_models import Event, Category, FormatType, AgeCategory, Tag
from backend.core.services.email_service.email_service import send_event_deletion_email

from backend.core.services.event_services.event_photo_service import process_photos, add_photos
from backend.core.services.event_services.event_session_service import delete_event_session, \
    clear_sessions_and_schedules, add_sessions
from backend.core.services.user_services.user_service import get_user_by_email
from backend.core.utilits.model_utils import get_model_by_name
from backend.core.utilits.file_utils import remove_file_if_exists, generate_reservations_csv


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


def verify_resident_owns_event(
        resident_id: int,
        event_id: int
) -> Tuple[Optional[Event], Optional[dict], Optional[int]]:
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
