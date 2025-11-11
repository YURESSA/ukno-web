from http import HTTPStatus
from typing import Tuple, Dict, Any

from backend.core import db
from backend.core.models.event_models import Reservation
from backend.core.services.email_service.email_service import send_reservation_refund_email
from backend.core.services.reservation_service.yookassa_service import refund_yookassa_payment
from backend.core.services.user_services.user_service import get_user_by_email


def cancel_user_reservation(user_email: str, reservation_id: int) -> Tuple[Dict[str, Any], HTTPStatus]:
    """
    Отменяет бронирование пользователя и при необходимости выполняет возврат средств через YooKassa.

    :param user_email: Email пользователя, который хочет отменить бронь
    :param reservation_id: ID бронирования
    :return: Словарь с результатом и HTTP-статус
    """
    user = get_user_by_email(user_email)
    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED

    if not reservation_id:
        return {"message": "reservation_id is required"}, HTTPStatus.BAD_REQUEST

    reservation = db.session.get(Reservation, reservation_id)
    if not reservation or reservation.user_id != user.user_id:
        return {"message": "Бронирование не найдено или не принадлежит вам"}, HTTPStatus.NOT_FOUND

    if reservation.is_cancelled:
        return {"message": "Бронирование уже отменено"}, HTTPStatus.BAD_REQUEST

    refund_done = False
    if reservation.is_paid:
        if reservation.payment:
            try:
                refund_yookassa_payment(reservation.payment.payment_id, float(reservation.payment.amount))
                refund_done = True
            except Exception as e:
                print(f"Ошибка возврата средств YooKassa: {e}")
                return {"message": "Не удалось сделать возврат средств"}, HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            refund_done = False

    reservation.is_cancelled = True
    db.session.commit()

    try:
        send_reservation_refund_email(reservation)
    except Exception as e:
        print(f"Ошибка отправки email: {e}")

    if refund_done:
        return {"message": "Бронирование отменено, средства возвращены"}, HTTPStatus.OK
    else:
        return {"message": "Бронирование отменено"}, HTTPStatus.OK
