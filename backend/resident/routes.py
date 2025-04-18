import json

from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx import Resource

from backend.core.schemas.auth_schemas import *
from backend.core.services.profile_service import *
from . import resident_ns
from ..core.schemas.excursion_schemas import *
from ..core.services.excursion_service import *


def resident_required():
    claims = get_jwt()
    if claims.get("role") != "resident":
        return False
    return True


@resident_ns.route('/login')
class ResidentLogin(Resource):
    @resident_ns.expect(login_model)
    @resident_ns.doc(description="Аутентификация резидента для получения токена доступа")
    def post(self):
        data = request.get_json()
        token = login_user("resident", data)
        if token:
            return {"access_token": token}, HTTPStatus.OK
        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@resident_ns.route('/profile')
class ResidentProfile(Resource):
    @jwt_required()
    @resident_ns.doc(description="Получение информации о резиденте")
    def get(self):
        if not resident_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user)

    @jwt_required()
    @resident_ns.expect(change_password_model)
    @resident_ns.doc(description="Изменение пароля резидента")
    def put(self):
        if not resident_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        data = request.get_json()
        return change_profile_password(data)

    @jwt_required()
    @resident_ns.doc(description="Удаление аккаунта резидента")
    def delete(self):
        if not resident_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        return delete_profile()


@resident_ns.route('/excursions')
class ExcursionsResource(Resource):
    @jwt_required()
    @resident_ns.doc(
        description="Создание экскурсии с данными JSON (в поле 'data') и фотофайлами",
        params={
            'data': data_param,
            'photos': photos_param
        }
    )
    def post(self):
        if not resident_required():
            return {"message": "Доступ запрещён"}, HTTPStatus.FORBIDDEN

        if 'data' not in request.form:
            return {"message": "Поле 'data' обязательно"}, HTTPStatus.BAD_REQUEST
        try:
            data = json.loads(request.form['data'])
        except json.JSONDecodeError as e:
            return {"message": f"Ошибка в JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST

        files = request.files.getlist("photos")

        created_by = get_jwt_identity()
        excursion, error, status = create_excursion(data, created_by, files)
        if error:
            return error, status

        return {
            "message": "Экскурсия успешно создана",
            "excursion_id": excursion.excursion_id
        }, HTTPStatus.CREATED

    @jwt_required()
    @resident_ns.doc(description="Получение всех экскурсий, созданных текущим резидентом")
    def get(self):
        resident_id = get_jwt_identity()
        excursions = get_excursions_for_resident(resident_id)
        return {"excursions": [serialize_excursion(ex) for ex in excursions]}, HTTPStatus.OK


@resident_ns.route('/excursions_detail/<int:excursion_id>')
class DetailExcursion(Resource):
    @jwt_required()
    def get(self, excursion_id):
        resident_id = get_jwt_identity()
        excursion = get_excursion_or_404(excursion_id, resident_id)

        if not excursion:
            return {"message": "Экскурсия не найдена или не принадлежит текущему резиденту"}, HTTPStatus.NOT_FOUND

        return serialize_excursion(excursion), HTTPStatus.OK

    @jwt_required()
    @resident_ns.doc(
        description="Обновление экскурсии с JSON-данными (в поле 'data') и новыми фотофайлами",
        params={
            'data': data_param,
            'photos': photos_param
        }
    )
    def put(self, excursion_id):
        resident_id = get_jwt_identity()
        excursion = get_excursion_or_404(excursion_id, resident_id)

        if not excursion:
            return {"message": "Экскурсия не найдена или не принадлежит текущему резиденту"}, HTTPStatus.NOT_FOUND

        if 'data' not in request.form:
            return {"message": "Поле 'data' обязательно"}, HTTPStatus.BAD_REQUEST

        try:
            data = json.loads(request.form['data'])
        except json.JSONDecodeError as e:
            return {"message": f"Ошибка в JSON: {str(e)}"}, HTTPStatus.BAD_REQUEST
        files = request.files.getlist("photos")
        return update_excursion(excursion, data, files)

    @jwt_required()
    def delete(self, excursion_id):
        resident_id = get_jwt_identity()
        excursion = get_excursion_or_404(excursion_id, resident_id)

        if not excursion:
            return {"message": "Экскурсия не найдена или не принадлежит текущему резиденту"}, HTTPStatus.NOT_FOUND

        try:
            clear_photos(excursion)

            db.session.delete(excursion)
            db.session.commit()

            return {"message": "Экскурсия успешно удалена"}, HTTPStatus.OK

        except Exception as e:
            return {"message": f"Ошибка при удалении экскурсии: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
