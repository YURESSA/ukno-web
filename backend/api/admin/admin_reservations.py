from http import HTTPStatus

from flask import request, send_file

from backend.api.errors import ApiResource
from backend.core.errors import ValidationError
from . import admin_ns
from .decorators import admin_required
from backend.core.services.reservation_service.reservation_queries import get_all_reservations, get_reservation_by_id
from backend.core.services.reservation_service.reservation_crud import delete_reservation_with_refund
from backend.core.services.reservation_service.reservation_queries import filtered_reservations
from backend.core.services.reservation_service.reservation_export import export_reservations


RESERVATION_PARAMS = {
    'event_id': 'ID события', 'session_id': 'ID сеанса', 'user_id': 'ID пользователя',
    'date_from': 'Дата сеанса от, YYYY-MM-DD (включительно)',
    'date_to': 'Дата сеанса до, YYYY-MM-DD (включительно)',
    'booked_from': 'Дата создания брони от, YYYY-MM-DD (включительно)',
    'booked_to': 'Дата создания брони до, YYYY-MM-DD (включительно)',
    'is_paid': 'true/false или 1/0', 'is_cancelled': 'true/false или 1/0',
    'payment_status': 'unpaid, pending, waiting_for_capture, succeeded, canceled',
    'q': 'Поиск по ФИО, телефону или email', 'format': 'json (по умолчанию) или xlsx',
}


def reservation_excel_response():
    return send_file(
        export_reservations(filtered_reservations(request.args)), as_attachment=True,
        download_name='reservations.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@admin_ns.route('/reservations')
class AdminReservationsResource(ApiResource):
    @admin_required
    @admin_ns.doc(params=RESERVATION_PARAMS)
    def get(self):
        """
        Получение списка всех броней (только для администратора).

        :return: JSON с массивом всех броней и HTTP-статус 200
        """
        output_format = request.args.get('format', 'json')
        if output_format == 'xlsx':
            return reservation_excel_response()
        if output_format != 'json':
            raise ValidationError('format: допустимы json или xlsx')
        reservations_data = get_all_reservations(request.args)
        return {'reservations': reservations_data}, HTTPStatus.OK


@admin_ns.route('/reservations/export')
class AdminReservationsExportResource(ApiResource):
    @admin_required
    @admin_ns.doc(params={key: value for key, value in RESERVATION_PARAMS.items() if key != 'format'})
    def get(self):
        """Выгрузка всех подходящих под фильтры броней в Excel."""
        return reservation_excel_response()


@admin_ns.route('/reservations/<int:reservation_id>')
class AdminReservationDetailResource(ApiResource):
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
