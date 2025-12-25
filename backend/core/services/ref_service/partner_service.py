import os

from backend.core import db
from backend.core.models.ref_models import Partner
from backend.core.utilits.file_utils import save_image, remove_file_if_exists


def get_all_partners():
    return Partner.query.order_by(Partner.order_index).all()


def create_partner(name: str, link: str = None, photo=None, order_index: int = 0):
    if not name:
        raise ValueError('Поле name обязательно')

    photo_path = None
    if photo:
        if not photo.content_type.startswith("image/"):
            raise ValueError('Файл должен быть изображением')

        photo.seek(0, os.SEEK_END)
        size = photo.tell()
        photo.seek(0)
        if size > 5 * 1024 * 1024:
            raise ValueError('Размер файла не должен превышать 5 MB')

        photo_path = save_image(photo, "partner_photos")

    item = Partner(
        name=name,
        link=link,
        photo=photo_path,
        order_index=order_index
    )
    db.session.add(item)
    db.session.commit()
    return item


def update_partner(item: Partner, name: str, link: str = None, order_index: int = None):
    if not name:
        raise ValueError('Поле name обязательно')

    item.name = name
    item.link = link

    if order_index is not None:
        item.order_index = order_index

    db.session.commit()
    return item


def delete_partner(item: Partner):
    if item.photo:
        remove_file_if_exists(item.photo)
    db.session.delete(item)
    db.session.commit()


def upload_partner_photo(item: Partner, photo):
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

    item.photo = save_image(photo, "partner_photos")
    db.session.commit()
    return item.photo
