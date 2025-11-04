import os
import re
import threading
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import Type, Any, Optional, List, Union, Tuple, Dict

from flask import current_app, Flask
from flask_mail import Message
from ics import Calendar, Event
from itsdangerous import URLSafeTimedSerializer
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from backend.core import mail
from backend.core.config import Config

UPLOAD_FOLDER = Config.UPLOAD_FOLDER


def save_image(file: FileStorage, subfolder: str = "") -> str:
    """
    Сохраняет загруженное изображение в указанную папку проекта и возвращает относительный путь.

    :param file: объект загруженного файла (FileStorage)
    :param subfolder: подкаталог внутри папки загрузок
    :return: относительный путь к сохранённому файлу (например, 'media/uploads/news/filename.png')
    """
    folder_path = os.path.join(Config.PROJECT_ROOT, Config.UPLOAD_FOLDER, subfolder)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    unique_suffix = uuid.uuid4().hex
    filename = f"{name}_{unique_suffix}{ext}"

    filepath = os.path.join(folder_path, filename)
    file.save(filepath)

    return os.path.join('media/uploads', subfolder, filename).replace("\\", "/")


def get_model_by_name(model: Type[Any], field_name: str, value: Any, error_message: str) -> Any:
    """
    Получает объект модели по значению указанного поля.

    :param model: SQLAlchemy модель
    :param field_name: имя поля модели для фильтра
    :param value: значение для поиска
    :param error_message: сообщение ошибки, если объект не найден
    :return: объект модели
    :raises ValueError: если объект не найден
    """
    instance = model.query.filter(getattr(model, field_name) == value).first()
    if not instance:
        raise ValueError(error_message)
    return instance


def remove_file_if_exists(file_path: str) -> None:
    """
    Удаляет файл, если он существует.

    :param file_path: путь к файлу
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении файла {file_path}: {e}")


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


def generate_reset_token(email: str, expires_sec: int = 3600) -> str:
    """
    Генерирует токен для сброса пароля.

    :param email: email пользователя
    :param expires_sec: срок действия токена в секундах
    :return: токен
    """
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt='password-reset-salt')


def verify_reset_token(token: str, max_age: int = 3600) -> Optional[str]:
    """
    Проверяет токен сброса пароля.

    :param token: токен
    :param max_age: максимальный возраст токена в секундах
    :return: email пользователя если токен валиден, иначе None
    """
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=max_age)
    except Exception:
        return None
    return email


def to_str(value: Union[bytes, str]) -> str:
    """
    Преобразует bytes или любой объект в строку.

    :param value: значение для преобразования
    :return: строковое представление
    """
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return str(value)


def format_datetime(value: datetime) -> str:
    """
    Форматирует datetime в строку "дд.мм.гггг чч:мм".

    :param value: объект datetime
    :return: строковое представление даты и времени
    """
    if isinstance(value, datetime):
        return value.strftime('%d.%m.%Y %H:%M')
    return str(value)


def generate_reservations_csv(reservations: List[Dict]) -> bytes:
    """
    Генерирует Excel-файл с отменёнными бронированиями.

    :param reservations: список словарей с данными бронирований
    :return: байты Excel-файла
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Отменённые бронирования"

    headers = [
        ('reservation_id', 'ID бронирования'),
        ('full_name', 'ФИО'),
        ('email', 'Электронная почта'),
        ('phone_number', 'Телефон'),
        ('participants_count', 'Количество участников'),
        ('booked_at', 'Дата бронирования'),
        ('session_datetime', 'Время сессии'),
        ('excursion_title', 'Название экскурсии'),
        ('place', 'Место экскурсии'),
        ('total_cost', 'Общая стоимость'),
        ('is_paid', 'Оплачена'),
        ('is_cancelled', 'Отменена'),
    ]
    ws.append([h[1] for h in headers])

    for r in reservations:
        ws.append([
            str(r.get('reservation_id', '')),
            str(r.get('full_name', '')),
            str(r.get('email', '')),
            str(r.get('phone_number', '')),
            str(r.get('participants_count', '')),
            format_datetime(r.get('booked_at', '')),
            format_datetime(r.get('session_datetime', '')),
            str(r.get('excursion_title', '')),
            str(r.get('place', '')),
            str(r.get('total_cost', '')),
            'Да' if r.get('is_paid') else 'Нет',
            'Да' if r.get('is_cancelled') else 'Нет',
        ])

    for col_idx, column_cells in enumerate(ws.columns, 1):
        max_length = max((len(str(cell.value)) if cell.value else 0) for cell in column_cells)
        ws.column_dimensions[get_column_letter(col_idx)].width = max_length + 2

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.read()


def create_ical_from_reservation(reservation) -> bytes:
    """
    Создает iCal-файл для бронирования экскурсии.

    :param reservation: объект Reservation с привязанной сессией и мероприятием
    :return: байты iCal-файла
    """
    c = Calendar()
    e = Event()

    e.name = f"Событие: {reservation.session.event.title}"
    e.begin = reservation.session.start_datetime
    duration_minutes = getattr(reservation.session.event, 'duration', 60)
    e.duration = timedelta(minutes=duration_minutes)

    e.location = reservation.session.event.place or ""
    e.description = f"Бронирование экскурсии. Участников: {reservation.participants_count}"

    c.events.add(e)
    return c.serialize().encode('utf-8')
