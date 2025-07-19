import os
from http import HTTPStatus

from sqlalchemy import func

from backend.core import db
from backend.core.models.excursion_models import ExcursionPhoto, Excursion
from backend.core.services.utilits import save_image, remove_file_if_exists


def process_photos(files):
    photos = []
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


def add_photos(excursion, photos):
    for p in photos:
        db.session.add(ExcursionPhoto(
            excursion_id=excursion.excursion_id,
            photo_url=p["photo_url"],
            order_index=p.get("order_index", 0)
        ))


def delete_photo_from_excursion(excursion_id, photo_id):
    photo = ExcursionPhoto.query.filter_by(excursion_id=excursion_id, photo_id=photo_id).first()
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


def get_photos_for_excursion(excursion_id):
    excursion = db.session.get(Excursion, excursion_id)

    if not excursion:
        return None, {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND
    photos = [photo.to_dict() for photo in excursion.photos]
    return photos, None, HTTPStatus.OK


def add_photo_to_excursion(excursion_id, photo_file):
    if not photo_file:
        return None, {"message": "Фото не загружено"}, HTTPStatus.BAD_REQUEST

    try:
        photos = process_photos([photo_file])
    except ValueError as e:
        return None, {"message": str(e)}, HTTPStatus.BAD_REQUEST

    if not photos:
        return None, {"message": "Недопустимый файл"}, HTTPStatus.BAD_REQUEST

    max_index = db.session.query(
        func.max(ExcursionPhoto.order_index)
    ).filter_by(excursion_id=excursion_id).scalar()
    next_index = (max_index or 0) + 1

    new_photo = ExcursionPhoto(
        excursion_id=excursion_id,
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


def clear_photos(excursion):
    photos = excursion.photos[:]
    for photo in photos:
        try:
            remove_file_if_exists(photo.photo_url)
            db.session.delete(photo)
        except Exception:
            pass
    db.session.flush()
