from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from backend.core.schemas.auth_schemas import login_model, user_model, change_password_model
from backend.core.services.profile_service import *
from . import user_ns
from ..core.services.excursion_service import list_excursions, serialize_excursion


@user_ns.route('/register')
class UserRegister(Resource):
    @user_ns.expect(user_model)
    @user_ns.doc(description="Регистрация обычного пользователя (роль автоматически 'user')")
    def post(self):
        data = request.get_json()
        return register_user("user", data)


@user_ns.route('/login')
class UserLogin(Resource):
    @user_ns.expect(login_model)
    @user_ns.doc(description="Аутентификация обычного пользователя для получения токена доступа")
    def post(self):
        data = request.get_json()
        token = login_user("user", data)
        if token:
            return {"access_token": token}, HTTPStatus.OK
        return {"message": AuthMessages.AUTH_INVALID_CREDENTIALS}, HTTPStatus.UNAUTHORIZED


@user_ns.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    @user_ns.doc(description="Получение информации о пользователе")
    def get(self):
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user)

    @jwt_required()
    @user_ns.expect(change_password_model)
    @user_ns.doc(description="Изменение пароля")
    def put(self):
        data = request.get_json()
        return change_profile_password(data)

    @jwt_required()
    @user_ns.doc(description="Удаление аккаунта")
    def delete(self):
        return delete_profile()


@user_ns.route('/excursions')
class UserExcursionsList(Resource):
    @user_ns.doc(
        description="Список всех активных экскурсий (без авторизации)",
        params={
            'category': 'фильтр по имени категории',
            'event_type': 'фильтр по имени типа события',
            'tags': 'фильтр по тегам, через запятую',
            'min_duration': 'мин. продолжительность, минуты',
            'max_duration': 'макс. продолжительность, минуты',
            'title': 'часть названия',
            'sort': 'имя поля для сортировки, допустимо "-duration", "title"'
        }
    )
    def get(self):
        args = request.args
        filters = {
            'category': args.get('category'),
            'event_type': args.get('event_type'),
            'tags': args.get('tags'),
            'min_duration': args.get('min_duration'),
            'max_duration': args.get('max_duration'),
            'title': args.get('title'),
        }
        sort = args.get('sort')
        excursions = list_excursions(filters, sort)
        return {
            "excursions": [serialize_excursion(excursion) for excursion in excursions]
        }, HTTPStatus.OK