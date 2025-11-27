from datetime import timedelta, datetime
from http import HTTPStatus
from urllib.parse import urlencode, quote_plus

from flask import Response
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource

from . import user_ns
from backend.core.schemas.event_schemas import reservation_model, cancel_model
from ...core.utilits.file_utils import create_ical_from_reservation
from backend.core.services.event_services.event_crud import get_event
from backend.core.services.reservation_service.reservation_queries import get_reservations_by_user_email, \
    get_reservations_by_reservation_id
from backend.core.services.reservation_service.reservation_cancel import cancel_user_reservation
from backend.core.services.reservation_service.reservation_crud import create_reservation_with_payment


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
