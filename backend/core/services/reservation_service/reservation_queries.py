from typing import Tuple, Optional, List, Dict

from backend.core.models.auth_models import User
from backend.core.models.event_models import Reservation
from backend.core.services.user_services.user_service import get_user_by_email


def get_reservations_by_user_email(email: str) -> Tuple[Optional[List['Reservation']], Optional['User']]:
    """
    Получение всех бронирований пользователя по email.

    :param email: email пользователя
    :return: кортеж (список бронирований или None, объект User или None)
    """
    user = get_user_by_email(email)
    if not user:
        return None, None

    reservations = Reservation.query.filter_by(user_id=user.user_id).all()
    return reservations, user


def get_reservations_by_reservation_id(reservation_id: int) -> Optional['Reservation']:
    """
    Получение бронирования по его ID.

    :param reservation_id: ID бронирования
    :return: объект Reservation или None, если не найден
    """
    return Reservation.query.filter_by(reservation_id=reservation_id).first()


def get_all_reservations() -> List[Dict]:
    """
    Получает все бронирования.

    :return: Список словарей с данными всех бронирований
    """
    reservations = Reservation.query.all()
    return [r.to_dict() for r in reservations]


def get_reservation_by_id(reservation_id: int) -> Optional[Dict]:
    """
    Получает подробное бронирование по ID.

    :param reservation_id: ID бронирования
    :return: Словарь с подробной информацией о бронировании или None, если не найдено
    """
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return None
    return reservation.to_dict_detailed()
