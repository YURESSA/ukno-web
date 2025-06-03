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
from ..core.schemas.excursion_schemas import excursion_model, session_model, session_patch_model
from ..core.services.excursion_photo_service import get_photos_for_excursion, add_photo_to_excursion, \
    delete_photo_from_excursion
from ..core.services.excursion_service import update_excursion, create_excursion, get_excursion, get_all_excursions, \
    delete_excursion
from ..core.services.excursion_session_service import get_sessions_for_excursion, create_excursion_session, \
    update_excursion_session, delete_excursion_session
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


@admin_ns.route('/excursions')
class AdminExcursionsResource(Resource):
    @admin_required
    @admin_ns.doc(description="Получить все экскурсии (админ)")
    def get(self):
        excursions = get_all_excursions()
        return {"excursions": [e.to_dict() for e in excursions]}, HTTPStatus.OK

    @admin_required
    @admin_ns.doc(
        description="Создание экскурсии (админ)",
        params={
            'data': {'description': 'JSON-данные экскурсии', 'in': 'formData', 'required': True},
            'photos': {'description': 'Список фото', 'in': 'formData', 'type': 'file', 'required': False}
        }
    )
    def post(self):
        if 'data' not in request.form:
            return {"message": "Поле 'data' обязательно"}, HTTPStatus.BAD_REQUEST
        try:
            data = json.loads(request.form['data'])
        except json.JSONDecodeError as e:
            return {"message": f"Неверный JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST

        files = request.files.getlist("photos")
        created_by = None

        excursion, error, status = create_excursion(data, created_by, files)
        if error:
            return error, status
        return {"message": "Экскурсия создана", "excursion_id": excursion.excursion_id}, HTTPStatus.CREATED


@admin_ns.route('/excursions/<int:excursion_id>')
class AdminExcursionResource(Resource):
    @admin_required
    @admin_ns.expect(excursion_model, validate=True)
    def patch(self, excursion_id):
        data = request.get_json()
        excursion, error, status = update_excursion(excursion_id, data)
        if error:
            return error, status
        return {"message": "Экскурсия обновлена", "excursion": excursion.to_dict()}, status

    @admin_required
    def get(self, excursion_id):
        excursion = get_excursion(excursion_id)
        if not excursion:
            return {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND
        return {"excursion": excursion.to_dict(include_related=True)}, HTTPStatus.OK

    @admin_required
    def delete(self, excursion_id):
        excursion = get_excursion(excursion_id)
        if not excursion:
            return {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND

        try:
            delete_excursion(excursion_id)
        except Exception as e:
            return {"message": f"Ошибка при удалении экскурсии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR

        return {"message": "Экскурсия успешно удалена"}, HTTPStatus.NO_CONTENT


@admin_ns.route('/excursions/<int:excursion_id>/sessions')
class AdminExcursionSessionsResource(Resource):
    @admin_required
    def get(self, excursion_id):
        sessions = get_sessions_for_excursion(excursion_id)
        return [s.to_dict() for s in sessions], HTTPStatus.OK

    @admin_required
    @admin_ns.expect(session_model, validate=True)
    def post(self, excursion_id):
        data = request.get_json()
        session, error, status = create_excursion_session(excursion_id, data)
        if error:
            return error, status
        return session.to_dict(), status


@admin_ns.route('/excursions/<int:excursion_id>/sessions/<int:session_id>')
class AdminExcursionSessionResource(Resource):
    @admin_required
    @admin_ns.expect(session_patch_model)
    def patch(self, excursion_id, session_id):
        data = request.get_json()
        session, error, status = update_excursion_session(excursion_id, session_id, data)
        if error:
            return error, status
        return session.to_dict(), status

    @admin_required
    def delete(self, excursion_id, session_id):
        result, status = delete_excursion_session(excursion_id, session_id)
        return result, status


@admin_ns.route('/excursions/<int:excursion_id>/photos')
class AdminExcursionPhotosResource(Resource):
    @admin_required
    def get(self, excursion_id):
        photos, error, status = get_photos_for_excursion(excursion_id)
        if error:
            return error, status
        return {"photos": photos}, status

    @admin_required
    @admin_ns.doc(
        description="Загрузка фото для экскурсии",
        params={
            'photo': {
                'description': 'Файл фотографии',
                'in': 'formData',
                'type': 'file',
                'required': True
            }
        }
    )
    def post(self, excursion_id):
        if 'photo' not in request.files:
            return {"message": "Фото не загружено"}, HTTPStatus.BAD_REQUEST
        photo_file = request.files['photo']
        photos, error, status = add_photo_to_excursion(excursion_id, photo_file)
        if error:
            return error, status
        photos, _, status = get_photos_for_excursion(excursion_id)
        return {"message": "Фото добавлено", "photos": photos}, status


@admin_ns.route('/excursions/<int:excursion_id>/photos/<int:photo_id>')
class AdminExcursionPhotoResource(Resource):
    @admin_required
    def delete(self, excursion_id, photo_id):
        result, status = delete_photo_from_excursion(excursion_id, photo_id)
        return result, status
