from datetime import datetime

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from backend.core.schemas.auth_schemas import login_model, user_model, change_password_model
from backend.core.services.profile_service import *
from . import user_ns
from ..core.models.excursion_models import Reservation, ExcursionSession
from ..core.schemas.excursion_schemas import reservation_model, cancel_model
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


@user_ns.route('/reservations')
class Reservations(Resource):
    @jwt_required()
    @user_ns.doc(description="Список своих бронирований")
    def get(self):
        user_id = get_jwt_identity()
        reservations = Reservation.query.filter_by(user_id=user_id).all()

        return {
            "reservations": [
                {
                    "reservation_id": r.reservation_id,
                    "excursion_id": r.session.excursion.excursion_id,
                    "session_id": r.session_id,
                    "excursion_title": r.session.excursion.title,
                    "start_datetime": r.session.start_datetime.isoformat(),
                    "cost": str(r.session.cost),
                    "booked_at": r.booked_at.isoformat()
                }
                for r in reservations
            ]
        }, HTTPStatus.OK

    @jwt_required()
    @user_ns.expect(reservation_model)
    @user_ns.doc(description="Запись на сеанс экскурсии")
    def post(self):
        data = request.get_json()
        session_id = data.get('session_id')
        user_id = get_jwt_identity()

        if not session_id:
            return {"message": "session_id is required"}, HTTPStatus.BAD_REQUEST

        session = ExcursionSession.query.get(session_id)
        if not session:
            return {"message": "Сеанс не найден"}, HTTPStatus.NOT_FOUND

        # Проверка дубликата
        if Reservation.query.filter_by(session_id=session_id, user_id=user_id).first():
            return {"message": "Вы уже записаны на этот сеанс"}, HTTPStatus.CONFLICT

        # Проверка доступных мест
        if Reservation.query.filter_by(session_id=session_id).count() >= session.max_participants:
            return {"message": "Мест на этот сеанс больше нет"}, HTTPStatus.BAD_REQUEST

        # Создание бронирования
        r = Reservation(
            session_id=session_id,
            user_id=user_id,
            booked_at=datetime.utcnow()
        )
        db.session.add(r)
        db.session.commit()
        return {"message": "Бронирование успешно", "reservation_id": r.reservation_id}, HTTPStatus.CREATED

    @jwt_required()
    @user_ns.expect(cancel_model)
    @user_ns.doc(description="Отмена своего бронирования")
    def delete(self):
        data = request.get_json() or {}
        reservation_id = data.get('reservation_id')
        user_id = get_jwt_identity()

        if not reservation_id:
            return {"message": "reservation_id is required"}, HTTPStatus.BAD_REQUEST

        reservation = Reservation.query.get(reservation_id)
        if not reservation or reservation.user_id != user_id:
            return {"message": "Бронирование не найдено"}, HTTPStatus.NOT_FOUND

        db.session.delete(reservation)
        db.session.commit()
        return {"message": "Бронирование отменено"}, HTTPStatus.OK
