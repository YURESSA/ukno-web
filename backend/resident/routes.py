from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx import Resource

from backend.core.services.common_endpoints import login_user, get_profile, get_user_info_response, change_profile_password, \
    delete_profile
from backend.core.messages import AuthMessages
from backend.core.schemas.auth_schemas import login_model, change_password_model
from . import resident_ns


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
