import json
import os
from http import HTTPStatus

from backend.core import db
from backend.core.models.news_models import NewsImage, News
from backend.core.services.user_services.auth_service import get_user_by_email
from backend.core.services.utilits import save_image, remove_file_if_exists


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
        image_path = save_image(photo_file, "news")
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


def create_news_with_images(user_email, data_str, image_files):
    if not data_str:
        return {"message": "Поле 'data' обязательно"}, HTTPStatus.BAD_REQUEST

    try:
        data = json.loads(data_str)
    except json.JSONDecodeError as e:
        return {"message": f"Ошибка в JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST

    title = data.get("title")
    content = data.get("content")
    if not all([title, content]):
        return {"message": "Поля title и content обязательны"}, HTTPStatus.BAD_REQUEST

    user = get_user_by_email(user_email)
    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

    news = News(
        title=title,
        content=content,
        author_id=user.user_id
    )
    db.session.add(news)
    db.session.flush()

    for image_file in image_files:
        if image_file:
            image_path = save_image(image_file, "news")
            news_image = NewsImage(news_id=news.news_id, image_path=image_path)
            db.session.add(news_image)

    db.session.commit()

    return {
        "message": "Новость успешно создана",
        "news_id": news.news_id
    }, HTTPStatus.CREATED


def get_all_news():
    news_list = News.query.order_by(News.created_at.desc()).all()
    return [n.to_dict() for n in news_list]


def get_news_by_id(news_id):
    return db.session.get(News, news_id)


def update_news(news_id, form_data, files):
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

    if title:
        news.title = title
    if content:
        news.content = content

    images = files.getlist("image") if files else []
    for image_file in images:
        if image_file:
            image_path = save_image(image_file, "news")
            news_image = NewsImage(news_id=news.news_id, image_path=image_path)
            db.session.add(news_image)

    db.session.commit()
    return news, None


def delete_news(news_id):
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
