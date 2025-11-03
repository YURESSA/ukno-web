from datetime import datetime, timedelta
from http import HTTPStatus
from urllib.parse import urlencode, quote_plus

from flask import Response
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, fields

from backend.core.schemas.auth_schemas import user_model, change_password_model, edit_profile_model
from backend.core.services.event_services.event_service import list_events, get_event
from . import user_ns
from ..core import db
from ..core.models.news_models import News
from ..core.schemas.event_schemas import reservation_model, cancel_model
from ..core.schemas.user_schemas import user_login
from ..core.services.calendar_utilits import create_ical_from_reservation
from ..core.services.email_service import send_reset_email
from ..core.services.reservation_service import get_reservations_by_user_email, create_reservation_with_payment, \
    cancel_user_reservation, get_reservations_by_reservation_id
from ..core.services.user_services.auth_service import get_user_by_email, update_profile, change_profile_password
from ..core.services.user_services.profile_service import register_user, login_user, get_profile, \
    get_user_info_response, delete_profile
from ..core.services.utilits import verify_reset_token


@user_ns.route('/register')
class UserRegister(Resource):
    @user_ns.expect(user_model)
    @user_ns.doc(description="Регистрация обычного пользователя (роль автоматически 'user')")
    def post(self) -> tuple[dict, int]:
        """
        Регистрация нового пользователя.

        :return: Возвращает словарь с данными зарегистрированного пользователя и статус HTTP.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        data = request.get_json()
        return register_user("user", data)


@user_ns.route('/login')
class UserLogin(Resource):
    @user_ns.expect(user_login)
    @user_ns.doc(description="Аутентификация обычного пользователя для получения токена доступа")
    def post(self) -> tuple[dict, int]:
        """
        Вход пользователя и получение JWT-токена.

        :return: Возвращает словарь с JWT-токеном и статус HTTP.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        data = request.get_json() or {}
        response, status = login_user("user", data)
        return response, status


@user_ns.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    @user_ns.doc(description="Получение информации о текущем пользователе")
    def get(self) -> tuple[dict, int]:
        """
        Получение профиля текущего пользователя.

        :return: Возвращает словарь с данными пользователя и HTTP-статус.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        user, error, status = get_profile()
        if error:
            return error, status
        return get_user_info_response(user)

    @jwt_required()
    @user_ns.expect(edit_profile_model)
    @user_ns.doc(description="Редактирование профиля текущего пользователя")
    def put(self) -> tuple[dict, int]:
        """
        Редактирование профиля текущего пользователя.

        :return: Возвращает обновлённые данные пользователя и HTTP-статус.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        data = request.get_json()
        response, status = update_profile(data)
        return response, status

    @jwt_required()
    @user_ns.doc(description="Удаление аккаунта текущего пользователя")
    def delete(self) -> tuple[dict, int]:
        """
        Удаление аккаунта текущего пользователя.

        :return: Возвращает сообщение об успешном удалении и HTTP-статус.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        response, status = delete_profile()
        return response, status


@user_ns.route('/profile/password')
class ChangePassword(Resource):
    @jwt_required()
    @user_ns.expect(change_password_model)
    @user_ns.doc(description="Смена пароля текущего пользователя")
    def put(self) -> tuple[dict, int]:
        """
        Смена пароля текущего пользователя.

        :return: Возвращает сообщение об успешной смене пароля и HTTP-статус.
                 В случае ошибки — словарь с сообщением об ошибке и соответствующий статус.
        """
        data = request.get_json()
        response, status = change_profile_password(data)
        return response, status


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
    def get(self) -> tuple[dict, int]:
        """
        Получение списка активных экскурсий с возможностью фильтрации и сортировки.

        Все параметры опциональны. Если фильтры не указаны, возвращаются все активные экскурсии.

        :return: Словарь с ключом "excursions", содержащим список экскурсий, и HTTP-статус.
        """
        args: dict = request.args
        filters: dict = {
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
        sort: str | None = args.get('sort')

        excursions: list = list_events(filters, sort)

        return {
            "excursions": [excursion.to_dict() for excursion in excursions]
        }, HTTPStatus.OK


@user_ns.route('/password-reset-request')
class PasswordResetRequest(Resource):
    password_reset_request_model = user_ns.model(
        "PasswordResetRequest",
        {
            "email": fields.String(required=True, description="Email пользователя")
        }
    )

    @user_ns.expect(password_reset_request_model, validate=True)
    @user_ns.doc(description="Запрос на сброс пароля: отправка инструкции на email")
    def post(self) -> tuple[dict, int]:
        """
        Обрабатывает запрос на сброс пароля.

        Всегда возвращает успешный ответ, чтобы не раскрывать существование пользователя.

        :return: Словарь с сообщением об отправке инструкции и HTTP-статус.
        """
        data: dict = request.get_json() or {}
        email: str | None = data.get("email")

        user = get_user_by_email(email)
        if user:
            send_reset_email(user)

        return {
            "message": "Если пользователь существует, инструкция отправлена на почту"
        }, HTTPStatus.OK


@user_ns.route('/password-reset')
class PasswordReset(Resource):
    password_reset_model = user_ns.model(
        "PasswordReset",
        {
            "token": fields.String(required=True, description="Токен из email"),
            "new_password": fields.String(required=True, description="Новый пароль")
        }
    )

    @user_ns.expect(password_reset_model, validate=True)
    @user_ns.doc(description="Сброс пароля по токену, без авторизации JWT")
    def post(self) -> tuple[dict, int]:
        """
        Сбрасывает пароль пользователя по токену.

        :return: В случае успешного сброса — сообщение об успешной операции и HTTPStatus.OK.
                 Если токен недействителен — сообщение об ошибке и HTTPStatus.BAD_REQUEST.
                 Если пользователь не найден — сообщение об ошибке и HTTPStatus.NOT_FOUND.
        """
        data: dict = request.get_json() or {}
        token: str | None = data.get("token")
        new_password: str | None = data.get("new_password")

        email: str | None = verify_reset_token(token)
        if not email:
            return {"message": "Неверный или просроченный токен"}, HTTPStatus.BAD_REQUEST

        user = get_user_by_email(email)
        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

        user.set_password(new_password)
        db.session.commit()

        return {"message": "Пароль успешно сброшен"}, HTTPStatus.OK


@user_ns.route('/reservations')
class Reservations(Resource):
    @jwt_required()
    @user_ns.doc(description="Получение списка своих бронирований пользователя")
    def get(self) -> tuple[dict, int]:
        """
        Получение списка всех бронирований текущего пользователя.

        :return: Словарь с ключом "reservations", содержащим список бронирований,
                 и HTTP-статус. Если пользователь не найден — сообщение об ошибке и HTTPStatus.UNAUTHORIZED.
        """
        email: str = get_jwt_identity()
        reservations, user = get_reservations_by_user_email(email)

        if not user:
            return {"message": "Пользователь не найден"}, HTTPStatus.UNAUTHORIZED

        return {
            "reservations": [r.to_dict_detailed() for r in reservations]
        }, HTTPStatus.OK


@user_ns.route('/v2/reservations')
class ReservationCreate(Resource):
    @jwt_required()
    @user_ns.expect(reservation_model, validate=True)
    @user_ns.doc(description="Запись на сеанс экскурсии через оплату")
    def post(self) -> tuple[dict, int]:
        """
        Создает бронь на сеанс экскурсии с оплатой.

        Использует данные пользователя из JWT (email) и информацию о бронировании из тела запроса.

        :return: Словарь с результатом операции и HTTP-статус.
        """
        data: dict = request.get_json() or {}

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
    @user_ns.expect(cancel_model, validate=True)
    @user_ns.doc(description="Отмена своего бронирования с возвратом средств")
    def delete(self) -> tuple[dict, int]:
        """
        Отменяет бронь пользователя и инициирует возврат средств.

        Использует email пользователя из JWT и ID бронирования из тела запроса.

        :return: Словарь с результатом отмены и HTTP-статус.
        """
        data: dict = request.get_json() or {}
        reservation_id: int | None = data.get('reservation_id')

        response, status = cancel_user_reservation(
            user_email=get_jwt_identity(),
            reservation_id=reservation_id
        )

        return response, status


@user_ns.route('/reservations/<int:reservation_id>/export_ical')
class ExportReservationICal(Resource):
    def get(self, reservation_id):
        """
        Генерирует iCal файл для указанного бронирования.

        Args:
            reservation_id (int): ID бронирования.

        Returns:
            Response: iCal файл с заголовком для скачивания.
            Или кортеж (dict, int) с сообщением об ошибке, если бронирование не найдено.
        """
        reservation = get_reservations_by_reservation_id(reservation_id)
        if not reservation:
            return {"message": "Бронирование не найдено"}, 404

        ical_bytes = create_ical_from_reservation(reservation)

        return Response(
            ical_bytes,
            mimetype="text/calendar",
            headers={
                "Content-Disposition": 'attachment; filename="reservation.ics"'
            }
        )


@user_ns.route('/reservations/<int:reservation_id>/google_calendar_link')
class GoogleCalendarLink(Resource):
    def get(self, reservation_id):
        """
        Генерирует ссылку для добавления бронирования в Google Calendar.

        Args:
            reservation_id (int): ID бронирования.

        Returns:
            dict: Словарь с ключом 'google_calendar_link'.
            tuple: (dict, int) с сообщением об ошибке, если бронирование не найдено.
        """
        reservation = get_reservations_by_reservation_id(reservation_id)
        if not reservation:
            return {"message": "Бронирование не найдено"}, 404

        title = f"Экскурсия: {reservation.session.event.title}"
        start = reservation.session.start_datetime.strftime('%Y%m%dT%H%M%S')
        end_dt = reservation.session.start_datetime + timedelta(minutes=reservation.session.event.duration)
        end = end_dt.strftime('%Y%m%dT%H%M%S')

        query = {
            "action": "TEMPLATE",
            "text": title,
            "dates": f"{start}/{end}",
            "details": f"Участников: {reservation.participants_count}",
            "location": reservation.session.event.place,
        }

        link = f"https://calendar.google.com/calendar/render?{urlencode(query, quote_via=quote_plus)}"
        return {"google_calendar_link": link}


@user_ns.route('/news')
class NewsList(Resource):
    @user_ns.doc(description="Список всех новостей (без авторизации)")
    def get(self):
        """
        Возвращает список всех новостей, отсортированных по дате создания по убыванию.

        Returns:
            dict: Словарь с ключом 'news', содержащий список новостей.
        """
        news_list = News.query.order_by(News.created_at.desc()).all()
        return {
            "news": [n.to_dict() for n in news_list]
        }, HTTPStatus.OK


@user_ns.route('/excursions_detail/<int:excursion_id>')
class DetailExcursion(Resource):
    def get(self, excursion_id):
        """
        Возвращает полную информацию об экскурсии, включая предстоящие сеансы.

        Args:
            excursion_id (int): ID экскурсии.

        Returns:
            dict: Информация об экскурсии.
            tuple: Словарь с сообщением об ошибке и HTTP статус, если экскурсия не найдена.
        """
        excursion = get_event(excursion_id)

        if not excursion:
            return {"message": "Экскурсия не найдена"}, HTTPStatus.NOT_FOUND

        now = datetime.now()
        excursion.sessions = [s for s in excursion.sessions if s.start_datetime > now]

        return excursion.to_dict(), HTTPStatus.OK


@user_ns.route('/news/<int:news_id>')
class NewsDetail(Resource):
    @user_ns.doc(description="Детальный просмотр новости по ID (без авторизации)")
    def get(self, news_id):
        """
        Возвращает полную информацию о конкретной новости.

        Args:
            news_id (int): ID новости.

        Returns:
            dict: Информация о новости.
            tuple: Словарь с сообщением об ошибке и HTTP статус, если новость не найдена.
        """
        news = News.query.get(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
        return news.to_dict(), HTTPStatus.OK
