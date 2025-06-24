import json
from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_restx import Resource

from . import resident_ns
from ..core.schemas.auth_schemas import *
from ..core.schemas.excursion_schemas import *
from ..core.services.excursion_photo_service import add_photo_to_excursion, get_photos_for_excursion, \
    delete_photo_from_excursion
from ..core.services.excursion_service import create_excursion, update_excursion, get_excursions_for_resident, \
    get_resident_excursion_analytics, get_excursion, verify_resident_owns_excursion
from ..core.services.excursion_session_service import create_excursion_session, update_excursion_session, \
    delete_excursion_session, get_sessions_for_excursion
from ..core.services.profile_service import *


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
    def post(self):
        data = request.get_json()
        token = login_user("resident", data)
        if token:
            return {"access_token": token, "role": "resident"}, HTTPStatus.OK
        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@resident_ns.route('/profile')
class ResidentProfile(Resource):
    @resident_required
    @resident_ns.doc(description="Получение информации о резиденте")
    def get(self):
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user)

    @resident_required
    @resident_ns.expect(change_password_model)
    @resident_ns.doc(description="Изменение пароля резидента")
    def put(self):
        data = request.get_json()
        return change_profile_password(data)

    @resident_required
    @resident_ns.doc(description="Удаление аккаунта резидента")
    def delete(self):
        return delete_profile()


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
    def post(self):
        if 'data' not in request.form:
            return {"message": "Поле 'data' обязательно"}, HTTPStatus.BAD_REQUEST
        try:
            data = json.loads(request.form['data'])
        except json.JSONDecodeError as e:
            return {"message": f"Неверный JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST

        files = request.files.getlist("photos")
        email = get_jwt_identity()

        excursion, error, status = create_excursion(data, email, files)
        if error:
            return error, status

        return {
            "message": "Экскурсия успешно создана",
            "excursion_id": excursion.excursion_id
        }, HTTPStatus.CREATED

    @resident_required
    @resident_ns.doc(description="Получение всех экскурсий, созданных текущим резидентом")
    def get(self):
        resident_email = get_jwt_identity()
        resident = get_user_by_email(resident_email)
        excursions = get_excursions_for_resident(resident.user_id)
        return {"excursions": [excursion.to_dict() for excursion in excursions]}, HTTPStatus.OK


@resident_ns.route('/excursions/<int:excursion_id>')
class ExcursionResource(Resource):
    @resident_required
    @resident_ns.expect(excursion_model, validate=True)
    @resident_ns.doc(description="Обновление экскурсии")
    def patch(self, excursion_id):
        data = request.get_json()
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        excursion, error, status = update_excursion(excursion_id, data)
        if error:
            return error, status
        return {"message": "Экскурсия обновлена", "excursion": excursion.to_dict()}, status

    @resident_required
    @resident_ns.doc(description="Получение экскурсии с записями")
    def get(self, excursion_id):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        excursion = get_excursion(excursion_id)
        if not excursion:
            return {"message": "Экскурсия не найдена"}, 404

        data = excursion.to_dict(include_related=True)
        return {"excursion": data}, HTTPStatus.OK


@resident_ns.route('/excursions/<int:excursion_id>/sessions')
class ExcursionSessionsResource(Resource):
    @resident_required
    def get(self, excursion_id):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        sessions = get_sessions_for_excursion(excursion_id)
        return [s.to_dict() for s in sessions], HTTPStatus.OK

    @resident_required
    @resident_ns.expect(session_model, validate=True)
    def post(self, excursion_id):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        data = request.get_json()
        session, error, status = create_excursion_session(excursion_id, data)
        if error:
            return error, status
        return session.to_dict(), status


@resident_ns.route('/excursions/<int:excursion_id>/sessions/<int:session_id>')
class ExcursionSessionResource(Resource):
    @resident_required
    @resident_ns.expect(session_patch_model)
    @resident_ns.doc(description="Обновление конкретной сессии экскурсии")
    def patch(self, excursion_id, session_id):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        data = request.get_json()
        session, error, status = update_excursion_session(excursion_id, session_id, data)
        if error:
            return error, status
        return session.to_dict(), status

    @resident_required
    @resident_ns.doc(description="Удаление конкретной сессии экскурсии")
    def delete(self, excursion_id, session_id):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        result, status = delete_excursion_session(excursion_id, session_id)
        return result, status


@resident_ns.route('/excursions/<int:excursion_id>/photos')
class ExcursionPhotosResource(Resource):
    @resident_required
    def get(self, excursion_id):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        photos, error, status = get_photos_for_excursion(excursion_id)
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
    def post(self, excursion_id):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        if 'photo' not in request.files:
            return {"message": "Фото не загружено"}, 400
        photo_file = request.files['photo']

        photos, error, status = add_photo_to_excursion(excursion_id, photo_file)
        if error:
            return error, status
        photos, error, status = get_photos_for_excursion(excursion_id)
        return {"message": "Фото добавлено", "photos": photos}, status


@resident_ns.route('/excursions/<int:excursion_id>/photos/<int:photo_id>')
class ExcursionPhotoResource(Resource):
    @resident_required
    def delete(self, excursion_id, photo_id):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        excursion, error, status = verify_resident_owns_excursion(resident_id, excursion_id)
        if error:
            return error, status
        result, status = delete_photo_from_excursion(excursion_id, photo_id)
        return result, status


@resident_ns.route('/analytics')
class ExcursionAnalytics(Resource):
    @resident_required
    @resident_ns.doc(description="Аналитика по экскурсиям резидента (кол-во посетителей, популярность и т.д.)")
    def get(self):
        resident_id = get_user_by_email(get_jwt_identity()).user_id
        analytics_data = get_resident_excursion_analytics(resident_id)
        return analytics_data, HTTPStatus.OK
