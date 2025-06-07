import os
from http import HTTPStatus

from backend.core import db
from backend.core.models.news_models import NewsImage, News
from backend.core.services.utilits import save_image


def get_photos_for_news(news_id):
    news = News.query.get(news_id)
    if not news:
        return None, {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
    photos = [{"photo_id": p.id, "image_path": p.image_path} for p in news.images]
    return photos, None, HTTPStatus.OK


def add_photo_to_news(news_id, photo_file):
    news = News.query.get(news_id)
    if not news:
        return None, {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
    try:
        image_path = save_image(photo_file, "news")  # твоя функция сохранения файла
        photo = NewsImage(news_id=news_id, image_path=image_path)
        db.session.add(photo)
        db.session.commit()
        photos = [{"photo_id": p.id, "image_path": p.image_path} for p in news.images]
        return photos, None, HTTPStatus.CREATED
    except Exception as e:
        return None, {"message": f"Ошибка при добавлении фото: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR


def delete_photo_from_news(news_id, photo_id):
    photo = NewsImage.query.filter_by(news_id=news_id, id=photo_id).first()
    if not photo:
        return {"message": "Фото не найдено"}, HTTPStatus.NOT_FOUND
    try:
        full_path = os.path.join(os.getcwd(), photo.image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        db.session.delete(photo)
        db.session.commit()
        return {"message": "Фото удалено"}, HTTPStatus.OK
    except Exception as e:
        return {"message": f"Ошибка при удалении фото: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
