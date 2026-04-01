import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Dict

from ics import Calendar, Event
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from backend.core import Config

import boto3
from botocore.client import Config as BotoConfig



s3 = boto3.client(
    "s3",
    endpoint_url=Config.S3_ENDPOINT,
    aws_access_key_id=Config.S3_ACCESS_KEY,
    aws_secret_access_key=Config.S3_SECRET_KEY,
    config=BotoConfig(signature_version="s3v4", s3={"addressing_style": "path"}),
)



def save_file_to_s3(file: FileStorage, subfolder: str = "") -> str:
    """
    Загружает файл в S3 и возвращает путь в виде 'media/uploads/...'.
    """
    original_filename = secure_filename(getattr(file, "filename", "file"))
    name, ext = os.path.splitext(original_filename)
    unique_suffix = uuid.uuid4().hex
    filename = f"{name}_{unique_suffix}{ext}"

    key = f"{subfolder}/{filename}".strip("/")

    # Читаем данные
    if hasattr(file, "read"):
        file_obj = BytesIO(file.read())
    else:
        file_obj = BytesIO(file)
    file_obj.seek(0)

    s3.upload_fileobj(file_obj, Config.BUCKET, key)

    return os.path.join('media', 'uploads', subfolder, filename).replace("\\", "/")


def remove_file_from_s3(relative_path: str) -> None:
    """
    Удаляет файл из S3, если он существует. relative_path — путь вида 'media/uploads/...'
    """
    key = "/".join(relative_path.split("/")[2:])  # удаляем 'media/uploads'
    try:
        s3.delete_object(Bucket=Config.BUCKET, Key=key)
    except Exception as e:
        print(f"Ошибка при удалении файла {key} из S3: {e}")


def save_image(file: FileStorage, subfolder: str = "") -> str:
    return save_file_to_s3(file, subfolder)


def save_file(file: FileStorage, subfolder: str = "") -> str:
    return save_file_to_s3(file, subfolder)


def remove_file_if_exists(file_path: str) -> None:
    remove_file_from_s3(file_path)


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

