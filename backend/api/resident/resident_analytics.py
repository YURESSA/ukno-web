from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource

from backend.core.services.event_services.event_analytics import get_resident_event_analytics
from . import resident_ns
from .decorators import resident_required
from ...core.services.user_services.user_service import get_user_by_email


@resident_ns.route('/analytics')
class ExcursionAnalytics(Resource):
    @resident_required
    @resident_ns.doc(description="Аналитика по экскурсиям резидента (кол-во посетителей, популярность и т.д.)")
    def get(self) -> tuple[dict, int]:
        """
        Получение аналитических данных по экскурсиям текущего резидента.

        :return: Словарь с данными аналитики и HTTP-статус.
        """
        resident_id: int = get_user_by_email(get_jwt_identity()).user_id
        analytics_data: dict = get_resident_event_analytics(resident_id)
        return analytics_data, HTTPStatus.OK
