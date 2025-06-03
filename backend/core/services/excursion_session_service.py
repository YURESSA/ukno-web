from datetime import datetime

from flask_jwt_extended import get_jwt_identity

from backend.core import db
from backend.core.models.auth_models import User
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
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    deleter_email = user.email
    session = ExcursionSession.query.filter_by(excursion_id=excursion_id, session_id=session_id).first()
    if not session:
        return {"message": "Сессия не найдена"}, HTTPStatus.NOT_FOUND

    active_reservations = [r for r in session.reservations if not r.is_cancelled]
    excursion_name = session.excursion.title if session.excursion else "экскурсии"
    if active_reservations:
        for res in active_reservations:
            send_email(
                subject="Отмена экскурсионной сессии",
                recipient=res.email,
                body=(
                    f"Здравствуйте, {res.full_name}!\n\n"
                    f"К сожалению, сессия экскурсии «{excursion_name}» (ID {session_id}), "
                    f"которая была запланирована на {session.start_datetime.strftime('%d.%m.%Y %H:%M')}, отменена.\n"
                    "Ваше бронирование было автоматически аннулировано.\n\n"
                    "Приносим искренние извинения за возможные неудобства.\n"
                    "Мы будем рады видеть вас на других наших мероприятиях!"
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
        send_email(
            subject="Список активных резервов после удаления сессии",
            recipient=deleter_email,
            body="В приложении вы найдете CSV-файл с информацией об активных резервированиях на удалённой сессии.",
            attachments=[("active_reservations.csv", csv_data)]
        )

    try:
        db.session.delete(session)
        db.session.commit()
        return {"message": "Сессия удалена"}, HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return {"message": f"Ошибка при удалении сессии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
