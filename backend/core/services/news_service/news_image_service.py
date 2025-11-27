import os
from http import HTTPStatus
from typing import Tuple, Optional, List, Dict

from werkzeug.datastructures import FileStorage

from backend.core import db
from backend.core.models.news_models import NewsImage, News
from backend.core.utilits.file_utils import save_image, remove_file_if_exists


def get_photos_for_news(news_id: int) -> Tuple[Optional[List[Dict]], Optional[Dict], HTTPStatus]:
    """
    Получает список фото для новости.

    :param news_id: ID новости
    :return: Кортеж (список фото, ошибка или None, HTTP-статус)
    """
    news = News.query.get(news_id)
    if not news:
        return None, {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
    photos = [{"photo_id": p.id, "image_path": p.image_path} for p in news.images]
    return photos, None, HTTPStatus.OK


def add_photo_to_news(news_id: int, photo_file: FileStorage) -> Tuple[Optional[List[Dict]], Optional[Dict], HTTPStatus]:
    """
    Добавляет фото к новости.

    :param news_id: ID новости
    :param photo_file: Загруженный файл (werkzeug.FileStorage)
    :return: Кортеж (обновленный список фото, ошибка или None, HTTP-статус)
    """
    news = News.query.get(news_id)
    if not news:
        return None, {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
    try:
        image_path = save_image(photo_file, "news")
        photo = NewsImage(news_id=news_id, image_path=image_path)
        db.session.add(photo)
        db.session.commit()
        photos = [{"photo_id": p.id, "image_path": p.image_path} for p in news.images]
        return photos, None, HTTPStatus.CREATED
    except Exception as e:
        return None, {"message": f"Ошибка при добавлении фото: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


def delete_photo_from_news(news_id: int, photo_id: int) -> Tuple[Dict, HTTPStatus]:
    """
    Удаляет фото новости по ID.

    :param news_id: ID новости
    :param photo_id: ID фото
    :return: Словарь с сообщением и HTTP-статус
    """
    photo = NewsImage.query.filter_by(news_id=news_id, id=photo_id).first()
    if not photo:
        return {"message": "Фото не найдено"}, HTTPStatus.NOT_FOUND
    try:
        remove_file_if_exists(photo.image_path)
        db.session.delete(photo)
        db.session.commit()
        return {"message": "Фото удалено"}, HTTPStatus.OK
    except Exception as e:
        return {"message": f"Ошибка при удалении фото: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
