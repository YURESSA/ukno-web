from datetime import date, datetime, time, timedelta
from typing import Tuple, Optional, List, Dict

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from backend.core.errors import ValidationError
from backend.core.models.auth_models import User
from backend.core.models.event_models import EventSession, Payment, Reservation
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


def filtered_reservations(filters=None):
    """Shared selection for the existing JSON list and the Excel export."""
    filters = filters or {}
    query = Reservation.query.options(
        joinedload(Reservation.session).joinedload(EventSession.event).lazyload('*'),
        joinedload(Reservation.payment),
    )
    for name, column in (
        ('event_id', EventSession.event_id), ('session_id', Reservation.session_id),
        ('user_id', Reservation.user_id),
    ):
        value = filters.get(name)
        if value is not None:
            text = str(value)
            if len(text) > 10 or not text.isascii() or not text.isdigit() or not 0 < int(text) <= 2147483647:
                raise ValidationError(f'{name}: укажите положительный целочисленный ID')
            condition = column == int(value)
            query = query.filter(Reservation.session.has(condition) if name == 'event_id' else condition)

    for name in ('is_paid', 'is_cancelled'):
        value = filters.get(name)
        if value is not None:
            if str(value).lower() not in ('true', 'false', '1', '0'):
                raise ValidationError(f'{name}: допустимы true, false, 1, 0')
            query = query.filter(getattr(Reservation, name).is_(str(value).lower() in ('true', '1')))

    for prefix, column, related in (
        ('date', EventSession.start_datetime, True), ('booked', Reservation.booked_at, False),
    ):
        bounds = {}
        for suffix in ('from', 'to'):
            name = f'{prefix}_{suffix}'
            value = filters.get(name)
            if value is None:
                continue
            try:
                parsed = date.fromisoformat(value)
                if parsed.isoformat() != value:
                    raise ValueError()
                boundary = datetime.combine(parsed, time.min)
                if suffix == 'to':
                    boundary += timedelta(days=1)
            except (TypeError, ValueError, OverflowError):
                raise ValidationError(f'{name}: укажите дату в формате YYYY-MM-DD')
            bounds[suffix] = parsed
            condition = column >= boundary if suffix == 'from' else column < boundary
            query = query.filter(Reservation.session.has(condition) if related else condition)
        if 'from' in bounds and 'to' in bounds and bounds['from'] > bounds['to']:
            raise ValidationError(f'{prefix}_from не может быть позже {prefix}_to')

    status = filters.get('payment_status')
    if status is not None:
        if status not in ('unpaid', 'pending', 'waiting_for_capture', 'succeeded', 'canceled'):
            raise ValidationError('Неизвестный payment_status')
        condition = Reservation.payment.has(Payment.status == status)
        if status == 'unpaid':
            condition = or_(~Reservation.payment.has(), condition)
        query = query.filter(condition)

    search = filters.get('q')
    if search is not None:
        if len(search) > 255:
            raise ValidationError('q: не более 255 символов')
        search = search.strip()
        if search:
            query = query.filter(or_(*[
                column.icontains(search, autoescape=True)
                for column in (Reservation.full_name, Reservation.email, Reservation.phone_number)
            ]))
    return query


def get_all_reservations(filters=None) -> List[Dict]:
    """
    Получает все бронирования.

    :return: Список словарей с данными всех бронирований
    """
    reservations = filtered_reservations(filters).all()
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
