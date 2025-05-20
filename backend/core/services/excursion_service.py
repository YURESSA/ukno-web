import os
from http import HTTPStatus

from sqlalchemy import desc, asc

from backend.core.models.excursion_models import *
from backend.core.services.utilits import save_image


def get_excursion_or_404(excursion_id, resident_id):
    return Excursion.query.filter_by(
        excursion_id=excursion_id,
        created_by=resident_id
    ).first()


def get_excursions_for_resident(resident_id):
    return Excursion.query.filter_by(created_by=resident_id).all()


def clear_photos(excursion):
    for photo in list(excursion.photos):
        fs_path = photo.photo_url.lstrip('/')
        if os.path.exists(fs_path):
            os.remove(fs_path)
        db.session.delete(photo)


def clear_sessions_and_schedules(excursion):
    ExcursionSession.query.filter_by(
        excursion_id=excursion.excursion_id
    ).delete()
    RecurringSchedule.query.filter_by(
        excursion_id=excursion.excursion_id
    ).delete()


def process_photos(files):
    photos = []
    for idx, file in enumerate(files):
        if not file or not file.filename or not file.content_type:
            continue
        if not file.content_type.startswith("image/"):
            raise ValueError("Файл должен быть изображением")
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > 5 * 1024 * 1024:
            raise ValueError("Размер файла не должен превышать 5 MB")
        rel_path = save_image(file, "excursion_photos")
        photos.append({"photo_url": rel_path, "order_index": idx})
    return photos


def add_photos(excursion, photos):
    for p in photos:
        db.session.add(ExcursionPhoto(
            excursion_id=excursion.excursion_id,
            photo_url=p["photo_url"],
            order_index=p.get("order_index", 0)
        ))


def add_sessions(excursion, sessions):
    for s in sessions:
        start_dt = datetime.fromisoformat(s["start_datetime"])
        db.session.add(ExcursionSession(
            excursion_id=excursion.excursion_id,
            start_datetime=start_dt,
            max_participants=s["max_participants"],
            cost=s["cost"]
        ))

def add_schedules(excursion, schedules):
    for r in schedules:
        start_time = datetime.strptime(r["start_time"], "%H:%M").time()
        db.session.add(RecurringSchedule(
            excursion_id=excursion.excursion_id,
            weekday=r["weekday"],
            start_time=start_time,
            repeats=r["repeats"],
            max_participants=r["max_participants"],
            cost=r["cost"]
        ))


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


def create_excursion(data, created_by, files):
    cat = Category.query.filter_by(category_name=data.get("category")).first()
    if not cat:
        return None, {"message": "Категория не найдена"}, HTTPStatus.BAD_REQUEST
    et = EventType.query.filter_by(event_type_name=data.get("event_type")).first()
    if not et:
        return None, {"message": "Тип события не найден"}, HTTPStatus.BAD_REQUEST

    excursion = Excursion(
        title=data.get("title"),
        description=data.get("description"),
        duration=data.get("duration"),
        category_id=cat.category_id,
        event_type_id=et.event_type_id,
        is_active=data.get("is_active"),
        created_by=created_by
    )
    db.session.add(excursion)
    db.session.flush()

    add_photos(excursion, process_photos(files or []))
    clear_sessions_and_schedules(excursion)
    add_sessions(excursion, data.get("sessions", []))
    add_schedules(excursion, data.get("recurring_schedule", []))

    add_tags(excursion, data.get("tags", []))

    db.session.commit()
    return excursion, None, None


def update_excursion(excursion, data, files):
    for field in ['title', 'description', 'duration', 'category_id', 'event_type_id', 'is_active']:
        if field in data:
            setattr(excursion, field, data[field])

    clear_photos(excursion)
    add_photos(excursion, process_photos(files or []))

    incoming = data.get("sessions", [])
    existing = {s.start_datetime.isoformat(): s for s in excursion.sessions}

    for s_data in incoming:
        dt_str = s_data["start_datetime"]
        try:
            dt = datetime.fromisoformat(dt_str)
        except ValueError:
            return {"message": f"Неверный формат даты: {dt_str}"}, HTTPStatus.BAD_REQUEST

        max_p = s_data["max_participants"]
        cost = s_data["cost"]

        if dt_str in existing:
            sess = existing.pop(dt_str)
            booked = len(sess.reservations)
            if max_p < booked:
                return {
                    "message": f"Нельзя уменьшить max_participants сеанса {dt_str} ниже уже забронированного ({booked})"
                }, HTTPStatus.BAD_REQUEST

            sess.max_participants = max_p
            sess.cost = cost
        else:
            new_sess = ExcursionSession(
                excursion_id=excursion.excursion_id,
                start_datetime=dt,
                max_participants=max_p,
                cost=cost
            )
            db.session.add(new_sess)

    for dt_str, sess in existing.items():
        if sess.reservations:
            return {
                "message": (
                    f"Нельзя удалить сеанс {dt_str}, "
                    f"на который есть бронирования"
                )
            }, HTTPStatus.BAD_REQUEST
        db.session.delete(sess)

    RecurringSchedule.query.filter_by(excursion_id=excursion.excursion_id).delete()
    add_schedules(excursion, data.get("recurring_schedule", []))

    excursion.tags.clear()
    add_tags(excursion, data.get("tags", []))
    db.session.commit()
    return {"message": "Экскурсия успешно обновлена"}, HTTPStatus.OK


def serialize_excursion(excursion):
    return {
        "id": excursion.excursion_id,
        "title": excursion.title,
        "description": excursion.description,
        "duration": excursion.duration,
        "category": serialize_category(excursion.category),
        "event_type": serialize_event_type(excursion.event_type),
        "is_active": excursion.is_active,
        "photos": serialize_photos(excursion.photos),
        "sessions": serialize_sessions(excursion.sessions),
        "recurring_schedule": serialize_recurring_schedule(excursion.recurring_schedules),
        "tags": serialize_tags(excursion.tags)
    }


def serialize_category(category):
    return category.to_dict() if category else None


def serialize_event_type(event_type):
    return event_type.to_dict() if event_type else None


def serialize_photos(photos):
    return [
        p.to_dict()
        for p in photos
    ]


def serialize_sessions(sessions):
    return [
        s.to_dict()
        for s in sessions
    ]


def serialize_recurring_schedule(recurring_schedules):
    return [
        r.to_dict()
        for r in recurring_schedules
    ]


def serialize_tags(tags):
    return [
        t.to_dict()
        for t in tags
    ]


def list_excursions(filters, sort_key):
    query = Excursion.query

    category = filters.get("category")
    if category:
        query = query.join(Category).filter(Category.category_name == category.strip())

    event_type = filters.get("event_type")
    if event_type:
        query = query.join(EventType).filter(EventType.event_type_name == event_type.strip())

    tags = filters.get("tags")
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            query = query.filter(Excursion.tags.any(Tag.name.in_(tag_list)))

    min_duration = filters.get("min_duration")
    if min_duration:
        try:
            query = query.filter(Excursion.duration >= int(min_duration))
        except ValueError:
            pass

    max_duration = filters.get("max_duration")
    if max_duration:
        try:
            query = query.filter(Excursion.duration <= int(max_duration))
        except ValueError:
            pass

    title = filters.get("title")
    if title:
        query = query.filter(Excursion.title.ilike(f"%{title.strip()}%"))

    if sort_key:
        field_name = sort_key.lstrip("-")
        if hasattr(Excursion, field_name):
            column = getattr(Excursion, field_name)
            order = desc(column) if sort_key.startswith("-") else asc(column)
            query = query.order_by(order)

    return query.all()


def get_resident_excursion_analytics(resident_id):
    excursions = db.session.query(Excursion).filter_by(created_by=resident_id).all()

    if not excursions:
        return {"message": "У вас пока нет экскурсий", "stats": []}

    result = []
    total_visitors = 0
    most_popular = None
    max_reservations = 0

    for excursion in excursions:
        sessions = excursion.sessions
        session_count = len(sessions)
        excursion_total_reservations = sum(len(session.reservations) for session in sessions)

        if excursion_total_reservations > max_reservations:
            most_popular = excursion
            max_reservations = excursion_total_reservations

        total_visitors += excursion_total_reservations

        result.append({
            "excursion_id": excursion.excursion_id,
            "title": excursion.title,
            "session_count": session_count,
            "total_reservations": excursion_total_reservations,
        })

    return {
        "total_excursions": len(excursions),
        "total_visitors": total_visitors,
        "most_popular_excursion": {
            "title": most_popular.title,
            "total_reservations": max_reservations
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
            session_data['reservations'].append({
                'reservation_id': reservation.reservation_id,
                'user_id': reservation.user_id,
                'booked_at': reservation.booked_at.isoformat(),
                'user': {
                    'user_id': reservation.user.user_id,
                    'full_name': reservation.user.full_name,
                    'email': reservation.user.email
                } if reservation.user else None
            })

        result['sessions'].append(session_data)

    return result
