import re
import threading
from io import BytesIO
from typing import Optional, List, Union, Tuple

from flask import Flask, current_app
from flask_mail import Message

from backend.core import mail


def is_valid_email(email: str) -> bool:
    """
    Проверяет, соответствует ли строка формату email.

    :param email: строка с email
    :return: True, если валидный email, иначе False
    """
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def send_async_email(app: Flask, msg: Message) -> None:
    """
    Отправляет email в асинхронном контексте Flask.

    :param app: экземпляр Flask
    :param msg: объект Message Flask-Mail
    """
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Ошибка при отправке email: {e}")


def send_email(
        subject: str,
        recipient: str,
        body: str,
        body_html: Optional[str] = None,
        attachments: Optional[List[Union[Tuple[str, bytes, str], Tuple[str, bytes]]]] = None
) -> None:
    """
    Отправляет email в отдельном потоке с возможностью вложений.

    :param subject: тема письма
    :param recipient: email получателя
    :param body: текст письма
    :param body_html: HTML-содержимое письма (опционально)
    :param attachments: список вложений. Каждый элемент:
                        - (filename, content_bytes, mimetype)
                        - или (filename, content_bytes) с типом по умолчанию "text/csv; charset=utf-8"
    """
    if not recipient or not is_valid_email(recipient):
        print(f"Попытка отправить email на невалидный адрес: {recipient}")
        return

    msg = Message(
        subject=subject,
        recipients=[recipient],
        body=body,
        html=body_html
    )

    if attachments:
        for attachment in attachments:
            if isinstance(attachment, tuple) and len(attachment) == 3:
                filename, content_bytes, mimetype = attachment
                data = BytesIO(content_bytes)
                msg.attach(filename, mimetype, data.read())
            elif isinstance(attachment, tuple) and len(attachment) == 2:
                filename, content_bytes = attachment
                data = BytesIO(content_bytes)
                msg.attach(filename, "text/csv; charset=utf-8", data.read())
            else:
                print(f"Некорректный формат вложения: {attachment}")

    threading.Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
