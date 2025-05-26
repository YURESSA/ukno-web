from datetime import datetime
from http import HTTPStatus

from backend.core import db
from backend.core.models.excursion_models import ExcursionSession
from backend.core.services.utilits import send_email


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
from io import StringIO
import csv

def delete_excursion_session(excursion_id, session_id):
    session = ExcursionSession.query.filter_by(excursion_id=excursion_id, session_id=session_id).first()
    if not session:
        return {"message": "Сессия не найдена"}, HTTPStatus.NOT_FOUND

    # Находим активные (не отменённые) бронирования
    active_reservations = [r for r in session.reservations if not r.is_cancelled]

    if active_reservations:
        # Уведомляем каждого участника
        for res in active_reservations:
            send_email(
                subject="Отмена экскурсионной сессии",
                recipient=res.email,
                body=(
                    f"Здравствуйте, {res.full_name}!\n\n"
                    f"К сожалению, сессия экскурсии (ID {session_id}) была отменена. "
                    "Ваше бронирование аннулировано.\n\n"
                    "Приносим извинения за неудобства."
                )
            )

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Reservation ID', 'Full Name', 'Email', 'Phone Number', 'Participants Count', 'Booked At'])
        for res in active_reservations:
            writer.writerow([
                res.reservation_id,
                res.full_name,
                res.email,
                res.phone_number,
                res.participants_count,
                res.booked_at.strftime("%Y-%m-%d %H:%M")
            ])
        output.seek(0)
        csv_data = output.read()


    try:
        db.session.delete(session)
        db.session.commit()
        return {"message": "Сессия удалена"}, HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return {"message": f"Ошибка при удалении сессии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
