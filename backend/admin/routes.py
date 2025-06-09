import json
import os
from functools import wraps

from flask import request
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from flask_restx import Resource

from backend.core.services.profile_service import *
from . import admin_ns
from ..core.messages import AuthMessages
from ..core.models.news_models import News
from ..core.schemas.auth_schemas import login_model, change_password_model, user_model
from ..core.services.utilits import save_image


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        return fn(*args, **kwargs)
    return wrapper


@admin_ns.route('/login')
class AdminLogin(Resource):
    @admin_ns.expect(login_model)
    @admin_ns.doc(description="Аутентификация администратора для получения токена доступа")
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        user = get_user_by_username(username)
        if not user or not user.check_password(password) or user.role.role_name != "admin":
            return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED

        access_token = authenticate_user(username, password)
        if access_token:
            return {"access_token": access_token, "role": "admin"}, HTTPStatus.OK
        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@admin_ns.route('/profile')
class AdminProfile(Resource):
    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Получение информации о пользователе (только для администратора)")
    def get(self):
        current_username = get_jwt_identity()
        user = get_user_by_username(current_username)
        return get_user_info_response(user)

    @jwt_required()
    @admin_required
    @admin_ns.expect(change_password_model)
    @admin_ns.doc(description="Изменение пароля администратора")
    def put(self):
        current_username = get_jwt_identity()
        data = request.get_json()
        if change_password(current_username, data.get("old_password"), data.get("new_password")):
            return {"message": AuthMessages.PASSWORD_CHANGED}, HTTPStatus.OK
        return {"message": AuthMessages.PASSWORD_INVALID_OLD}, HTTPStatus.BAD_REQUEST


@admin_ns.route('/users')
class AdminUserList(Resource):
    @jwt_required()
    @admin_required
    @admin_ns.doc(
        description="Получение списка всех пользователей с возможностью фильтрации по роли (только для администратора)")
    @admin_ns.param('role', 'Фильтрация пользователей по роли')
    def get(self):
        role_filter = request.args.get('role')
        users = get_all_users(role_filter)
        user_list = [get_user_info_response(u)[0] for u in users]
        return user_list, HTTPStatus.OK

    @jwt_required()
    @admin_required
    @admin_ns.expect(user_model)
    @admin_ns.doc(description="Создание нового пользователя (или резидента) от лица администратора")
    def post(self):
        current_role = get_jwt().get('role')
        data = request.get_json()
        return register_user("user", data, current_role)

@admin_ns.route('/users/detail/<string:username>')
class AdminUserDetail(Resource):
    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Получение информации о пользователе по username (только для администратора)")
    def get(self, username):
        user = get_user_by_username(username)
        if user:
            return get_user_info_response(user)
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Удаление пользователя по username (только для администратора)")
    def delete(self, username):
        if delete_user(username):
            return {"message": AuthMessages.USER_DELETED}, HTTPStatus.OK
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND


@admin_ns.route('/news')
class NewsResource(Resource):
    @jwt_required()
    @admin_required
    @admin_ns.doc(
        description="Создание новости с JSON-данными (в поле 'data') и изображением (в поле 'image')",
        params={
            'data': 'JSON-объект с полями title, content',
            'image': 'Файл изображения (jpeg, png и т.д.)'
        }
    )
    def post(self):
        if 'data' not in request.form:
            return {"message": "Поле 'data' обязательно"}, HTTPStatus.BAD_REQUEST
        try:
            data = json.loads(request.form['data'])
        except json.JSONDecodeError as e:
            return {"message": f"Ошибка в JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST

        title = data.get("title")
        content = data.get("content")
        if not all([title, content]):
            return {"message": "Поля title и content обязательны"}, HTTPStatus.BAD_REQUEST

        image = request.files.get("image")
        image_path = save_image(image, "news") if image else None
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

        news = News(
            title=title,
            content=content,
            author_id=user.user_id,
            image_path=image_path
        )
        db.session.add(news)
        db.session.commit()

        return {
            "message": "Новость успешно создана",
            "news_id": news.news_id
        }, HTTPStatus.CREATED

    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Получение всех новостей")
    def get(self):
        news_list = News.query.order_by(News.created_at.desc()).all()
        return {"news": [n.to_dict() for n in news_list]}, HTTPStatus.OK


@admin_ns.route('/news/<int:news_id>')
class NewsDetailResource(Resource):
    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Получение конкретной новости по ID")
    def get(self, news_id):
        news = News.query.get(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
        return news.to_dict(), HTTPStatus.OK

    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Обновление новости по ID (только администратор)",
                  params={'data': 'JSON с полями title и/или content', 'image': 'Новая картинка (опционально)'})
    def put(self, news_id):
        news = News.query.get(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND

        if 'data' not in request.form:
            return {"message": "Поле 'data' обязательно"}, HTTPStatus.BAD_REQUEST
        try:
            data = json.loads(request.form['data'])
        except json.JSONDecodeError as e:
            return {"message": f"Ошибка в JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST
        title = data.get("title")
        content = data.get("content")

        if title:
            news.title = title
        if content:
            news.content = content

        image = request.files.get("image")
        if image:
            news.image_path = save_image(image, "news")

        db.session.commit()
        return {"message": "Новость обновлена", "news": news.to_dict()}, HTTPStatus.OK

    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Удаление новости по ID (только администратор)")
    def delete(self, news_id):
        news = News.query.get(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND

        if news.image_path:
            image_path = os.path.join(os.getcwd(), news.image_path)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    return {"message": f"Ошибка при удалении изображения: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR

        db.session.delete(news)
        db.session.commit()
        return {"message": "Новость удалена"}, HTTPStatus.OK