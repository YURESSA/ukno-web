import os
from http import HTTPStatus
from typing import List, Dict, Tuple, Optional, Any, NoReturn

from sqlalchemy import func
from werkzeug.datastructures import FileStorage

from backend.core import db
from backend.core.models.event_models import EventPhoto, Event
from backend.core.utilits.file_utils import save_image, remove_file_if_exists


def process_photos(files: list[FileStorage]) -> list[dict[str, str | int]]:
    """
    Обрабатывает загруженные фото: проверяет тип, размер и сохраняет их.

    :param files: Список файлов (объекты FileStorage)
    :return: Список словарей с относительным путём к файлу и порядковым индексом.
    :raises ValueError: Если файл не является изображением или превышает 5 MB.
    """
    photos: list[dict[str, str | int]] = []
    for idx, file in enumerate(files):
        if not file or not file.filename or not file.content_type:
            continue
        if not file.content_type.startswith("image/"):
            raise ValueError("Файл должен быть изображением")
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > 5 * 1024 * 1024:
            raise ValueError("Размер файла не должен превышать 5 MB")
        rel_path = save_image(file, "excursion_photos")
        photos.append({"photo_url": rel_path, "order_index": idx})
    return photos


def handle_add_photo(excursion_id: int, photo_file) -> tuple[dict, int]:
    """
    Добавляет фото к экскурсии и возвращает актуальный список фото.

    :param excursion_id: ID экскурсии
    :param photo_file: объект загруженного файла (werkzeug.FileStorage)
    :return: Словарь с сообщением и списком фото, HTTP-статус.
             В случае ошибки возвращается словарь с сообщением и статус ошибки.
    """
    photos, error, status = add_photo_to_event(excursion_id, photo_file)
    if error:
        return error, status

    photos, _, status = get_photos_for_event(excursion_id)
    return {"message": "Фото добавлено", "photos": photos}, status


def add_photos(event, photos: List[Dict[str, str | int]]) -> None:
    """
    Добавляет фотографии к указанному событию (экскурсии).

    :param event: Объект события (экскурсии), к которому добавляются фото.
    :param photos: Список словарей с ключами:
                   - "photo_url": относительный путь к изображению
                   - "order_index": порядок отображения (опционально)
    """
    for p in photos:
        db.session.add(EventPhoto(
            event_id=event.event_id,
            photo_url=p["photo_url"],
            order_index=p.get("order_index", 0)
        ))


def delete_photo_from_event(event_id: int, photo_id: int) -> Tuple[Dict[str, str], int]:
    """
    Удаляет фото, связанное с указанной экскурсией (событием).

    :param event_id: ID экскурсии (события)
    :param photo_id: ID фотографии
    :return: Кортеж (словарь с сообщением, HTTP-статус)
    """
    photo = EventPhoto.query.filter_by(event_id=event_id, photo_id=photo_id).first()
    if not photo:
        return {"message": "Фото не найдено"}, HTTPStatus.NOT_FOUND

    try:
        remove_file_if_exists(photo.photo_url)
        db.session.delete(photo)
        db.session.commit()
        return {"message": "Фото удалено"}, HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return {"message": f"Ошибка при удалении фото: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


def get_photos_for_event(event_id: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], int]:
    """
    Получает список фотографий, привязанных к указанной экскурсии.

    :param event_id: ID экскурсии (события)
    :return: Кортеж (список фото или None, словарь ошибки или None, HTTP-статус)
    """
    event = db.session.get(Event, event_id)

    if not event:
        return None, {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND
    photos = [photo.to_dict() for photo in event.photos]
    return photos, None, HTTPStatus.OK


def add_photo_to_event(
        event_id: int,
        photo_file: FileStorage
) -> Tuple[Optional[EventPhoto], Optional[Dict[str, str]], int]:
    """
    Добавляет одно фото к экскурсии.

    :param event_id: ID экскурсии
    :param photo_file: объект загруженного файла (werkzeug.FileStorage)
    :return: Кортеж (объект фото или None, словарь ошибки или None, HTTP-статус)
    """
    if not photo_file:
        return None, {"message": "Фото не загружено"}, HTTPStatus.BAD_REQUEST

    try:
        photos = process_photos([photo_file])
    except ValueError as e:
        return None, {"message": str(e)}, HTTPStatus.BAD_REQUEST

    if not photos:
        return None, {"message": "Недопустимый файл"}, HTTPStatus.BAD_REQUEST

    max_index = db.session.query(
        func.max(EventPhoto.order_index)
    ).filter_by(event_id=event_id).scalar()
    next_index = (max_index or 0) + 1

    new_photo = EventPhoto(
        event_id=event_id,
        photo_url=photos[0]["photo_url"],
        order_index=next_index
    )
    try:
        db.session.add(new_photo)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        remove_file_if_exists(new_photo.photo_url)
        return None, {"message": f"Ошибка при сохранении фото: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
    return new_photo, None, HTTPStatus.CREATED


def clear_photos(event: Event) -> NoReturn:
    """
    Удаляет все фотографии, связанные с экскурсионным событием,
    как из базы данных, так и с файловой системы.

    :param event: Объект экскурсии (Event), для которой нужно очистить фото.
    """
    photos = event.photos[:]
    for photo in photos:
        try:
            remove_file_if_exists(photo.photo_url)
            db.session.delete(photo)
        except Exception:
            pass
    db.session.flush()
