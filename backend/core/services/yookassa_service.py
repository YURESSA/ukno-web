import uuid

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from yookassa import Payment
from yookassa.client import ApiClient

session = requests.Session()
retries = Retry(
    total=3,  # Максимум 3 попытки
    backoff_factor=1.0,  # Задержка: 1s, 2s, 4s
    status_forcelist=[500, 502, 503, 504],  # При каких статусах повторять
    allowed_methods=["POST"]  # Повтор только на POST-запросах
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)

api_client = ApiClient()
api_client.session = session


def create_yookassa_payment(amount, email, description, quantity=1, metadata=None, currency='RUB'):
    try:
        payment = Payment.create({
            "amount": {
                "value": str(amount),
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
                        "quantity": f"{quantity:.2f}",
                        "amount": {
                            "value": f"{amount / quantity:.2f}",
                            "currency": currency
                        },
                        "vat_code": 1
                    }
                ]
            },
            "metadata": metadata or {},
            "payment_method_data": {
                "type": "bank_card"
            }
        }, uuid.uuid4())
        print(payment)
        return payment

    except Exception as e:
        print(f"Ошибка создания платежа YooKassa: {e}")
        raise e


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
