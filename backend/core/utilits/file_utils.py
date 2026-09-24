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
from backend.core.storage import delete as delete_from_s3
from backend.core.storage import upload as upload_to_s3
from backend.core.storage import uses_s3


def _unique_upload_path(file: FileStorage, subfolder: str = "") -> tuple[str, str]:
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    filename = f"{name}_{uuid.uuid4().hex}{ext}"
    relative_path = os.path.join('media', 'uploads', subfolder, filename).replace("\\", "/")
    return filename, relative_path


def save_image(file: FileStorage, subfolder: str = "") -> str:
    """
    Сохраняет загруженное изображение в указанную папку проекта и возвращает относительный путь.

    :param file: объект загруженного файла (FileStorage)
    :param subfolder: подкаталог внутри папки загрузок
    :return: относительный путь к сохранённому файлу (например, 'media/uploads/news/filename.png')
    """
    filename, relative_path = _unique_upload_path(file, subfolder)
    if uses_s3():
        upload_to_s3(file.stream, relative_path, file.content_type)
        return relative_path

    folder_path = os.path.join(Config.PROJECT_ROOT, Config.UPLOAD_FOLDER, subfolder)
    os.makedirs(folder_path, exist_ok=True)
    file.save(os.path.join(folder_path, filename))
    return relative_path


def remove_file_if_exists(file_path: str) -> None:
    """
    Удаляет файл, если он существует.

    :param file_path: путь к файлу
    """
    if uses_s3():
        delete_from_s3(file_path)
        return

    absolute_path = file_path
    if not os.path.isabs(absolute_path):
        absolute_path = os.path.join(Config.PROJECT_ROOT, file_path)
    if os.path.exists(absolute_path):
        try:
            os.remove(absolute_path)
        except Exception as e:
            print(f"Ошибка при удалении файла {absolute_path}: {e}")


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


def save_file(file, subfolder: str = "") -> str:
    """
    Сохраняет загруженный файл в указанную папку проекта и возвращает относительный путь.

    :param file: объект загруженного файла (FileStorage)
    :param subfolder: подкаталог внутри папки загрузок
    :return: относительный путь к сохранённому файлу (например, 'media/uploads/requisites/filename.pdf')
    """
    filename, relative_path = _unique_upload_path(file, subfolder)
    if uses_s3():
        upload_to_s3(file.stream, relative_path, file.content_type)
        return relative_path

    folder_path = os.path.join(Config.PROJECT_ROOT, Config.UPLOAD_FOLDER, subfolder)
    os.makedirs(folder_path, exist_ok=True)
    file.save(os.path.join(folder_path, filename))
    return relative_path
