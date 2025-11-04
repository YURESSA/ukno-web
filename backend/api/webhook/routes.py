from http import HTTPStatus

from flask import request
from flask_restx import Resource

from . import webhook_ns
from backend.core import db
from backend.core.models.auth_models import User
from backend.core.models.event_models import Reservation, Payment
from backend.core.services.email_service.email_service import send_reservation_confirmation_email


@webhook_ns.route('/yookassa')
class YooKassaWebhook(Resource):
    def post(self) -> tuple[dict, int]:
        """
        Обработка вебхука от YooKassa.

        Ожидается JSON следующей структуры:
        {
            "event": "payment.succeeded" | "payment.canceled" | "refund.succeeded",
            "object": {
                "id": "идентификатор платежа",
                "metadata": {
                    "reservation_id": int
                }
            }
        }

        Логика:
        - payment.succeeded: помечает бронь как оплаченной, обновляет статус платежа и отправляет email.
        - payment.canceled: обновляет статус платежа на 'canceled'.
        - refund.succeeded: обновляет статус платежа на 'refunded'.

        Returns:
            dict: сообщение о статусе обработки
            int: HTTP статус код
        """
        event_data = request.get_json()

        if not event_data or 'event' not in event_data:
            return {"message": "Некорректные данные"}, HTTPStatus.BAD_REQUEST

        event = event_data['event']
        object_data = event_data.get('object', {})
        metadata = object_data.get('metadata', {})
        payment_id = object_data.get('id')

        if event == 'payment.succeeded':
            reservation_id = metadata.get('reservation_id')
            reservation = Reservation.query.get(reservation_id)
            if reservation and not reservation.is_paid:
                reservation.is_paid = True
                db.session.commit()
                try:
                    user = User.query.get(reservation.user_id)
                    send_reservation_confirmation_email(reservation, user)
                except Exception as e:
                    print(f"Ошибка при отправке письма: {e}")

            payment = Payment.query.filter_by(payment_id=payment_id).first()
            if payment:
                payment.status = 'succeeded'
                db.session.commit()

        elif event == 'payment.canceled':
            payment = Payment.query.filter_by(payment_id=payment_id).first()
            if payment:
                payment.status = 'canceled'
                db.session.commit()

        elif event == 'refund.succeeded':
            payment_id = object_data.get('payment_id')
            payment = Payment.query.filter_by(payment_id=payment_id).first()
            if payment:
                payment.status = 'refunded'
                db.session.commit()

        return {"message": "Webhook обработан"}, HTTPStatus.OK
