from datetime import datetime
from urllib.parse import quote

from flask import make_response
from flask_jwt_extended import get_jwt_identity

from backend.core import db
from backend.core.models.excursion_models import ExcursionSession
from backend.core.services.auth_service import get_user_by_email
from backend.core.services.utilits import send_email, generate_reservations_csv


def clear_sessions_and_schedules(excursion):
    ExcursionSession.query.filter_by(excursion_id=excursion.excursion_id).delete()


def add_sessions(excursion, sessions):
    for s in sessions:
        start_dt = datetime.fromisoformat(s["start_datetime"])
        db.session.add(ExcursionSession(
            excursion_id=excursion.excursion_id,
            start_datetime=start_dt,
            max_participants=s["max_participants"],
            cost=s["cost"]
        ))


def get_sessions_for_excursion(excursion_id):
    return ExcursionSession.query.filter_by(excursion_id=excursion_id).all()


def create_excursion_session(excursion_id, data):
    try:
        start_dt = datetime.fromisoformat(data['start_datetime'])
    except (KeyError, ValueError):
        return None, {"message": "Неверный или отсутствует start_datetime"}, HTTPStatus.BAD_REQUEST

    new_session = ExcursionSession(
        excursion_id=excursion_id,
        start_datetime=start_dt,
        max_participants=data.get('max_participants'),
        cost=data.get('cost')
    )
    try:
        db.session.add(new_session)
        db.session.commit()
        return new_session, None, HTTPStatus.CREATED
    except Exception as e:
        db.session.rollback()
        return None, {"message": f"Ошибка при создании сессии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


def update_excursion_session(excursion_id, session_id, data):
    session = ExcursionSession.query.filter_by(excursion_id=excursion_id, session_id=session_id).first()
    if not session:
        return None, {"message": "Сессия не найдена"}, HTTPStatus.NOT_FOUND

    if 'start_datetime' in data:
        try:
            session.start_datetime = datetime.fromisoformat(data['start_datetime'])
        except ValueError:
            return None, {"message": "Неверный формат start_datetime"}, HTTPStatus.BAD_REQUEST
    if 'max_participants' in data:
        session.max_participants = data['max_participants']
    if 'cost' in data:
        session.cost = data['cost']

    try:
        db.session.commit()
        return session, None, HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return None, {"message": f"Ошибка при обновлении сессии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


from http import HTTPStatus


def delete_excursion_session(excursion_id, session_id, notify_resident=True):
    email = get_jwt_identity()
    user = get_user_by_email(email)
    deleter_email = user.email
    session = ExcursionSession.query.filter_by(excursion_id=excursion_id, session_id=session_id).first()
    if not session:
        return {"message": "Сессия не найдена"}, HTTPStatus.NOT_FOUND

    active_reservations = [r for r in session.reservations if not r.is_cancelled]
    excursion_name = session.excursion.title if session.excursion else "экскурсии"

    # Письма клиентам
    for res in active_reservations:
        send_email(
            subject="Отмена экскурсионной сессии",
            recipient=res.email,
            body=(
                f"Здравствуйте, {res.full_name}!\n\n"
                f"Сессия экскурсии «{excursion_name}» (ID {session_id}) на {session.start_datetime.strftime('%d.%m.%Y %H:%M')} отменена.\n"
                "Ваше бронирование автоматически аннулировано.\n\n"
                "Приносим извинения за возможные неудобства."
            )
        )

    cancelled_reservations = [
        {
            "reservation_id": res.reservation_id,
            "full_name": res.full_name,
            "email": res.email,
            "phone_number": res.phone_number,
            "participants_count": res.participants_count,
            "booked_at": res.booked_at.strftime("%Y-%m-%d %H:%M"),
            "session_datetime": session.start_datetime.strftime("%d.%m.%Y %H:%M"),
            "excursion_title": excursion_name
        }
        for res in active_reservations
    ]

    if notify_resident and cancelled_reservations:
        csv_data = generate_reservations_csv(cancelled_reservations)
        send_email(
            subject="Список отменённых бронирований по сессии",
            recipient=deleter_email,
            body=(
                f"Сессия экскурсии «{excursion_name}» (ID {session_id}) была удалена.\n"
                "В приложении — список бронирований, которые были отменены."
            ),
            attachments=[("cancelled_reservations.csv", csv_data)]
        )
    else:
        csv_data = None

    try:
        db.session.delete(session)
        db.session.commit()

        if notify_resident and csv_data:
            response = make_response(csv_data)
            filename = f"отмененные_бронирования_сессия_{session_id}.csv"
            encoded_filename = quote(filename)
            response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
            response.headers["Content-Type"] = "text/csv; charset=utf-8"
            return response

        return {"message": "Сессия удалена", "cancelled_reservations": cancelled_reservations}, HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return {"message": f"Ошибка при удалении сессии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
