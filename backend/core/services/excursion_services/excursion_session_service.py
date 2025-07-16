from datetime import datetime
from http import HTTPStatus
from urllib.parse import quote

from flask import make_response
from flask_jwt_extended import get_jwt_identity

from backend.core import db
from backend.core.models.excursion_models import ExcursionSession
from backend.core.services.email_service import send_session_cancellation_email, send_session_deletion_email
from backend.core.services.user_services.auth_service import get_user_by_email
from backend.core.services.utilits import generate_reservations_csv
from backend.core.services.yookassa_service import refund_yookassa_payment


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


def delete_excursion_session(excursion_id, session_id, notify_resident=True):
    email = get_jwt_identity()
    user = get_user_by_email(email)
    deleter_email = user.email
    session = ExcursionSession.query.filter_by(excursion_id=excursion_id, session_id=session_id).first()
    if not session:
        return {"message": "Сессия не найдена"}, HTTPStatus.NOT_FOUND

    active_reservations = [r for r in session.reservations if not r.is_cancelled]
    excursion_name = session.excursion.title if session.excursion else "экскурсии"

    refunded = []

    for res in active_reservations:
        if res.is_paid and res.payment and session.cost > 0 and res.payment.status == "succeeded":
            try:
                refund_yookassa_payment(
                    payment_id=res.payment.payment_id,
                    amount=float(res.payment.amount),
                    currency=res.payment.currency
                )
                refunded.append(res.reservation_id)
            except Exception as e:
                db.session.rollback()
                return {"message": f"Ошибка возврата по брони {res.reservation_id}: {str(e)}"}, HTTPStatus.BAD_REQUEST

        send_session_cancellation_email(reservation=res, excursion_name=excursion_name, session=session)

    cancelled_reservations = [
        res.to_dict()
        for res in active_reservations
    ]

    if notify_resident and cancelled_reservations:
        csv_data = generate_reservations_csv(cancelled_reservations)
    else:
        csv_data = None

    try:
        for res in active_reservations:
            if res.payment:
                db.session.delete(res.payment)

        db.session.delete(session)
        db.session.commit()

        if notify_resident and csv_data:
            send_session_deletion_email(deleter_email, excursion_name, session_id, csv_data)

            response = make_response(csv_data)
            filename = f"отмененные_бронирования_сессия_{session_id}.csv"
            encoded_filename = quote(filename)
            response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
            response.headers["Content-Type"] = "text/csv; charset=utf-8"
            return response

        return {
            "message": "Сессия удалена",
            "cancelled_reservations": cancelled_reservations,
            "refunded": refunded
        }, HTTPStatus.OK

    except Exception as e:
        db.session.rollback()
        return {"message": f"Ошибка при удалении сессии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
