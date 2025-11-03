from functools import wraps
from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity
from flask_restx import Resource

from backend.core.services.event_services.event_photo_service import get_photos_for_event, \
    delete_photo_from_event, handle_add_photo
from backend.core.services.event_services.event_service import update_event, \
    get_events_for_resident, \
    get_resident_event_analytics, get_event, verify_resident_owns_event, delete_event, handle_create_event
from backend.core.services.event_services.event_session_service import create_event_session, \
    update_event_session, \
    delete_event_session, get_sessions_for_event
from . import resident_ns
from ..core.schemas.auth_schemas import login_model, change_password_model
from ..core.schemas.event_schemas import data_param, photos_param, event_model, session_model, \
    session_patch_model
from ..core.services.user_services.auth_service import get_user_by_email, change_profile_password
from ..core.services.user_services.profile_service import login_user, get_profile, get_user_info_response, \
    delete_profile


def resident_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        email = get_jwt_identity()
        user = get_user_by_email(email)
        if claims.get("role") != "resident" or not user:
            return {"message": "Доступ запрещён"}, HTTPStatus.FORBIDDEN
        return fn(*args, **kwargs)

    return wrapper


@resident_ns.route('/login')
class ResidentLogin(Resource):
    @resident_ns.expect(login_model)
    @resident_ns.doc(description="Аутентификация резидента для получения токена доступа")
    def post(self) -> tuple[dict, int]:
        """
        Вход резидента и получение JWT-токена.

        :return: Словарь с JWT-токеном и HTTP-статус.
        """
        data: dict = request.get_json() or {}
        response, status = login_user("resident", data)
        return response, status


@resident_ns.route('/profile')
class ResidentProfile(Resource):
    @resident_required
    @resident_ns.doc(description="Получение информации о резиденте")
    def get(self) -> tuple[dict, int]:
        """
        Получение профиля текущего резидента.

        :return: Словарь с данными резидента и HTTP-статус.
                 В случае ошибки — словарь с сообщением и соответствующий статус.
        """
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user), status

    @resident_required
    @resident_ns.expect(change_password_model, validate=True)
    @resident_ns.doc(description="Изменение пароля резидента")
    def put(self) -> tuple[dict, int]:
        """
        Смена пароля текущего резидента.

        :return: Словарь с результатом операции и HTTP-статус.
        """
        data: dict = request.get_json()
        response, status = change_profile_password(data)
        return response, status

    @resident_required
    @resident_ns.doc(description="Удаление аккаунта резидента")
    def delete(self) -> tuple[dict, int]:
        """
        Удаление аккаунта текущего резидента.

        :return: Словарь с результатом операции и HTTP-статус.
        """
        response, status = delete_profile()
        return response, status


@resident_ns.route('/excursions')
class ExcursionsResource(Resource):
    @resident_required
    @resident_ns.doc(
        description="Создание экскурсии с JSON-данными (в поле 'data') и фотофайлами",
        params={
            'data': data_param,
            'photos': photos_param
        }
    )
    def post(self) -> tuple[dict, int]:
        """
        Создание новой экскурсии текущим резидентом.

        :return: Словарь с данными созданной экскурсии и HTTP-статус.
        """
        return handle_create_event()

    @resident_required
    @resident_ns.doc(description="Получение всех экскурсий, созданных текущим резидентом")
    def get(self) -> tuple[dict, int]:
        """
        Получение списка всех экскурсий, созданных текущим резидентом.

        :return: Словарь с ключом "excursions", содержащий список экскурсий,
                 и HTTP-статус.
        """
        resident_email: str = get_jwt_identity()
        resident = get_user_by_email(resident_email)
        excursions = get_events_for_resident(resident.user_id)

        return {
            "excursions": [excursion.to_dict(include_related=True) for excursion in excursions]
        }, HTTPStatus.OK


@resident_ns.route('/excursions/<int:excursion_id>')
class ExcursionResource(Resource):
    @resident_required
    @resident_ns.expect(event_model, validate=True)
    @resident_ns.doc(description="Обновление экскурсии")
    def patch(self, excursion_id: int) -> tuple[dict, int]:
        """
        Обновление данных экскурсии текущего резидента.

        :param excursion_id: ID экскурсии
        :return: Словарь с сообщением и обновлённой экскурсии, а также HTTP-статус.
                 В случае ошибки — словарь с сообщением и статус ошибки.
        """
        data: dict = request.get_json()
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id

        excursion, error, status = verify_resident_owns_event(resident_id, excursion_id)
        if error:
            return error, status

        excursion, error, status = update_event(excursion_id, data)
        if error:
            return error, status

        return {"message": "Экскурсия обновлена", "excursion": excursion.to_dict()}, status

    @resident_required
    @resident_ns.doc(description="Получение экскурсии с записями")
    def get(self, excursion_id: int) -> tuple[dict, int]:
        """
        Получение экскурсии текущего резидента вместе с записями.

        :param excursion_id: ID экскурсии
        :return: Словарь с данными экскурсии и HTTP-статус.
                 Если экскурсия не найдена — сообщение об ошибке и 404.
        """
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id

        excursion, error, status = verify_resident_owns_event(resident_id, excursion_id)
        if error:
            return error, status

        excursion = get_event(excursion_id)
        if not excursion:
            return {"message": "Экскурсия не найдена"}, 404

        data: dict = excursion.to_dict(include_related=True)
        return {"excursion": data}, HTTPStatus.OK

    @resident_required
    @resident_ns.doc(description="Полное удаление экскурсии вместе с сессиями")
    def delete(self, excursion_id: int) -> tuple[dict, int]:
        """
        Полное удаление экскурсии текущего резидента вместе с её сессиями.

        :param excursion_id: ID экскурсии
        :return: Словарь с результатом удаления и HTTP-статус.
                 В случае ошибки — словарь с сообщением и статус ошибки.
        """
        resident = get_user_by_email(get_jwt_identity())
        excursion, error, status = verify_resident_owns_event(resident.user_id, excursion_id)
        if error:
            return error, status

        return delete_event(excursion_id, resident, return_csv=True)


@resident_ns.route('/excursions/<int:excursion_id>/sessions')
class ExcursionSessionsResource(Resource):
    @resident_required
    def get(self, excursion_id: int) -> tuple[list[dict], int]:
        """
        Получение всех сессий конкретной экскурсии текущего резидента.

        :param excursion_id: ID экскурсии
        :return: Список сессий в виде словарей и HTTP-статус.
                 В случае ошибки — словарь с сообщением и статус ошибки.
        """
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_event(resident_id, excursion_id)
        if error:
            return error, status

        sessions = get_sessions_for_event(excursion_id)
        return [s.to_dict() for s in sessions], HTTPStatus.OK

    @resident_required
    @resident_ns.expect(session_model, validate=True)
    def post(self, excursion_id: int) -> tuple[dict, int]:
        """
        Создание новой сессии для конкретной экскурсии текущего резидента.

        :param excursion_id: ID экскурсии
        :return: Словарь с данными созданной сессии и HTTP-статус.
                 В случае ошибки — словарь с сообщением и статус ошибки.
        """
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_event(resident_id, excursion_id)
        if error:
            return error, status

        data: dict = request.get_json()
        session, error, status = create_event_session(excursion_id, data)
        if error:
            return error, status

        return session.to_dict(), status


@resident_ns.route('/excursions/<int:excursion_id>/sessions/<int:session_id>')
class ExcursionSessionResource(Resource):
    @resident_required
    @resident_ns.expect(session_patch_model, validate=True)
    @resident_ns.doc(description="Обновление конкретной сессии экскурсии")
    def patch(self, excursion_id: int, session_id: int) -> tuple[dict, int]:
        """
        Обновление данных конкретной сессии экскурсии текущего резидента.

        :param excursion_id: ID экскурсии
        :param session_id: ID сессии
        :return: Словарь с данными обновлённой сессии и HTTP-статус.
                 В случае ошибки — словарь с сообщением и статус ошибки.
        """
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_event(resident_id, excursion_id)
        if error:
            return error, status

        data: dict = request.get_json()
        session, error, status = update_event_session(excursion_id, session_id, data)
        if error:
            return error, status

        return session.to_dict(), status

    @resident_required
    @resident_ns.doc(description="Удаление конкретной сессии экскурсии")
    def delete(self, excursion_id: int, session_id: int) -> tuple[dict, int]:
        """
        Полное удаление конкретной сессии экскурсии текущего резидента.

        :param excursion_id: ID экскурсии
        :param session_id: ID сессии
        :return: Словарь с результатом удаления и HTTP-статус.
                 В случае ошибки — словарь с сообщением и статус ошибки.
        """
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_event(resident_id, excursion_id)
        if error:
            return error, status

        return delete_event_session(excursion_id, session_id, notify_resident=True)


@resident_ns.route('/excursions/<int:excursion_id>/photos')
class ExcursionPhotosResource(Resource):
    @resident_required
    def get(self, excursion_id: int) -> tuple[dict, int]:
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_event(resident_id, excursion_id)
        if error:
            return error, status
        photos, error, status = get_photos_for_event(excursion_id)
        if error:
            return error, status
        return {"photos": photos}, status

    @resident_required
    @resident_ns.doc(
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


@resident_ns.route('/excursions/<int:excursion_id>/photos/<int:photo_id>')
class ExcursionPhotoResource(Resource):
    @resident_required
    def delete(self, excursion_id: int, photo_id: int) -> tuple[dict, int]:
        """
        Удаление конкретного фото из экскурсии текущего резидента.

        :param excursion_id: ID экскурсии
        :param photo_id: ID фото
        :return: Словарь с результатом операции и HTTP-статус.
                 В случае ошибки возвращается словарь с сообщением и статус ошибки.
        """
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_event(resident_id, excursion_id)
        if error:
            return error, status

        result, status = delete_photo_from_event(excursion_id, photo_id)
        return result, status


@resident_ns.route('/analytics')
class ExcursionAnalytics(Resource):
    @resident_required
    @resident_ns.doc(description="Аналитика по экскурсиям резидента (кол-во посетителей, популярность и т.д.)")
    def get(self) -> tuple[dict, int]:
        """
        Получение аналитических данных по экскурсиям текущего резидента.

        :return: Словарь с данными аналитики и HTTP-статус.
        """
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id
        analytics_data: dict = get_resident_event_analytics(resident_id)
        return analytics_data, HTTPStatus.OK
