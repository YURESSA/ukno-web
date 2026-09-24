import os
import uuid

import requests
from yookassa import Payment as YooKassaPayment, Refund as YooKassaRefund, Configuration

from backend.core.config import Config


def _configure_yookassa() -> None:
    """Configure the SDK lazily so importing the app never requires live secrets."""
    account_id = os.environ.get("ACCOUNT_ID")
    secret_key = os.environ.get("YOOKASSA_SECRET_KEY")
    if not account_id or not secret_key:
        raise RuntimeError("YooKassa credentials are not configured")
    Configuration.configure(
        account_id=account_id,
        secret_key=secret_key,
        max_attempts=3,
    )


def create_yookassa_payment(amount, email, description, quantity=1, metadata=None, currency='RUB'):
    try:
        _configure_yookassa()
        quantity = round(quantity, 2)
        unit_price = round(amount / quantity, 2)

        payment = YooKassaPayment.create(
            {
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": currency
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": Config.YOOKASSA_REDIRECT_URI
                },
                "capture": True,
                "description": description,
                "receipt": {
                    "customer": {
                        "email": email
                    },
                    "items": [
                        {
                            "description": description,
                            "quantity": quantity,
                            "amount": {
                                "value": f"{unit_price:.2f}",
                                "currency": currency
                            },
                            "vat_code": 1,
                            "payment_subject": "service",
                            "payment_mode": "full_payment"
                        }
                    ]
                },
                "metadata": metadata or {},
                "payment_method_data": {
                    "type": "bank_card"
                }
            }
        )

        print(f"[OK] Создан платёж {payment.id}")
        return payment

    except requests.exceptions.RequestException as e:
        print(f"[Ошибка сети] Не удалось соединиться с YooKassa: {e}")
        raise
    except Exception as e:
        print(f"[Ошибка API] Ошибка при создании платежа: {e}")
        raise


def get_yookassa_payment(payment_id: str):
    """Fetch the authoritative payment state before trusting a webhook."""
    _configure_yookassa()
    return YooKassaPayment.find_one(payment_id)


def get_yookassa_refund(refund_id: str):
    """Fetch the authoritative refund state before trusting a webhook."""
    _configure_yookassa()
    return YooKassaRefund.find_one(refund_id)


def refund_yookassa_payment(payment_id: str, amount: float, currency: str = "RUB") -> YooKassaRefund:
    _configure_yookassa()
    refund = YooKassaRefund.create({
        "payment_id": payment_id,
        "amount": {
            "value": f"{amount:.2f}",
            "currency": currency
        },
        "comment": "Возврат за отменённое бронирование"
    }, uuid.uuid4())
    return refund

# def refund_yookassa_payment(payment_id, amount, receipt, currency="RUB"):
#     refund = Refund.create({
#         "payment_id": payment_id,
#         "amount": {
#             "value": f"{amount:.2f}",
#             "currency": currency
#         },
#         "receipt": receipt,  # чек обязателен, если был в платеже
#         "comment": "Полный возврат за отменённое бронирование"
#     }, uuid.uuid4())
#     return refund
