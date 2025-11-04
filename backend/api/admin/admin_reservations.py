from http import HTTPStatus

from flask_restx import Resource

from . import admin_ns
from .decorators import admin_required
from backend.core.services.reservation_service.reservation_queries import get_all_reservations, get_reservation_by_id
from backend.core.services.reservation_service.reservation_crud import delete_reservation_with_refund


@admin_ns.route('/reservations')
class AdminReservationsResource(Resource):
    @admin_required
    def get(self) -> tuple[dict, int]:
        """
        Получение списка всех броней (только для администратора).

        :return: JSON с массивом всех броней и HTTP-статус 200
        """
        reservations_data = get_all_reservations()
        return {'reservations': reservations_data}, HTTPStatus.OK


@admin_ns.route('/reservations/<int:reservation_id>')
class AdminReservationDetailResource(Resource):
    @admin_required
    def get(self, reservation_id: int) -> tuple[dict, int]:
        """
        Получение информации о конкретной брони по ID.

        :param reservation_id: Идентификатор брони
        :return: JSON с данными брони или сообщение об ошибке, если бронь не найдена
        """
        reservation_data = get_reservation_by_id(reservation_id)
        if not reservation_data:
            return {'message': 'Бронь не найдена'}, HTTPStatus.NOT_FOUND
        return {'reservation': reservation_data}, HTTPStatus.OK

    @admin_required
    def delete(self, reservation_id: int) -> tuple[dict, int]:
        """
        Удаление брони с возможным возвратом средств (только для администратора).

        :param reservation_id: Идентификатор брони
        :return: JSON с сообщением об успешном удалении или ошибке и соответствующий HTTP-статус
        """
        success, message, status_code = delete_reservation_with_refund(reservation_id)
        return {"message": message}, status_code
