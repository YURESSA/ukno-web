from http import HTTPStatus
from typing import Tuple, Dict, Any

from datetime import datetime

from sqlalchemy import func, select

from backend.core import db
from backend.core.models.event_models import EventSession, Reservation, Payment
from backend.core.services.email_service.email_service import send_reservation_confirmation_email, \
    send_reservation_cancellation_email
from backend.core.services.reservation_service.yookassa_service import create_yookassa_payment, refund_yookassa_payment
from backend.core.services.user_services.user_service import get_user_by_email


def create_reservation_with_payment(
        user_email: str,
        session_id: int,
        full_name: str,
        phone_number: str,
        email: str,
        participants_count: int
) -> Tuple[Dict[str, Any], HTTPStatus]:
    """
    Создает бронирование для указанного сеанса с обработкой оплаты через YooKassa.

    Если стоимость сеанса равна 0, бронирование считается оплаченным автоматически.

    :param user_email: email пользователя, создающего бронь
    :param session_id: ID сеанса экскурсии
    :param full_name: имя участника
    :param phone_number: телефон участника
    :param email: email участника
    :param participants_count: количество участников
    :return: кортеж (ответ в виде словаря, HTTP статус)
    """
    user = get_user_by_email(user_email)
    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED

    if not session_id:
        return {"message": "session_id is required"}, HTTPStatus.BAD_REQUEST

    if isinstance(participants_count, bool) or not isinstance(participants_count, int) or participants_count < 1:
        return {"message": "Количество участников должно быть положительным целым числом"}, HTTPStatus.BAD_REQUEST

    try:
        # A row lock serializes every capacity check for this session in PostgreSQL.
        # Unpaid reservations are counted as short-lived holds and are removed by
        # cleanup_unpaid_reservations after 15 minutes.
        session = db.session.execute(
            select(EventSession)
            .where(EventSession.session_id == session_id)
            .with_for_update()
        ).scalar_one_or_none()
        if not session:
            db.session.rollback()
            return {"message": "Сеанс не найден"}, HTTPStatus.NOT_FOUND
        if not session.event or not session.event.is_active:
            db.session.rollback()
            return {"message": "Событие недоступно для бронирования"}, HTTPStatus.BAD_REQUEST
        if session.start_datetime <= datetime.now():
            db.session.rollback()
            return {"message": "Нельзя забронировать прошедший сеанс"}, HTTPStatus.BAD_REQUEST

        duplicate = Reservation.query.filter_by(
            session_id=session_id,
            user_id=user.user_id,
            is_cancelled=False,
        ).first()
        if duplicate:
            db.session.rollback()
            return {"message": "У вас уже есть активное бронирование на этот сеанс"}, HTTPStatus.CONFLICT

        held_participants = db.session.query(
            func.coalesce(func.sum(Reservation.participants_count), 0)
        ).filter_by(session_id=session_id, is_cancelled=False).scalar()

        if held_participants + participants_count > session.max_participants:
            db.session.rollback()
            return {"message": "Недостаточно свободных мест"}, HTTPStatus.CONFLICT

        amount = session.cost * participants_count
        reservation = Reservation(
            session_id=session_id,
            user_id=user.user_id,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            participants_count=participants_count,
            is_paid=amount == 0,
            is_cancelled=False
        )
        db.session.add(reservation)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    if amount == 0:
        try:
            send_reservation_confirmation_email(reservation, user)
        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")

        return {
            "message": "Бронирование успешно создано (бесплатно)",
            "reservation_id": reservation.reservation_id,
        }, HTTPStatus.CREATED

    try:
        payment_response = create_yookassa_payment(
            amount=amount,
            email=user_email,
            description=f"Оплата экскурсии «{session.event.title}» на {session.start_datetime}",
            quantity=participants_count,
            metadata={
                "type": "reservation",
                "reservation_id": reservation.reservation_id,
                "session_id": session_id,
                "email": user_email
            }
        )
    except Exception:
        # Do not leave a capacity hold behind when the payment provider could
        # not create a payment at all.
        stale_reservation = db.session.get(Reservation, reservation.reservation_id)
        if stale_reservation:
            db.session.delete(stale_reservation)
            db.session.commit()
        return {"message": "Не удалось создать платёж"}, HTTPStatus.BAD_GATEWAY

    payment = Payment(
        payment_id=payment_response.id,
        session_id=session_id,
        reservation_id=reservation.reservation_id,
        participants_count=participants_count,
        email=user_email,
        amount=amount,
        currency='RUB',
        status=payment_response.status,
        method=payment_response.payment_method.type
    )
    db.session.add(payment)
    db.session.commit()

    return {
        "message": "Перейдите по ссылке для оплаты",
        "payment_id": payment.payment_id,
        "payment_url": payment_response.confirmation.confirmation_url
    }, HTTPStatus.CREATED


def delete_reservation_with_refund(reservation_id: int) -> Tuple[bool, str, int]:
    """
    Удаляет бронирование и при необходимости выполняет возврат средств через YooKassa.

    :param reservation_id: ID бронирования для удаления
    :return: Кортеж (успех: bool, сообщение: str, HTTP-статус: int)
    """
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return False, 'Бронь не найдена', 404

    user = reservation.user

    if reservation.is_paid and reservation.payment:
        try:
            refund = refund_yookassa_payment(
                payment_id=reservation.payment.payment_id,
                amount=reservation.payment.amount,
                currency="RUB"
            )
            if refund.status != "succeeded":
                return False, f"Не удалось вернуть средства, статус возврата: {refund.status}", 400

        except Exception as e:
            return False, f"Ошибка при попытке возврата средств: {str(e)}", 500

    try:
        send_reservation_cancellation_email(user, reservation)
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

    try:
        db.session.delete(reservation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return False, f"Ошибка при удалении брони: {str(e)}", 500

    return True, "Бронирование успешно удалено", 200
