from http import HTTPStatus

from flask import request
from flask_restx import Resource

from . import webhook_ns
from backend.core import db
from backend.core.models.auth_models import User
from backend.core.models.event_models import Payment, Reservation
from backend.core.models.merch_models import MerchOrder
from backend.core.services.email_service.email_service import send_reservation_confirmation_email
from backend.core.services.reservation_service.yookassa_service import (
    get_yookassa_payment,
    get_yookassa_refund,
)


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


def _object_value(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _metadata_dict(obj) -> dict:
    metadata = _object_value(obj, "metadata", {}) or {}
    if isinstance(metadata, dict):
        return metadata
    try:
        return dict(metadata)
    except (TypeError, ValueError):
        return {}


def handle_merch_payment_succeeded(metadata: dict, payment_id: str) -> None:
    order = MerchOrder.query.get(metadata.get("merch_order_id"))
    if order and order.payment_id == payment_id:
        if order.delivery_method == "delivery":
            order.status = "waiting_shipment"
        else:
            order.status = "paid"
        db.session.commit()


def handle_merch_payment_canceled(metadata: dict, payment_id: str) -> None:
    order = MerchOrder.query.get(metadata.get("merch_order_id"))
    if not order or order.payment_id != payment_id:
        return

    if order.status != "payment_canceled":
        for item in order.items:
            if item.variant:
                item.variant.stock += item.quantity
    order.status = "payment_canceled"
    db.session.commit()


def handle_reservation_payment_succeeded(metadata: dict, payment_id: str | None) -> None:
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if not payment or not payment.reservation_id:
        return
    if metadata.get("reservation_id") and str(metadata.get("reservation_id")) != str(payment.reservation_id):
        return

    reservation = db.session.get(Reservation, payment.reservation_id)
    if reservation and not reservation.is_paid:
        reservation.is_paid = True
        db.session.commit()
        try:
            user = User.query.get(reservation.user_id)
            send_reservation_confirmation_email(reservation, user)
        except Exception as e:
            print(f"Failed to send reservation confirmation email: {e}")

    payment.status = "succeeded"
    db.session.commit()


def handle_reservation_payment_canceled(payment_id: str | None) -> None:
    payment = Payment.query.filter_by(payment_id=payment_id).first()
    if payment:
        payment.status = "canceled"
        if payment.reservation and not payment.reservation.is_paid:
            payment.reservation.is_cancelled = True
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

        if not event_data or event_data.get("type") != "notification" or "event" not in event_data:
            return {"message": "Invalid webhook payload"}, HTTPStatus.BAD_REQUEST

        event = event_data["event"]
        object_data = event_data.get("object", {})
        payment_id = object_data.get("id")

        if event in ("payment.succeeded", "payment.canceled"):
            if not payment_id:
                return {"message": "Missing payment id"}, HTTPStatus.BAD_REQUEST
            try:
                trusted_payment = get_yookassa_payment(payment_id)
            except Exception:
                # A non-2xx response asks YooKassa to retry the notification.
                return {"message": "Could not verify payment"}, HTTPStatus.SERVICE_UNAVAILABLE

            expected_status = "succeeded" if event == "payment.succeeded" else "canceled"
            if (_object_value(trusted_payment, "id") != payment_id
                    or _object_value(trusted_payment, "status") != expected_status):
                return {"message": "Payment status verification failed"}, HTTPStatus.BAD_REQUEST

            metadata = _metadata_dict(trusted_payment)
            payment_type = detect_payment_type(metadata)

        if event == "payment.succeeded":
            if payment_type == PAYMENT_TYPE_MERCH_ORDER:
                handle_merch_payment_succeeded(metadata, payment_id)
            elif payment_type == PAYMENT_TYPE_RESERVATION:
                handle_reservation_payment_succeeded(metadata, payment_id)

        elif event == "payment.canceled":
            if payment_type == PAYMENT_TYPE_MERCH_ORDER:
                handle_merch_payment_canceled(metadata, payment_id)
            elif payment_type == PAYMENT_TYPE_RESERVATION:
                handle_reservation_payment_canceled(payment_id)

        elif event == "refund.succeeded":
            refund_id = object_data.get("id")
            if not refund_id:
                return {"message": "Missing refund id"}, HTTPStatus.BAD_REQUEST
            try:
                trusted_refund = get_yookassa_refund(refund_id)
            except Exception:
                return {"message": "Could not verify refund"}, HTTPStatus.SERVICE_UNAVAILABLE
            if (_object_value(trusted_refund, "id") != refund_id
                    or _object_value(trusted_refund, "status") != "succeeded"):
                return {"message": "Refund status verification failed"}, HTTPStatus.BAD_REQUEST
            handle_refund_succeeded({
                "payment_id": _object_value(trusted_refund, "payment_id")
            })

        return {"message": "Webhook processed"}, HTTPStatus.OK
