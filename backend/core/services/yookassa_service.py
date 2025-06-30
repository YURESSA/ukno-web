def create_yookassa_payment(amount, email, description, quantity=1, metadata=None, currency='RUB'):
    from yookassa import Payment
    import uuid

    try:
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": currency
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://ваш-сайт/оплата/возврат"
            },
            "capture": True,
            "description": description,
            "receipt": {
                "customer": {
                    "email": email
                },
                "tax_system_code": 1,
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
