from functools import wraps
from http import HTTPStatus
from typing import Dict, Any, Optional, List, Tuple

from flask import request, Response
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity
from flask_restx import Resource

from backend.core.services.event_services.event_photo_service import get_photos_for_event, \
    delete_photo_from_event, handle_add_photo
from backend.core.services.event_services.event_service import update_event, get_event, get_all_events, \
    delete_event, handle_create_event
from backend.core.services.event_services.event_session_service import get_sessions_for_event, \
    create_event_session, \
    update_event_session, delete_event_session
from backend.core.services.user_services.profile_service import get_user_info_response, update_user, register_user, \
    login_user
from . import admin_ns
from ..core.messages import AuthMessages
from ..core.models.event_models import Reservation
from ..core.schemas.admin_schemas import admin_login, create_parser, update_parser, update_user_model
from ..core.schemas.auth_schemas import change_password_model, user_model
from ..core.schemas.event_schemas import event_model, session_model, session_patch_model
from ..core.services.news_service import add_photo_to_news, get_photos_for_news, delete_photo_from_news, \
    create_news_with_images, get_all_news, get_news_by_id, update_news, delete_news
from ..core.services.reservation_service import delete_reservation_with_refund, get_all_reservations, \
    get_reservation_by_id
from ..core.services.user_services.auth_service import get_user_by_email, change_password, \
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
    @admin_ns.expect(admin_login)
    @admin_ns.doc(description="Аутентификация администратора для получения токена доступа")
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Авторизация администратора для получения JWT токена.
        """
        data: Dict[str, Any] = request.get_json() or {}
        response, status = login_user("admin", data)
        return response, status


@admin_ns.route('/profile')
class AdminProfile(Resource):

    @admin_required
    def get(self) -> Tuple[Dict[str, Any], int]:
        """
        Получение информации о текущем администраторе.
        """
        current_email = get_jwt_identity()
        user = get_user_by_email(current_email)
        return get_user_info_response(user)

    @admin_required
    @admin_ns.expect(change_password_model)
    def put(self) -> Tuple[Dict[str, str], int]:
        """
        Изменение пароля администратора.
        """
        current_email: str = get_jwt_identity()
        data: Dict[str, Any] = request.get_json() or {}

        old_password: str | None = data.get("old_password")
        new_password: str | None = data.get("new_password")

        if not old_password or not new_password:
            return {"message": "Старый и новый пароль обязательны"}, HTTPStatus.BAD_REQUEST

        if change_password(current_email, old_password, new_password):
            return {"message": AuthMessages.PASSWORD_CHANGED}, HTTPStatus.OK

        return {"message": AuthMessages.PASSWORD_INVALID_OLD}, HTTPStatus.BAD_REQUEST


@admin_ns.route('/users')
class AdminUserList(Resource):

    @admin_required
    def get(self) -> Tuple[List[Dict[str, Any]], int]:
        """
        Получение списка всех пользователей с возможностью фильтрации по роли (только для администратора)
        """
        role_filter: str | None = request.args.get('role')
        users: list = get_all_users(role_filter)
        user_list: List[Dict[str, Any]] = [get_user_info_response(u)[0] for u in users]
        return user_list, HTTPStatus.OK

    @admin_required
    @admin_ns.expect(user_model)
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Создание нового пользователя (или резидента) от лица администратора
        """
        current_role: str = get_jwt().get('role', '')
        data: Dict[str, Any] = request.get_json() or {}
        response, status = register_user("user", data, current_role)
        return response, status


@admin_ns.route('/users/detail/<string:email>')
class AdminUserDetail(Resource):
    @admin_required
    @admin_ns.doc(description="Получение информации о пользователе по email (только для администратора)")
    def get(self, email: str) -> Tuple[dict, int]:
        """
        Получение информации о пользователе по email
        """
        user = get_user_by_email(email)
        if user:
            return get_user_info_response(user)
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

    @admin_required
    @admin_ns.doc(description="Удаление пользователя по email (только для администратора)")
    def delete(self, email: str) -> Tuple[dict, int]:
        """
        Удаление пользователя по email
        """
        if delete_user(email):
            return {"message": AuthMessages.USER_DELETED}, HTTPStatus.OK
        return {"message": AuthMessages.USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

    @admin_required
    @admin_ns.doc(description="Редактирование пользователя по email (только для администратора)")
    @admin_ns.expect(update_user_model)
    def put(self, email: str) -> tuple[dict, int]:
        """
        Редактирование полей пользователя:
        - full_name
        - email
        - phone
        - password
        - role_name
        """
        data: dict = request.get_json() or {}
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
    @admin_required
    @admin_ns.expect(create_parser)
    @admin_ns.doc(description="Создание новости")
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Создание новости с прикрепленными изображениями
        """
        data_str: str = request.form.get("data", "")
        images: List = request.files.getlist("image")
        user_email: str = get_jwt_identity()

        response, status = create_news_with_images(user_email, data_str, images)
        return response, status

    @admin_required
    @admin_ns.doc(description="Получение всех новостей")
    def get(self) -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
        """
        Получение списка всех новостей
        """
        news_data: List[Dict[str, Any]] = get_all_news()
        return {"news": news_data}, HTTPStatus.OK


@admin_ns.route('/news/<int:news_id>')
class NewsDetailResource(Resource):
    @admin_required
    def get(self, news_id: int) -> tuple[dict, int]:
        """
        Получение конкретной новости по ID.

        :param news_id: Идентификатор новости
        :return: JSON с данными новости или сообщение об ошибке
        """
        news = get_news_by_id(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
        return news.to_dict(), HTTPStatus.OK

    @admin_required
    @admin_ns.expect(update_parser)
    def put(self, news_id: int) -> tuple[dict, int]:
        """
        Обновление новости по ID.

        :param news_id: Идентификатор новости
        :return: JSON с обновленной новостью или сообщение об ошибке
        """
        args = update_parser.parse_args()
        form_data: dict = {'data': args['data']}
        files: Optional[dict] = {'image': args.getlist('image')} if args.get('image') else None

        news, error = update_news(news_id, form_data, files)
        if error:
            return ({
                        "message": error}, HTTPStatus.BAD_REQUEST if "JSON" in error or "обязательно" in error
                    else HTTPStatus.NOT_FOUND)
        return {"message": "Новость обновлена", "news": news.to_dict()}, HTTPStatus.OK

    @admin_required
    def delete(self, news_id: int) -> tuple[dict, int]:
        """
        Удаление новости по ID (только для администратора).

        :param news_id: Идентификатор новости
        :return: Сообщение об успешном удалении или об ошибке
        """
        success, error = delete_news(news_id)
        if not success:
            return {"message": error}, HTTPStatus.NOT_FOUND
        return {"message": "Новость удалена"}, HTTPStatus.OK


@admin_ns.route('/news/<int:news_id>/photos')
class AdminNewsPhotosResource(Resource):
    @admin_required
    def get(self, news_id: int) -> tuple[dict, int]:
        """
        Получение списка всех фото для конкретной новости.

        :param news_id: Идентификатор новости
        :return: JSON с массивом фото или сообщение об ошибке
        """
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
    def post(self, news_id: int) -> tuple[dict, int]:
        """
        Загрузка нового фото для конкретной новости.

        :param news_id: Идентификатор новости
        :return: JSON с сообщением и обновленным списком фото или сообщение об ошибке
        """
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
    def delete(self, news_id: int, photo_id: int) -> tuple[dict, int]:
        """
        Удаление конкретного фото новости по ID.

        :param news_id: Идентификатор новости
        :param photo_id: Идентификатор фото
        :return: Сообщение об успешном удалении или ошибка
        """
        result, status = delete_photo_from_news(news_id, photo_id)
        if not result:
            return {"message": "Фото не найдено или не удалось удалить"}, status
        return {"message": "Фото удалено"}, status


@admin_ns.route('/excursions')
class AdminExcursionsResource(Resource):
    @admin_required
    @admin_ns.doc(description="Получение списка всех экскурсий (только для администратора)")
    def get(self) -> tuple[dict, int]:
        """
        Получение всех экскурсий с полями для отображения в админ-панели.

        :return: JSON с массивом экскурсий и HTTP-статус 200
        """
        excursions = get_all_events()
        return {"excursions": [e.to_dict() for e in excursions]}, HTTPStatus.OK

    @admin_required
    @admin_ns.doc(
        description="Создание новой экскурсии (только для администратора)",
        params={
            'data': {'description': 'JSON-данные экскурсии', 'in': 'formData', 'required': True},
            'photos': {'description': 'Список фото', 'in': 'formData', 'type': 'file', 'required': False}
        }
    )
    def post(self) -> tuple[dict, int]:
        """
        Создание новой экскурсии с возможностью загрузки фотографий.

        Ожидается поле 'data' в form-data с JSON-данными экскурсии.
        Дополнительно можно передать фотографии в поле 'photos'.

        :return: JSON с сообщением об успешном создании и ID экскурсии или ошибкой, HTTP-статус
        """
        return handle_create_event()


@admin_ns.route('/excursions/<int:excursion_id>')
class AdminExcursionResource(Resource):
    @admin_required
    @admin_ns.expect(event_model, validate=True)
    def patch(self, excursion_id: int) -> tuple[dict, int]:
        """
        Обновление данных конкретной экскурсии (только для администратора).

        :param excursion_id: ID экскурсии
        :return: JSON с сообщением и обновлёнными данными экскурсии, или ошибка, HTTP-статус
        """
        data = request.get_json()
        excursion, error, status = update_event(excursion_id, data)
        if error:
            return error, status
        return {"message": "Экскурсия обновлена", "excursion": excursion.to_dict()}, status

    @admin_required
    def get(self, excursion_id: int) -> tuple[dict, int]:
        """
        Получение информации о конкретной экскурсии по ID (только для администратора).

        :param excursion_id: ID экскурсии
        :return: JSON с данными экскурсии и HTTP-статус 200 или ошибка 404
        """
        excursion = get_event(excursion_id)
        if not excursion:
            return {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND
        return {"excursion": excursion.to_dict(include_related=True)}, HTTPStatus.OK

    @admin_required
    def delete(self, excursion_id: int) -> tuple[dict, int] | Response:
        """
        Удаление конкретной экскурсии (только для администратора).

        :param excursion_id: ID экскурсии
        :return: JSON
        """
        admin = get_user_by_email(get_jwt_identity())
        response = delete_event(excursion_id, admin, return_csv=True)

        if isinstance(response, Response):
            return response

        result, status = response
        return result, status


@admin_ns.route('/excursions/<int:excursion_id>/sessions')
class AdminExcursionSessionsResource(Resource):
    @admin_required
    def get(self, excursion_id: int) -> tuple[list[dict], int]:
        """
        Получение всех сессий конкретной экскурсии (только для администратора).

        :param excursion_id: ID экскурсии
        :return: Список сессий в виде словарей и HTTP-статус 200
        """
        sessions = get_sessions_for_event(excursion_id)
        return [s.to_dict() for s in sessions], HTTPStatus.OK

    @admin_required
    @admin_ns.expect(session_model, validate=True)
    def post(self, excursion_id: int) -> tuple[dict, int]:
        """
        Создание новой сессии для конкретной экскурсии (только для администратора).

        :param excursion_id: ID экскурсии
        :return: Созданная сессия в виде словаря и соответствующий HTTP-статус.
                 В случае ошибки возвращается словарь с сообщением и статус ошибки.
        """
        data = request.get_json()
        session, error, status = create_event_session(excursion_id, data)
        if error:
            return error, status
        return session.to_dict(), status


@admin_ns.route('/excursions/<int:excursion_id>/sessions/<int:session_id>')
class AdminExcursionSessionResource(Resource):
    @admin_required
    @admin_ns.expect(session_patch_model)
    def patch(self, excursion_id: int, session_id: int) -> tuple[dict, int]:
        """
        Обновление данных сессии конкретной экскурсии (только для администратора).

        :param excursion_id: ID экскурсии
        :param session_id: ID сессии
        :return: Обновленная сессия в виде словаря и HTTP-статус.
                 В случае ошибки возвращается словарь с сообщением и статус ошибки.
        """
        data = request.get_json()
        session, error, status = update_event_session(excursion_id, session_id, data)
        if error:
            return error, status
        return session.to_dict(), status

    @admin_required
    def delete(self, excursion_id: int, session_id: int) -> tuple[dict, int] | Response:
        """
        Удаление сессии экскурсии (только для администратора).

        :param excursion_id: ID экскурсии
        :param session_id: ID сессии
        :return: Сообщение об успешном удалении и HTTP-статус или Response (например, CSV).
        """
        response = delete_event_session(excursion_id, session_id, notify_resident=True)
        if isinstance(response, Response):
            return response

        result, status = response
        return result, status

    @admin_required
    def get(self, excursion_id: int, session_id: int) -> tuple[dict, int]:
        """
        Получение списка участников конкретной сессии экскурсии (только для администратора).

        :param excursion_id: ID экскурсии
        :param session_id: ID сессии
        :return: Словарь с участниками и HTTP-статус 200
        """
        reservations = Reservation.query.filter_by(session_id=session_id).all()
        participants = [r.to_dict_detailed() for r in reservations]
        return {'participants': participants}, HTTPStatus.OK


@admin_ns.route('/excursions/<int:excursion_id>/photos')
class AdminExcursionPhotosResource(Resource):
    @admin_required
    def get(self, excursion_id: int) -> tuple[dict, int]:
        photos, error, status = get_photos_for_event(excursion_id)
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
    def post(self, excursion_id: int) -> tuple[dict, int]:
        """
            Загрузка нового фото для конкретной экскурсии.

            :param excursion_id: ID экскурсии, к которой добавляется фото
            :return: Словарь с сообщением и обновлённым списком фото, и HTTP-статус.
                     В случае ошибки возвращается словарь с сообщением и статус ошибки.
            """
        if 'photo' not in request.files:
            return {"message": "Фото не загружено"}, HTTPStatus.BAD_REQUEST
        photo_file = request.files['photo']
        return handle_add_photo(excursion_id, photo_file)


@admin_ns.route('/excursions/<int:excursion_id>/photos/<int:photo_id>')
class AdminExcursionPhotoResource(Resource):
    @admin_required
    def delete(self, excursion_id: int, photo_id: int) -> tuple[dict, int]:
        """
        Удаление конкретного фото экскурсии.

        :param excursion_id: ID экскурсии
        :param photo_id: ID фото
        :return: Словарь с сообщением и HTTP-статус.
        """
        result, status = delete_photo_from_event(excursion_id, photo_id)
        return result, status


@admin_ns.route('/reservations')
class AdminReservationsResource(Resource):
    @admin_required
    def get(self) -> tuple[dict, int]:
        """
        Получение списка всех броней (только для администратора).

        :return: JSON с массивом всех броней и HTTP-статус 200
        """
        reservations_data = get_all_reservations()
        return {'reservations': reservations_data}, HTTPStatus.OK


@admin_ns.route('/reservations/<int:reservation_id>')
class AdminReservationDetailResource(Resource):
    @admin_required
    def get(self, reservation_id: int) -> tuple[dict, int]:
        """
        Получение информации о конкретной брони по ID.

        :param reservation_id: Идентификатор брони
        :return: JSON с данными брони или сообщение об ошибке, если бронь не найдена
        """
        reservation_data = get_reservation_by_id(reservation_id)
        if not reservation_data:
            return {'message': 'Бронь не найдена'}, HTTPStatus.NOT_FOUND
        return {'reservation': reservation_data}, HTTPStatus.OK

    @admin_required
    def delete(self, reservation_id: int) -> tuple[dict, int]:
        """
        Удаление брони с возможным возвратом средств (только для администратора).

        :param reservation_id: Идентификатор брони
        :return: JSON с сообщением об успешном удалении или ошибке и соответствующий HTTP-статус
        """
        success, message, status_code = delete_reservation_with_refund(reservation_id)
        return {"message": message}, status_code
