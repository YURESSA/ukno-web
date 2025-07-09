import uuid

from yookassa import Refund, Payment


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
        return payment

    except Exception as e:
        print(f"Ошибка создания платежа YooKassa: {e}")
        raise e


# def refund_yookassa_payment(payment_id: str, amount: float, currency: str = "RUB") -> Refund:
#     refund = Refund.create({
#         "payment_id": payment_id,
#         "amount": {
#             "value": f"{amount:.2f}",
#             "currency": currency
#         },
#         "comment": "Возврат за отменённое бронирование",
#         "receipt": {
#             "items": [
#                 {
#                     "description": "Билет на экскурсию",
#                     "quantity": 1,
#                     "amount": {
#                         "value": f"{amount:.2f}",
#                         "currency": currency
#                     },
#                     "vat_code": 1  # 1 = без НДС (наиболее часто)
#                 }
#             ]
#         }
#     }, uuid.uuid4())
#     return refund


def refund_yookassa_payment(payment_id, amount, currency="RUB"):
    refund = Refund.create({
        "payment_id": payment_id,
        "comment": "Полный возврат за отменённое бронирование"
    }, uuid.uuid4())
    return refund
