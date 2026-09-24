from http import HTTPStatus

from flask import request
from flask_restx import Resource

from . import webhook_ns
from backend.core import db
from backend.core.models.auth_models import User
from backend.core.models.event_models import Payment, Reservation
from backend.core.models.merch_models import MerchOrder
from backend.core.services.email_service.email_service import send_reservation_confirmation_email


PAYMENT_TYPE_RESERVATION = "reservation"
PAYMENT_TYPE_MERCH_ORDER = "merch_order"


def detect_payment_type(metadata: dict) -> str | None:
    payment_type = metadata.get("type")
    if payment_type:
        return payment_type

    # Fallback for payment links created before explicit metadata type was added.
    if metadata.get("merch_order_id"):
        return PAYMENT_TYPE_MERCH_ORDER
    if metadata.get("reservation_id"):
        return PAYMENT_TYPE_RESERVATION
    return None


def handle_merch_payment_succeeded(metadata: dict) -> None:
    order = MerchOrder.query.get(metadata.get("merch_order_id"))
    if order:
        if order.delivery_method == "delivery":
            order.status = "waiting_shipment"
        else:
            order.status = "paid"
        db.session.commit()


def handle_merch_payment_canceled(metadata: dict) -> None:
    order = MerchOrder.query.get(metadata.get("merch_order_id"))
    if not order:
        return

    if order.status != "payment_canceled":
        for item in order.items:
            if item.variant:
                item.variant.stock += item.quantity
    order.status = "payment_canceled"
    db.session.commit()


def handle_reservation_payment_succeeded(metadata: dict, payment_id: str | None) -> None:
    reservation = Reservation.query.get(metadata.get("reservation_id"))
    if reservation and not reservation.is_paid:
        reservation.is_paid = True
        db.session.commit()
        try:
            user = User.query.get(reservation.user_id)
            send_reservation_confirmation_email(reservation, user)
        except Exception as e:
            print(f"Failed to send reservation confirmation email: {e}")

    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if payment:
        payment.status = "succeeded"
        db.session.commit()


def handle_reservation_payment_canceled(payment_id: str | None) -> None:
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if payment:
        payment.status = "canceled"
        db.session.commit()


def handle_refund_succeeded(object_data: dict) -> None:
    payment = Payment.query.filter_by(payment_id=object_data.get("payment_id")).first()
    if payment:
        payment.status = "refunded"
        db.session.commit()


@webhook_ns.route("/yookassa")
class YooKassaWebhook(Resource):
    def post(self) -> tuple[dict, int]:
        event_data = request.get_json()

        if not event_data or "event" not in event_data:
            return {"message": "Invalid webhook payload"}, HTTPStatus.BAD_REQUEST

        event = event_data["event"]
        object_data = event_data.get("object", {})
        metadata = object_data.get("metadata", {})
        payment_id = object_data.get("id")
        payment_type = detect_payment_type(metadata)

        if event == "payment.succeeded":
            if payment_type == PAYMENT_TYPE_MERCH_ORDER:
                handle_merch_payment_succeeded(metadata)
            elif payment_type == PAYMENT_TYPE_RESERVATION:
                handle_reservation_payment_succeeded(metadata, payment_id)

        elif event == "payment.canceled":
            if payment_type == PAYMENT_TYPE_MERCH_ORDER:
                handle_merch_payment_canceled(metadata)
            elif payment_type == PAYMENT_TYPE_RESERVATION:
                handle_reservation_payment_canceled(payment_id)

        elif event == "refund.succeeded":
            handle_refund_succeeded(object_data)

        return {"message": "Webhook processed"}, HTTPStatus.OK
