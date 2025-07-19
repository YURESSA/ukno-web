import json
from functools import wraps
from http import HTTPStatus

from flask import request, Response
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request, get_jwt_identity
from flask_restx import Resource

from backend.core.services.excursion_services.excursion_photo_service import get_photos_for_excursion, \
    add_photo_to_excursion, \
    delete_photo_from_excursion
from backend.core.services.excursion_services.excursion_service import update_excursion, create_excursion, \
    get_excursion, get_all_excursions, \
    delete_excursion
from backend.core.services.excursion_services.excursion_session_service import get_sessions_for_excursion, \
    create_excursion_session, \
    update_excursion_session, delete_excursion_session
from backend.core.services.user_services.profile_service import get_user_info_response, update_user, register_user
from . import admin_ns
from ..core.messages import AuthMessages
from ..core.models.excursion_models import Reservation
from ..core.schemas.auth_schemas import login_model, change_password_model, user_model
from ..core.schemas.excursion_schemas import excursion_model, session_model, session_patch_model
from ..core.services.news_service import add_photo_to_news, get_photos_for_news, delete_photo_from_news, \
    create_news_with_images, get_all_news, get_news_by_id, update_news, delete_news
from ..core.services.reservation_service import delete_reservation_with_refund, get_all_reservations, \
    get_reservation_by_id
from ..core.services.user_services.auth_service import get_user_by_email, authenticate_user, change_password, \
    get_all_users, delete_user


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        email = get_jwt_identity()
        user = get_user_by_email(email)
        if claims.get("role") != "admin" or not user:
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        return fn(*args, **kwargs)

    return wrapper


@admin_ns.route('/login')
class AdminLogin(Resource):
    @admin_ns.expect(login_model)
    @admin_ns.doc(description="Аутентификация администратора для получения токена доступа")
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = get_user_by_email(email)
        if not user or not user.check_password(password) or user.role.role_name != "admin":
            return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED

        access_token = authenticate_user(email, password)
        if access_token:
            return {"access_token": access_token, "role": "admin"}, HTTPStatus.OK
        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@admin_ns.route('/profile')
class AdminProfile(Resource):
    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Получение информации о пользователе (только для администратора)")
    def get(self):
        current_email = get_jwt_identity()
        user = get_user_by_email(current_email)
        return get_user_info_response(user)

    @jwt_required()
    @admin_required
    @admin_ns.expect(change_password_model)
    @admin_ns.doc(description="Изменение пароля администратора")
    def put(self):
        current_email = get_jwt_identity()
        data = request.get_json()
        if change_password(current_email, data.get("old_password"), data.get("new_password")):
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


@admin_ns.route('/users/detail/<string:email>')
class AdminUserDetail(Resource):
    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Получение информации о пользователе по email (только для администратора)")
    def get(self, email):
        user = get_user_by_email(email)
        if user:
            return get_user_info_response(user)
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Удаление пользователя по email (только для администратора)")
    def delete(self, email):
        if delete_user(email):
            return {"message": AuthMessages.USER_DELETED}, HTTPStatus.OK
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Редактирование пользователя по email (только для администратора)")
    def put(self, email):
        data = request.get_json()
        if not data:
            return {"message": "Пустой JSON"}, HTTPStatus.BAD_REQUEST

        user = get_user_by_email(email)
        if not user:
            return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

        try:
            updated_user = update_user(email, data)
        except ValueError as e:
            return {"message": str(e)}, HTTPStatus.BAD_REQUEST

        return get_user_info_response(updated_user), HTTPStatus.OK


@admin_ns.route('/news')
class NewsResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        data_str = request.form.get("data")
        images = request.files.getlist("image")
        user_email = get_jwt_identity()

        response, status = create_news_with_images(user_email, data_str, images)
        return response, status

    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Получение всех новостей")
    def get(self):
        news_data = get_all_news()
        return {"news": news_data}, HTTPStatus.OK


@admin_ns.route('/news/<int:news_id>')
class NewsDetailResource(Resource):
    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Получение конкретной новости по ID")
    def get(self, news_id):
        news = get_news_by_id(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
        return news.to_dict(), HTTPStatus.OK

    @jwt_required()
    @admin_required
    def put(self, news_id):
        news, error = update_news(news_id, request.form, request.files)
        if error:
            return ({
                        "message": error}, HTTPStatus.BAD_REQUEST if "JSON" in error or "обязательно" in error
                    else HTTPStatus.NOT_FOUND)
        return {"message": "Новость обновлена", "news": news.to_dict()}, HTTPStatus.OK

    @jwt_required()
    @admin_required
    @admin_ns.doc(description="Удаление новости по ID (только администратор)")
    def delete(self, news_id):
        success, error = delete_news(news_id)
        if not success:
            return {"message": error}, HTTPStatus.NOT_FOUND
        return {"message": "Новость удалена"}, HTTPStatus.OK


@admin_ns.route('/news/<int:news_id>/photos')
class AdminNewsPhotosResource(Resource):
    @admin_required
    def get(self, news_id):
        photos, error, status = get_photos_for_news(news_id)
        if error:
            return error, status
        return {"photos": photos}, status

    @admin_required
    @admin_ns.doc(
        description="Загрузка фото для новости",
        params={
            'photo': {
                'description': 'Файл фотографии',
                'in': 'formData',
                'type': 'file',
                'required': True
            }
        }
    )
    def post(self, news_id):
        if 'photo' not in request.files:
            return {"message": "Фото не загружено"}, HTTPStatus.BAD_REQUEST
        photo_file = request.files['photo']
        photos, error, status = add_photo_to_news(news_id, photo_file)
        if error:
            return error, status
        photos, _, status = get_photos_for_news(news_id)
        return {"message": "Фото добавлено", "photos": photos}, status


@admin_ns.route('/news/<int:news_id>/photos/<int:photo_id>')
class AdminNewsPhotoResource(Resource):
    @admin_required
    def delete(self, news_id, photo_id):
        result, status = delete_photo_from_news(news_id, photo_id)
        return result, status


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
        created_by = get_jwt_identity()

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
        admin = get_user_by_email(get_jwt_identity())
        response = delete_excursion(excursion_id, admin, return_csv=True)

        if isinstance(response, Response):
            return response

        result, status = response
        return result, status


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
        response = delete_excursion_session(excursion_id, session_id, notify_resident=True)
        if isinstance(response, Response):
            return response

        result, status = response
        return result, status

    @admin_required
    def get(self, excursion_id, session_id):
        reservations = Reservation.query.filter_by(session_id=session_id).all()

        participants = [r.to_dict_detailed() for r in reservations]

        return {'participants': participants}, 200


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


@admin_ns.route('/reservations')
class AdminReservationsResource(Resource):
    @admin_required
    def get(self):
        reservations_data = get_all_reservations()
        return {'reservations': reservations_data}, 200


@admin_ns.route('/reservations/<int:reservation_id>')
class AdminReservationDetailResource(Resource):
    @admin_required
    def get(self, reservation_id):
        reservation_data = get_reservation_by_id(reservation_id)
        if not reservation_data:
            return {'message': 'Бронь не найдена'}, 404
        return {'reservation': reservation_data}, 200

    @jwt_required()
    @admin_required
    def delete(self, reservation_id):
        success, message, status_code = delete_reservation_with_refund(reservation_id)
        return {"message": message}, status_code
