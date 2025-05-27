from datetime import datetime

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource
from sqlalchemy import func

from backend.core.schemas.auth_schemas import login_model, user_model, change_password_model
from backend.core.services.profile_service import *
from . import user_ns
from ..core.models.excursion_models import Reservation, ExcursionSession
from ..core.models.news_models import News
from ..core.schemas.excursion_schemas import reservation_model, cancel_model
from ..core.services.excursion_service import list_excursions, get_excursion


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
            return {"access_token": token, "role": "user"}, HTTPStatus.OK
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
            'category': 'Фильтр по имени категории (можно несколько через запятую)',
            'format_type': 'Фильтр по типу формата (можно несколько через запятую)',
            'age_category': 'Фильтр по возрастной категории (можно несколько через запятую)',
            'tags': 'Фильтр по тегам, через запятую',
            'min_duration': 'Минимальная продолжительность, минуты',
            'max_duration': 'Максимальная продолжительность, минуты',
            'min_distance_to_center': 'Мин. расстояние до центра, км',
            'max_distance_to_center': 'Макс. расстояние до центра, км',
            'min_distance_to_stop': 'Мин. расстояние до остановки, мин',
            'max_distance_to_stop': 'Макс. расстояние до остановки, мин',
            'min_price': 'Минимальная стоимость ближайшей сессии',
            'max_price': 'Максимальная стоимость ближайшей сессии',
            'start_date': 'Дата начала периода (ISO 8601, например 2025-06-01)',
            'end_date': 'Дата конца периода (ISO 8601, например 2025-06-30)',
            'title': 'Поиск по названию',
            'sort': (
                    'Сортировка: title, duration, price, time. '
                    'Можно с -, например: -price, -time'
            )
        }
    )
    def get(self):
        args = request.args
        filters = {
            'category': args.get('category'),
            'format_type': args.get('format_type'),
            'age_category': args.get('age_category'),
            'tags': args.get('tags'),
            'min_duration': args.get('min_duration'),
            'max_duration': args.get('max_duration'),
            'min_distance_to_center': args.get('min_distance_to_center'),
            'max_distance_to_center': args.get('max_distance_to_center'),
            'min_distance_to_stop': args.get('min_distance_to_stop'),
            'max_distance_to_stop': args.get('max_distance_to_stop'),
            'min_price': args.get('min_price'),
            'max_price': args.get('max_price'),
            'start_date': args.get('start_date'),
            'end_date': args.get('end_date'),
            'title': args.get('title'),
        }
        sort = args.get('sort')
        excursions = list_excursions(filters, sort)
        return {
            "excursions": [excursion.to_dict() for excursion in excursions]
        }, HTTPStatus.OK


@user_ns.route('/reservations')
class Reservations(Resource):
    @jwt_required()
    @user_ns.doc(description="Список своих бронирований")
    def get(self):
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()

        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED

        reservations = Reservation.query.filter_by(user_id=user.user_id).all()

        return {
            "reservations": [
                {
                    "reservation_id": r.reservation_id,
                    "excursion_id": r.session.excursion.excursion_id,
                    "session_id": r.session_id,
                    "excursion_title": r.session.excursion.title,
                    "start_datetime": r.session.start_datetime.isoformat(),
                    "cost": str(r.session.cost),
                    "booked_at": r.booked_at.isoformat() if r.booked_at else None,
                    "full_name": r.full_name,
                    "phone_number": r.phone_number,
                    "email": r.email,
                    "participants_count": r.participants_count,
                    "is_cancelled": r.is_cancelled
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
        full_name = data.get('full_name')
        phone_number = data.get('phone_number')
        email = data.get('email')
        participants_count = data.get('participants_count', 1)

        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()

        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED

        if not session_id:
            return {"message": "session_id is required"}, HTTPStatus.BAD_REQUEST

        session = ExcursionSession.query.get(session_id)
        if not session:
            return {"message": "Сеанс не найден"}, HTTPStatus.NOT_FOUND

        existing_participants = db.session.query(
            func.coalesce(func.sum(Reservation.participants_count), 0)
        ).filter_by(session_id=session_id, is_cancelled=False).scalar()

        if existing_participants + participants_count > session.max_participants:
            return {"message": "Недостаточно свободных мест"}, HTTPStatus.BAD_REQUEST

        r = Reservation(
            session_id=session_id,
            user_id=user.user_id,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            participants_count=participants_count,
            booked_at=datetime.utcnow(),
            is_cancelled=False
        )
        db.session.add(r)
        db.session.commit()

        return {
            "message": "Бронирование успешно",
            "reservation_id": r.reservation_id
        }, HTTPStatus.CREATED

    @jwt_required()
    @user_ns.expect(cancel_model)
    @user_ns.doc(description="Отмена своего бронирования")
    def delete(self):
        data = request.get_json() or {}
        reservation_id = data.get('reservation_id')
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()

        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED

        if not reservation_id:
            return {"message": "reservation_id is required"}, HTTPStatus.BAD_REQUEST

        reservation = Reservation.query.get(reservation_id)
        if not reservation or reservation.user_id != user.user_id:
            return {"message": "Бронирование не найдено или не принадлежит вам"}, HTTPStatus.NOT_FOUND

        reservation.is_cancelled = True
        db.session.commit()

        return {"message": "Бронирование отменено"}, HTTPStatus.OK


@user_ns.route('/news')
class NewsList(Resource):
    @user_ns.doc(description="Список всех новостей (без авторизации)")
    def get(self):
        news_list = News.query.order_by(News.created_at.desc()).all()
        return {
            "news": [n.to_dict() for n in news_list]
        }, HTTPStatus.OK


@user_ns.route('/excursions_detail/<int:excursion_id>')
class DetailExcursion(Resource):
    def get(self, excursion_id):
        excursion = get_excursion(excursion_id)

        if not excursion:
            return {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND

        now = datetime.now()
        excursion.sessions = [s for s in excursion.sessions if s.start_datetime > now]

        return excursion.to_dict(), HTTPStatus.OK


@user_ns.route('/news/<int:news_id>')
class NewsDetail(Resource):
    @user_ns.doc(description="Детальный просмотр новости по ID (без авторизации)")
    def get(self, news_id):
        news = News.query.get(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
        return news.to_dict(), HTTPStatus.OK
