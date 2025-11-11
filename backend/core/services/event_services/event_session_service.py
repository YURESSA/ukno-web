from datetime import datetime
from http import HTTPStatus
from typing import List, Dict, Tuple, Optional, Union
from urllib.parse import quote

from flask import make_response, Response
from flask_jwt_extended import get_jwt_identity

from backend.core import db
from backend.core.models.event_models import EventSession, Event
from backend.core.services.email_service.email_service import send_session_deletion_email, \
    send_session_cancellation_email

from backend.core.services.user_services.user_service import get_user_by_email
from backend.core.utilits.file_utils import generate_reservations_csv
from backend.core.services.reservation_service.yookassa_service import refund_yookassa_payment


def clear_sessions_and_schedules(event: Event) -> None:
    """
    Удаляет все сессии и связанные расписания для заданной экскурсии.

    :param event: объект Event, для которого очищаются сессии
    :return: None
    """
    EventSession.query.filter_by(event_id=event.event_id).delete()


def add_sessions(event: Event, sessions: List[Dict]) -> None:
    """
    Добавляет новые сессии к экскурсии.

    :param event: объект Event, к которому добавляются сессии
    :param sessions: список словарей с данными сессий, каждый словарь должен содержать:
                     - start_datetime (str, ISO-формат)
                     - max_participants (int)
                     - cost (float)
    :return: None
    """
    for s in sessions:
        start_dt = datetime.fromisoformat(s["start_datetime"])
        db.session.add(EventSession(
            event_id=event.event_id,
            start_datetime=start_dt,
            max_participants=s["max_participants"],
            cost=s["cost"]
        ))


def get_sessions_for_event(event_id: int) -> List[EventSession]:
    """
    Получает все сессии для конкретной экскурсии.

    :param event_id: ID экскурсии
    :return: Список объектов EventSession
    """
    return EventSession.query.filter_by(event_id=event_id).all()


def create_event_session(event_id: int, data: dict) -> Tuple[Optional[EventSession], Optional[dict], int]:
    """
    Создает новую сессию для экскурсии.

    :param event_id: ID экскурсии
    :param data: Словарь с данными сессии, ожидается ключ 'start_datetime' в ISO формате,
                 а также необязательные 'max_participants' и 'cost'.
    :return: Кортеж (созданный объект EventSession | None, словарь с сообщением об ошибке | None, HTTPStatus)
    """
    try:
        start_dt = datetime.fromisoformat(data['start_datetime'])
    except (KeyError, ValueError):
        return None, {"message": "Неверный или отсутствует start_datetime"}, HTTPStatus.BAD_REQUEST

    new_session = EventSession(
        event_id=event_id,
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


def update_event_session(
        event_id: int,
        session_id: int,
        data: dict
) -> Tuple[Optional[EventSession], Optional[dict], int]:
    """
    Обновляет данные конкретной сессии экскурсии.

    :param event_id: ID экскурсии
    :param session_id: ID сессии
    :param data: Словарь с обновляемыми данными. Возможные ключи:
                 'start_datetime' (ISO формат), 'max_participants', 'cost'.
    :return: Кортеж (обновленный объект EventSession | None, словарь с ошибкой | None, HTTPStatus)
    """
    session = EventSession.query.filter_by(event_id=event_id, session_id=session_id).first()
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


def delete_event_session(
        event_id: int,
        session_id: int,
        notify_resident: bool = True
) -> Union[Tuple[dict, int], 'Response']:
    """
    Удаляет конкретную сессию экскурсии, отменяет активные бронирования и при необходимости отправляет уведомления.

    :param event_id: ID экскурсии
    :param session_id: ID сессии
    :param notify_resident: Отправлять ли CSV уведомление о отмене бронирований резиденту
    :return: Либо словарь с результатом и HTTPStatus, либо Flask Response с CSV.
    """
    email = get_jwt_identity()
    user = get_user_by_email(email)
    deleter_email = user.email
    session = EventSession.query.filter_by(event_id=event_id, session_id=session_id).first()
    if not session:
        return {"message": "Сессия не найдена"}, HTTPStatus.NOT_FOUND

    active_reservations = [r for r in session.reservations if not r.is_cancelled]
    event_name = session.event.title if session.event else "экскурсии"

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

        send_session_cancellation_email(reservation=res, event_name=event_name, session=session)

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
            send_session_deletion_email(deleter_email, event_name, session_id, csv_data)

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
