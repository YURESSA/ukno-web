import json
import os
from http import HTTPStatus
from typing import Tuple, Optional, List, Dict

from werkzeug.datastructures import FileStorage

from backend.core import db
from backend.core.models.news_models import NewsImage, News
from backend.core.services.user_services.user_service import get_user_by_email
from backend.core.utilits.file_utils import save_image, remove_file_if_exists


def create_news_with_images(user_email: str, data_str: str, image_files: List[FileStorage]) -> Tuple[Dict, HTTPStatus]:
    """
    Создает новость с прикрепленными фото.

    :param user_email: Email автора новости
    :param data_str: JSON-строка с данными новости (title, content, photo_author)
    :param image_files: Список файлов изображений
    :return: Словарь с сообщением, ID новости и HTTP-статус
    """
    if not data_str:
        return {"message": "Поле 'data' обязательно"}, HTTPStatus.BAD_REQUEST

    try:
        data = json.loads(data_str)
    except json.JSONDecodeError as e:
        return {"message": f"Ошибка в JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST

    title = data.get("title")
    content = data.get("content")
    photo_author = data.get("photo_author")
    if not all([title, content]):
        return {"message": "Поля title и content обязательны"}, HTTPStatus.BAD_REQUEST

    user = get_user_by_email(user_email)
    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

    news = News(
        title=title,
        content=content,
        author_id=user.user_id,
        photo_author=photo_author
    )
    db.session.add(news)
    db.session.flush()

    for image_file in image_files:
        print(1)
        if image_file:
            image_path = save_image(image_file, "news")
            news_image = NewsImage(news_id=news.news_id, image_path=image_path)
            db.session.add(news_image)

    db.session.commit()

    return {
        "message": "Новость успешно создана",
        "news_id": news.news_id
    }, HTTPStatus.CREATED


def get_all_news() -> List[Dict]:
    """
    Получает все новости в порядке убывания даты создания.

    :return: Список словарей с новостями
    """
    news_list = News.query.order_by(News.created_at.desc()).all()
    return [n.to_dict() for n in news_list]


def get_news_by_id(news_id: int) -> Optional[News]:
    """Получает новость по ID."""
    return db.session.get(News, news_id)


def update_news(news_id: int, form_data: dict, files: Optional[dict] = None) -> Tuple[Optional[News], Optional[str]]:
    """
    Обновляет новость и добавляет новые изображения.

    :param news_id: ID новости
    :param form_data: словарь с полем 'data', содержащим JSON с title, content, photo_author
    :param files: словарь с ключом 'image', содержащий список файлов
    :return: кортеж (объект новости или None, сообщение об ошибке или None)
    """
    news = db.session.get(News, news_id)
    if not news:
        return None, "Новость не найдена"

    if 'data' not in form_data:
        return None, "Поле 'data' обязательно"

    try:
        data = json.loads(form_data['data'])
    except json.JSONDecodeError as e:
        return None, f"Ошибка в JSON: {str(e)}"

    title = data.get("title")
    content = data.get("content")
    photo_author = data.get("photo_author")

    if title:
        news.title = title
    if content:
        news.content = content
    if photo_author is not None:
        news.photo_author = photo_author

    images = files.getlist("image") if files else []
    for image_file in images:
        if image_file:
            image_path = save_image(image_file, "news")
            news_image = NewsImage(news_id=news.news_id, image_path=image_path)
            db.session.add(news_image)

    db.session.commit()
    return news, None


def delete_news(news_id: int) -> Tuple[bool, Optional[str]]:
    """
    Удаляет новость и связанные с ней изображения.

    :param news_id: ID новости
    :return: кортеж (успех: bool, сообщение об ошибке или None)
    """
    news = db.session.get(News, news_id)
    if not news:
        return False, "Новость не найдена"

    for image in news.images:
        image_path = os.path.join(os.getcwd(), image.image_path)
        remove_file_if_exists(image_path)

    for image in news.images:
        db.session.delete(image)

    db.session.delete(news)
    db.session.commit()

    return True, None
