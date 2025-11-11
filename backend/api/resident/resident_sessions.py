from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource

from backend.core.services.event_services.event_crud import verify_resident_owns_event
from backend.core.services.event_services.event_session_service import create_event_session, \
    update_event_session, \
    delete_event_session, get_sessions_for_event
from . import resident_ns
from .decorators import resident_required
from backend.core.schemas.event_schemas import session_model, \
    session_patch_model
from ...core.services.user_services.user_service import get_user_by_email


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
