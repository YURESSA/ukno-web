import os
import uuid

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from yookassa import Payment, Refund, Configuration
from yookassa.client import ApiClient

session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1.0,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["POST"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)

api_client = ApiClient()
api_client.session = session

Configuration.configure(
    account_id=os.environ.get("ACCOUNT_ID"),
    secret_key=os.environ.get("YOOKASSA_SECRET_KEY"),
    api_client=api_client
)


def create_yookassa_payment(amount, email, description, quantity=1, metadata=None, currency='RUB'):
    try:
        quantity = round(quantity, 2)
        unit_price = round(amount / quantity, 2)

        payment = Payment.create(
            {
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": currency
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://yuressa.uxp.ru/profile"
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


def refund_yookassa_payment(payment_id: str, amount: float, currency: str = "RUB") -> Refund:
    refund = Refund.create({
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
