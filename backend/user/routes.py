from datetime import datetime

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields

from backend.core.schemas.auth_schemas import login_model, user_model, change_password_model, edit_profile_model
from backend.core.services.excursion_services.excursion_service import list_excursions, get_excursion
from backend.core.services.user_services.profile_service import *
from . import user_ns
from ..core.models.news_models import News
from ..core.schemas.excursion_schemas import reservation_model, cancel_model
from ..core.services.email_service import send_reset_email
from ..core.services.reservation_service import get_reservations_by_user_email, create_reservation_with_payment, \
    cancel_user_reservation
from ..core.services.utilits import verify_reset_token


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
    @user_ns.expect(edit_profile_model)
    @user_ns.doc(description="Редактирование профиля пользователя")
    def put(self):
        data = request.get_json()
        return update_profile(data)

    @jwt_required()
    @user_ns.doc(description="Удаление аккаунта")
    def delete(self):
        return delete_profile()


@user_ns.route('/profile/password')
class ChangePassword(Resource):
    @jwt_required()
    @user_ns.expect(change_password_model)
    @user_ns.doc(description="Смена пароля пользователя")
    def put(self):
        data = request.get_json()
        return change_profile_password(data)


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


@user_ns.route('/password-reset-request')
class PasswordResetRequest(Resource):
    @user_ns.expect(user_ns.model("PasswordResetRequest", {
        "email": fields.String(required=True, description="Email")
    }))
    @user_ns.doc(description="Запрос на сброс пароля (отправка email)")
    def post(self):
        data = request.get_json()
        email = data.get("email")

        user = get_user_by_email(email)
        if not user:
            return {"message": "Если пользователь существует, инструкция отправлена на почту"}, HTTPStatus.OK

        send_reset_email(user)
        return {"message": "Письмо для восстановления пароля отправлено"}, HTTPStatus.OK


@user_ns.route('/password-reset')
class PasswordReset(Resource):
    @user_ns.expect(user_ns.model("PasswordReset", {
        "token": fields.String(required=True, description="Токен из email"),
        "new_password": fields.String(required=True, description="Новый пароль")
    }))
    @user_ns.doc(description="Сброс пароля по токену")
    def post(self):
        data = request.get_json()
        token = data.get("token")
        new_password = data.get("new_password")

        email = verify_reset_token(token)
        if not email:
            return {"message": "Неверный или просроченный токен"}, HTTPStatus.BAD_REQUEST

        user = get_user_by_email(get_jwt_identity())
        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

        user.set_password(new_password)
        db.session.commit()

        return {"message": "Пароль успешно сброшен"}, HTTPStatus.OK


@user_ns.route('/reservations')
class Reservations(Resource):
    @jwt_required()
    @user_ns.doc(description="Список своих бронирований")
    def get(self):
        email = get_jwt_identity()
        reservations, user = get_reservations_by_user_email(email)

        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED
        return {
            "reservations": [r.to_dict_detailed() for r in reservations]
        }, HTTPStatus.OK


@user_ns.route('/v2/reservations')
class Reservations(Resource):
    @jwt_required()
    @user_ns.expect(reservation_model)
    @user_ns.doc(description="Запись на сеанс экскурсии через оплату")
    def post(self):
        data = request.get_json()

        response, status = create_reservation_with_payment(
            user_email=get_jwt_identity(),
            session_id=data.get('session_id'),
            full_name=data.get('full_name'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            participants_count=data.get('participants_count', 1)
        )

        return response, status

    @jwt_required()
    @user_ns.expect(cancel_model)
    @user_ns.doc(description="Отмена своего бронирования с возвратом средств")
    def delete(self):
        print(1)
        data = request.get_json() or {}
        reservation_id = data.get('reservation_id')

        response, status = cancel_user_reservation(
            user_email=get_jwt_identity(),
            reservation_id=reservation_id
        )

        return response, status


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
