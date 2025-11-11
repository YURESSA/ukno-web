from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource

from backend.core.services.event_services.event_photo_service import get_photos_for_event, \
    delete_photo_from_event, handle_add_photo
from backend.core.services.event_services.event_crud import verify_resident_owns_event
from . import resident_ns
from .decorators import resident_required
from ...core.services.user_services.user_service import get_user_by_email


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
