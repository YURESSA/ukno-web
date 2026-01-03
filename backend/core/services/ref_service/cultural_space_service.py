import os

from backend.core import db
from backend.core.models.ref_models import CulturalSpace
from backend.core.utilits.file_utils import save_image, remove_file_if_exists


def get_all_cultural_spaces():
    return CulturalSpace.query.order_by(CulturalSpace.order_index).all()


def get_cultural_space_by_id(id):
    return db.session.get(CulturalSpace, id)


def create_cultural_space(text: str, photo=None, order_index: int = 0):
    if not text:
        raise ValueError('Поле text обязательно')

    photo_path = None
    if photo:
        if not photo.content_type.startswith("image/"):
            raise ValueError('Файл должен быть изображением')

        photo.seek(0, os.SEEK_END)
        size = photo.tell()
        photo.seek(0)
        if size > 5 * 1024 * 1024:
            raise ValueError('Размер файла не должен превышать 5 MB')

        photo_path = save_image(photo, "cultural_space_photos")

    item = CulturalSpace(text=text, photo=photo_path, order_index=order_index)
    db.session.add(item)
    db.session.commit()
    return item


def update_cultural_space(item: CulturalSpace, text: str, order_index: int = None):
    if not text:
        raise ValueError('Поле text обязательно')
    item.text = text
    if order_index is not None:
        item.order_index = order_index
    db.session.commit()
    return item


def delete_cultural_space(item: CulturalSpace):
    if item.photo:
        remove_file_if_exists(item.photo)
    db.session.delete(item)
    db.session.commit()


def upload_cultural_space_photo(item: CulturalSpace, photo):
    if not photo:
        raise ValueError('Файл не выбран')
    if not photo.content_type.startswith("image/"):
        raise ValueError('Файл должен быть изображением')

    photo.seek(0, os.SEEK_END)
    size = photo.tell()
    photo.seek(0)
    if size > 5 * 1024 * 1024:
        raise ValueError('Размер файла не должен превышать 5 MB')

    if item.photo:
        remove_file_if_exists(item.photo)

    item.photo = save_image(photo, "cultural_space_photos")
    db.session.commit()
    return item.photo


def delete_cultural_space_photo(cultural_space_id: int) -> None:
    item = db.session.get(CulturalSpace, cultural_space_id)
    if not item:
        raise ValueError('Элемент не найден')

    if not item.photo:
        raise ValueError('Фото отсутствует')

    remove_file_if_exists(item.photo)
    item.photo = None
    db.session.commit()
