from flask import request
from flask_restx import Resource
from http import HTTPStatus

from . import webhook_ns
from ..core import db
from ..core.models.excursion_models import Reservation, Payment


@webhook_ns.route('/yookassa')
class YooKassaWebhook(Resource):
    def post(self):
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
