from datetime import datetime
from http import HTTPStatus
from urllib.parse import quote

from flask import make_response
from sqlalchemy import func
from sqlalchemy.orm import aliased

from backend.core import db
from backend.core.models.excursion_models import Excursion, Category, FormatType, AgeCategory, Tag, Reservation, \
    ExcursionSession
from backend.core.services.email_service import send_excursion_deletion_email
from backend.core.services.excursion_services.excursion_photo_service import process_photos, add_photos
from backend.core.services.excursion_services.excursion_session_service import clear_sessions_and_schedules, \
    add_sessions, delete_excursion_session
from backend.core.services.user_services.auth_service import get_user_by_email
from backend.core.services.utilits import get_model_by_name, generate_reservations_csv, remove_file_if_exists


def get_excursion(excursion_id, resident_id=None):
    query = Excursion.query.filter_by(excursion_id=excursion_id)
    if resident_id is not None:
        query = query.filter_by(created_by=resident_id)
    return query.first()


def get_all_excursions():
    return Excursion.query.all()


def get_excursions_for_resident(resident_id):
    return Excursion.query.filter_by(created_by=resident_id).all()


def delete_excursion(excursion_id, resident, return_csv=False):
    excursion = Excursion.query.filter_by(excursion_id=excursion_id).first()
    if not excursion:
        return {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND

    all_reservations = []
    sessions = excursion.sessions[:]

    for session in sessions:
        result, status = delete_excursion_session(excursion_id, session.session_id, notify_resident=False)
        if status >= 400:
            db.session.rollback()
            return {
                "message": f"Ошибка при удалении сессии ID {session.session_id}: {result.get('message', '')}"
            }, status
        all_reservations.extend(result.get("cancelled_reservations", []))

    try:
        for photo in excursion.photos:
            remove_file_if_exists(photo.photo_url)
            db.session.delete(photo)
        db.session.delete(excursion)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"message": f"Ошибка при удалении экскурсии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR

    if all_reservations:
        csv_data = generate_reservations_csv(all_reservations)

        send_excursion_deletion_email(resident, excursion, csv_data)

        if return_csv:
            response = make_response(csv_data)
            filename = f"отменённые_бронирования_экскурсия_{excursion.excursion_id}.csv"
            encoded_filename = quote(filename)
            response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
            response.headers["Content-Type"] = "text/csv; charset=utf-8"
            return response

    return {"message": "Экскурсия и все связанные сессии удалены"}, HTTPStatus.NO_CONTENT


def create_excursion(data, email, files):
    try:
        category = get_model_by_name(Category, "category_name", data.get("category"), "Категория не найдена")
        format_type = get_model_by_name(FormatType, "format_type_name", data.get("format_type"),
                                        "Формат мероприятия не найден")
        age_category = get_model_by_name(AgeCategory, "age_category_name", data.get("age_category"),
                                         "Возрастная категория не найдена")

        if not data.get("place"):
            return None, {"message": "Место проведения обязательно"}, HTTPStatus.BAD_REQUEST

        user = get_user_by_email(email)

        excursion = Excursion(
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

        db.session.add(excursion)
        db.session.flush()

        photos = process_photos(files or [])
        add_photos(excursion, photos)

        clear_sessions_and_schedules(excursion)
        add_sessions(excursion, data.get("sessions", []))

        add_tags(excursion, data.get("tags", []))

        db.session.commit()
        return excursion, {"message": "Событие создано", "excursion_id": excursion.excursion_id}, None

    except ValueError as ve:
        db.session.rollback()
        return None, {"message": str(ve)}, HTTPStatus.BAD_REQUEST
    except Exception as e:
        db.session.rollback()
        return None, {"message": f"Ошибка при создании экскурсии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


def update_excursion(excursion_id, data):
    excursion = db.session.get(Excursion, excursion_id)

    if not excursion:
        return None, {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND

    allowed_fields = [
        'title', 'description', 'duration', 'place', 'conducted_by',
        'is_active', 'working_hours', 'contact_email', 'iframe_url',
        'telegram', 'vk', 'distance_to_center', 'time_to_nearest_stop'
    ]

    for field in allowed_fields:
        if field in data:
            setattr(excursion, field, data[field])

    if 'category' in data:
        category = Category.query.filter_by(category_name=data['category']).first()
        if not category:
            return None, {"message": f"Категория '{data['category']}' не найдена"}, HTTPStatus.BAD_REQUEST
        excursion.category = category

    if 'format_type' in data:
        format_type = FormatType.query.filter_by(format_type_name=data['format_type']).first()
        if not format_type:
            return None, {"message": f"Формат '{data['format_type']}' не найден"}, HTTPStatus.BAD_REQUEST
        excursion.format_type = format_type

    if 'age_category' in data:
        age_category = AgeCategory.query.filter_by(age_category_name=data['age_category']).first()
        if not age_category:
            return None, {
                "message": f"Возрастная категория '{data['age_category']}' не найдена"}, HTTPStatus.BAD_REQUEST
        excursion.age_category = age_category

    try:
        db.session.commit()
        return excursion, None, HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return None, {"message": f"Ошибка при обновлении экскурсии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


def add_tags(excursion, tag_names):
    for raw in tag_names or []:
        name = raw.strip()
        if not name:
            continue
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.flush()
        if tag not in excursion.tags:
            excursion.tags.append(tag)


from sqlalchemy import asc, desc


def verify_resident_owns_excursion(resident_id, excursion_id):
    excursion = Excursion.query.get(excursion_id)
    if not excursion:
        return None, {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND
    if excursion.created_by != resident_id:
        return None, {"message": "У вас нет доступа к этой экскурсии"}, HTTPStatus.FORBIDDEN
    return excursion, None, None


def list_excursions(filters, sort_key):
    now = datetime.now()

    session_alias = aliased(ExcursionSession)

    subquery = (
        db.session.query(
            session_alias.excursion_id,
            func.min(session_alias.cost).label("min_cost"),
            func.min(session_alias.start_datetime).label("min_date")
        )
        .filter(session_alias.start_datetime > now)
        .group_by(session_alias.excursion_id)
        .subquery()
    )

    query = Excursion.query.join(subquery, Excursion.excursion_id == subquery.c.excursion_id)

    if category := filters.get("category"):
        category_list = [c.strip() for c in category.split(",") if c.strip()]
        if category_list:
            query = query.join(Category).filter(Category.category_name.in_(category_list))

    if format_type := filters.get("format_type"):
        format_type_list = [f.strip() for f in format_type.split(",") if f.strip()]
        if format_type_list:
            query = query.join(FormatType).filter(FormatType.format_type_name.in_(format_type_list))

    if age_category := filters.get("age_category"):
        age_category_list = [a.strip() for a in age_category.split(",") if a.strip()]
        if age_category_list:
            query = query.join(AgeCategory).filter(AgeCategory.age_category_name.in_(age_category_list))

    if tags := filters.get("tags"):
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            query = query.filter(Excursion.tags.any(Tag.name.in_(tag_list)))

    try:
        if min_duration := filters.get("min_duration"):
            query = query.filter(Excursion.duration >= int(min_duration))
    except ValueError:
        pass
    try:
        if max_duration := filters.get("max_duration"):
            query = query.filter(Excursion.duration <= int(max_duration))
    except ValueError:
        pass

    try:
        if min_center_distance := filters.get("min_distance_to_center"):
            query = query.filter(Excursion.distance_to_center >= float(min_center_distance))
    except ValueError:
        pass
    try:
        if max_center_distance := filters.get("max_distance_to_center"):
            query = query.filter(Excursion.distance_to_center <= float(max_center_distance))
    except ValueError:
        pass

    try:
        if min_type_to_stop := filters.get("min_distance_to_stop"):
            query = query.filter(Excursion.time_to_nearest_stop >= float(min_type_to_stop))
    except ValueError:
        pass
    try:
        if max_type_to_stop := filters.get("max_distance_to_stop"):
            query = query.filter(Excursion.time_to_nearest_stop <= float(max_type_to_stop))
    except ValueError:
        pass

    try:
        if min_price := filters.get("min_price"):
            query = query.filter(subquery.c.min_cost >= float(min_price))
    except ValueError:
        pass
    try:
        if max_price := filters.get("max_price"):
            query = query.filter(subquery.c.min_cost <= float(max_price))
    except ValueError:
        pass

    try:
        if start_date := filters.get("start_date"):
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(subquery.c.min_date >= start_dt)
    except ValueError:
        pass
    try:
        if end_date := filters.get("end_date"):
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(subquery.c.min_date <= end_dt)
    except ValueError:
        pass

    if sort_key:
        sort_fields = [s.strip() for s in sort_key.split(",") if s.strip()]
        order_criteria = []
        for field in sort_fields:
            is_desc = field.startswith("-")
            field_name = field.lstrip("-")

            if field_name == "price":
                order = desc(subquery.c.min_cost) if is_desc else asc(subquery.c.min_cost)
                order_criteria.append(order)
            elif field_name == "time":
                order = desc(subquery.c.min_date) if is_desc else asc(subquery.c.min_date)
                order_criteria.append(order)
            elif hasattr(Excursion, field_name):
                column = getattr(Excursion, field_name)
                order = desc(column) if is_desc else asc(column)
                order_criteria.append(order)

        if order_criteria:
            query = query.order_by(*order_criteria)
    excursions = query.all()

    if title := filters.get("title"):
        clean_title = title.strip().lower()
        excursions = [
            excursion for excursion in excursions
            if clean_title in excursion.title.lower()
        ]

    for excursion in excursions:
        excursion.sessions = [s for s in excursion.sessions if s.start_datetime > now]

    return excursions


def get_resident_excursion_analytics(resident_id):
    excursions = db.session.query(Excursion).filter_by(created_by=resident_id).all()

    if not excursions:
        return {"message": "У вас пока нет экскурсий", "stats": []}

    result = []
    total_visitors = 0
    most_popular = None
    max_participants = 0

    for excursion in excursions:
        session_count = len(excursion.sessions)
        excursion_total_participants = db.session.query(
            func.coalesce(func.sum(Reservation.participants_count), 0)
        ).join(ExcursionSession).filter(
            ExcursionSession.excursion_id == excursion.excursion_id,
            Reservation.is_cancelled == False
        ).scalar()

        if excursion_total_participants > max_participants:
            most_popular = excursion
            max_participants = excursion_total_participants

        total_visitors += excursion_total_participants

        result.append({
            "excursion_id": excursion.excursion_id,
            "title": excursion.title,
            "session_count": session_count,
            "total_participants": excursion_total_participants,
        })

    return {
        "total_excursions": len(excursions),
        "total_visitors": total_visitors,
        "most_popular_excursion": {
            "title": most_popular.title,
            "total_participants": max_participants
        } if most_popular else None,
        "details": result
    }


def get_detailed_excursion_with_reservations(excursion):
    result = excursion.to_dict()
    result['sessions'] = []

    for session in excursion.sessions:
        session_data = session.to_dict()
        session_data['reservations'] = []

        for reservation in session.reservations:
            if reservation.is_cancelled:
                continue
            session_data['reservations'].append({
                'reservation_id': reservation.reservation_id,
                'user_id': reservation.user_id,
                'booked_at': reservation.booked_at.isoformat(),
                'participants_count': reservation.participants_count,
                'user': {
                    'user_id': reservation.user.user_id,
                    'full_name': reservation.user.full_name,
                    'email': reservation.user.email
                } if reservation.user else None
            })

        result['sessions'].append(session_data)

    return result
