from http import HTTPStatus

from sqlalchemy import func

from backend.core import db
from backend.core.models.excursion_models import Reservation, ExcursionSession, Payment
from backend.core.services.email_service import send_reservation_confirmation_email, send_reservation_refund_email, \
    send_reservation_cancellation_email
from backend.core.services.user_services.auth_service import get_user_by_email
from backend.core.services.yookassa_service import create_yookassa_payment, refund_yookassa_payment


def get_reservations_by_user_email(email: str):
    user = get_user_by_email(email)
    if not user:
        return None, None  #

    reservations = Reservation.query.filter_by(user_id=user.user_id).all()
    return reservations, user


def create_reservation_with_payment(user_email, session_id, full_name, phone_number, email, participants_count):
    user = get_user_by_email(user_email)
    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED

    if not session_id:
        return {"message": "session_id is required"}, HTTPStatus.BAD_REQUEST

    session = ExcursionSession.query.get(session_id)
    if not session:
        return {"message": "Сеанс не найден"}, HTTPStatus.NOT_FOUND

    existing_participants = db.session.query(
        func.coalesce(func.sum(Reservation.participants_count), 0)
    ).filter_by(session_id=session_id, is_cancelled=False, is_paid=True).scalar()

    if existing_participants + participants_count > session.max_participants:
        return {"message": "Недостаточно свободных мест"}, HTTPStatus.BAD_REQUEST

    amount = session.cost * participants_count

    # Бесплатная бронь
    if amount == 0:
        reservation = Reservation(
            session_id=session_id,
            user_id=user.user_id,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            participants_count=participants_count,
            is_paid=True,
            is_cancelled=False
        )
        db.session.add(reservation)
        db.session.commit()

        try:
            send_reservation_confirmation_email(reservation, user)
        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")

        return {
            "message": "Бронирование успешно создано (бесплатно)",
            "reservation_id": reservation.reservation_id,
        }, HTTPStatus.CREATED

    # Платная бронь (is_paid=False, создаём платёж)
    reservation = Reservation(
        session_id=session_id,
        user_id=user.user_id,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        participants_count=participants_count,
        is_paid=False,
        is_cancelled=False
    )
    db.session.add(reservation)
    db.session.commit()

    payment_response = create_yookassa_payment(
        amount=amount,
        email=user_email,
        description=f"Оплата экскурсии «{session.excursion.title}» на {session.start_datetime}",
        quantity=participants_count,
        metadata={
            "reservation_id": reservation.reservation_id,
            "session_id": session_id,
            "email": user_email
        }
    )

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


def cancel_user_reservation(user_email, reservation_id):
    user = get_user_by_email(user_email)
    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED

    if not reservation_id:
        return {"message": "reservation_id is required"}, HTTPStatus.BAD_REQUEST

    reservation = Reservation.query.get(reservation_id)
    if not reservation or reservation.user_id != user.user_id:
        return {"message": "Бронирование не найдено или не принадлежит вам"}, HTTPStatus.NOT_FOUND

    if reservation.is_cancelled:
        return {"message": "Бронирование уже отменено"}, HTTPStatus.BAD_REQUEST

    if reservation.is_paid:
        if not reservation.payment:
            return {"message": "Платеж для бронирования не найден"}, HTTPStatus.INTERNAL_SERVER_ERROR

        try:
            refund_yookassa_payment(reservation.payment.payment_id, float(reservation.payment.amount))
        except Exception as e:
            print(f"Ошибка возврата средств YooKassa: {e}")
            return {"message": "Не удалось сделать возврат средств"}, HTTPStatus.INTERNAL_SERVER_ERROR

    reservation.is_cancelled = True
    db.session.commit()

    try:
        send_reservation_refund_email(reservation)
    except Exception as e:
        print(f"Ошибка отправки email: {e}")

    return {"message": "Бронирование отменено, средства возвращены"}, HTTPStatus.OK

def delete_reservation_with_refund(reservation_id):
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

def get_all_reservations():
    reservations = Reservation.query.all()
    return [r.to_dict() for r in reservations]


def get_reservation_by_id(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return None
    return reservation.to_dict_detailed()
