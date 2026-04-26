from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource

from backend.core.schemas.event_schemas import data_param, photos_param, event_model
from backend.core.services.event_services.event_api import handle_create_event
from backend.core.services.event_services.event_crud import get_event, get_events_for_resident, delete_event, \
    update_event, \
    verify_resident_owns_event
from ...core.services.user_services.user_service import get_user_by_email
from . import resident_ns
from .decorators import resident_required


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
