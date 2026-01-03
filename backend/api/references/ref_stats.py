from flask_restx import Resource

from backend.api.references import ref_ns
from backend.core.services.ref_service.excursion_stats_service import get_excursion_stats


@ref_ns.route('/excursion-stats')
class ExcursionStats(Resource):
    @ref_ns.doc(description="Получить статистику экскурсий: стоимость, время, расстояние, роли, возрастные категории,"
                            " форматы и категории")
    def get(self) -> tuple[dict, int]:
        """
        Получение сводной статистики для фильтров на фронтенде.

        Returns:
            dict: Статистика по экскурсиям и справочникам:
                - cost: минимальная и максимальная стоимость сессий
                - distance_to_center: минимальное и максимальное расстояние до центра
                - time_to_stop: минимальное и максимальное время до ближайшей остановки
                - roles: список ролей пользователей
                - age_categories: список возрастных категорий
                - format_types: список типов форматов экскурсий
                - categories: список категорий экскурсий
            int: HTTP статус код (200)
        """
        stats = get_excursion_stats()
        return stats, HTTPStatus.OK
