from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx import Resource

from backend.core.services.profile_service import *
from backend.core.services.team_service import *
from . import organizer_ns
from ..core.messages import AuthMessages
from ..core.schemas.auth_schemas import login_model


def organizer_or_admin_required():
    claims = get_jwt()
    return claims.get("role") in ["organizer", "admin"]


def organizer_required():
    claims = get_jwt()
    return claims.get("role") == "organizer"


@organizer_ns.route('/login')
class OrganizerLogin(Resource):
    @organizer_ns.expect(login_model)
    @organizer_ns.doc(description="Аутентификация организатора для получения токена доступа")
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        user = get_user_by_username(username)

        if not user or not user.check_password(password) or user.system_role.role_name != "organizer":
            return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED

        access_token = authenticate_user(username, password)
        if access_token:
            return {"access_token": access_token}, HTTPStatus.OK

        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@organizer_ns.route('/profile')
class OrganizerProfile(Resource):
    @jwt_required()
    def get(self):
        if not organizer_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        username = get_jwt_identity()
        user = get_user_by_username(username)
        return get_user_info_response(user)


@organizer_ns.route('/jury')
class JuryManage(Resource):
    @jwt_required()
    def post(self):
        if not organizer_or_admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        data = request.get_json()
        new_user_role = data.get("role_name")

        if not new_user_role:
            return {"message": "Поле 'role_name' обязательно для создания пользователя."}, HTTPStatus.BAD_REQUEST

        if new_user_role != "jury":
            return {"message": f"Вы можете создать только пользователя с ролью 'jury'."}, HTTPStatus.FORBIDDEN

        return register_user(data)

    @jwt_required()
    def get(self):
        if not organizer_or_admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        jury_users = get_all_users("jury")
        return [get_user_info_response(jury)[0] for jury in jury_users], HTTPStatus.OK


@organizer_ns.route('/teams')
class TeamList(Resource):
    @jwt_required()
    def get(self):
        if not organizer_or_admin_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN
        teams = Team.query.all()
        return [team.to_dict() for team in teams], HTTPStatus.OK


@organizer_ns.route('/teams/<string:team_name>/members')
class TeamMembersByName(Resource):
    @jwt_required()
    def get(self, team_name):
        if not organizer_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        team = Team.query.filter_by(team_name=team_name).first()
        if not team:
            return {"message": "Команда не найдена."}, HTTPStatus.NOT_FOUND

        members = team.members
        return [user.to_dict() for user in members], HTTPStatus.OK


@organizer_ns.route('/teams/<string:team_name>')
class TeamDeleteByName(Resource):
    @jwt_required()
    def delete(self, team_name):
        if not organizer_required():
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        team = Team.query.filter_by(team_name=team_name).first()
        if not team:
            return {"message": "Команда не найдена."}, HTTPStatus.NOT_FOUND

        db.session.delete(team)
        db.session.commit()
        return {"message": "Команда успешно удалена."}, HTTPStatus.OK
