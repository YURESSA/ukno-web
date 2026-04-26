from http import HTTPStatus

from flask import request, Response
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource

from backend.core.services.event_services.event_photo_service import get_photos_for_event, \
    delete_photo_from_event, handle_add_photo
from backend.core.services.event_services.event_api import handle_create_event
from backend.core.services.event_services.event_crud import get_event, get_all_events, delete_event, update_event
from backend.core.services.event_services.event_session_service import get_sessions_for_event, \
    create_event_session, \
    update_event_session, delete_event_session
from . import admin_ns
from .decorators import admin_required
from backend.core.models.event_models import Reservation
from backend.core.schemas.event_schemas import event_model, session_model, session_patch_model
from ...core.services.user_services.user_service import get_user_by_email


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
