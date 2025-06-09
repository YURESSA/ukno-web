from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx import Resource

from backend.core.schemas.auth_schemas import *
from backend.core.services.profile_service import *
from . import jury_ns



def resident_required():
    claims = get_jwt()
    if claims.get("role") != "jury":
        return False
    return True


@jury_ns.route('/login')
class ResidentLogin(Resource):
    @jury_ns.expect(login_model)
    @jury_ns.doc(description="Аутентификация резидента для получения токена доступа")
    def post(self):
        data = request.get_json()
        token = login_user("jury", data)
        if token:
            return {"access_token": token}, HTTPStatus.OK
        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@jury_ns.route('/profile')
class ResidentProfile(Resource):
    @jwt_required()
    @jury_ns.doc(description="Получение информации о резиденте")
    def get(self):
        if not resident_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user)

    @jwt_required()
    @jury_ns.expect(change_password_model)
    @jury_ns.doc(description="Изменение пароля резидента")
    def put(self):
        if not resident_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        data = request.get_json()
        return change_profile_password(data)

    @jwt_required()
    @jury_ns.doc(description="Удаление аккаунта резидента")
    def delete(self):
        if not resident_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        return delete_profile()
