"""Opaque reservation tickets and atomic, idempotent group admissions."""
import re
from datetime import datetime, timezone
from io import BytesIO
from secrets import token_urlsafe
from uuid import UUID

from sqlalchemy import or_, update
from sqlalchemy.exc import IntegrityError

from backend.core import db
from backend.core.errors import ApiError, NotFoundError, ValidationError
from backend.core.models.event_models import Event, EventSession, Reservation, ReservationAdmission


QR_PREFIX = 'ukno:ticket:v1:'


class TicketConflict(ApiError):
    status_code = 409


def positive_integer(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 < value <= 2147483647:
        raise ValidationError(f'{field}: укажите положительное целое число')
    return value


def _token(payload):
    if not isinstance(payload, str):
        raise ValidationError('ticket: передайте содержимое QR-кода')
    token = payload[len(QR_PREFIX):] if payload.startswith(QR_PREFIX) else payload
    if not re.fullmatch(r'[A-Za-z0-9_-]{43}', token):
        raise ValidationError('Некорректный формат билета')
    return token


def _find_ticket(payload):
    reservation = Reservation.query.filter_by(ticket_token=_token(payload)).populate_existing().first()
    if not reservation:
        raise NotFoundError('Билет не найден')
    return reservation


def ticket_summary(reservation, session_id=None):
    session = reservation.session
    event = session.event if session else None
    remaining = max(0, reservation.participants_count - reservation.checked_in_count)
    if reservation.is_cancelled:
        status = 'cancelled'
    elif not session or not event or not event.is_active or event.moderation_status != 'approved':
        status = 'unavailable'
    elif session_id is not None and session.session_id != session_id:
        status = 'wrong_session'
    elif session.cost > 0 and not reservation.is_paid:
        status = 'unpaid'
    elif remaining == 0:
        status = 'fully_used'
    elif reservation.checked_in_count:
        status = 'partially_used'
    else:
        status = 'valid'
    return {
        'reservation_id': reservation.reservation_id,
        'session_id': reservation.session_id,
        'event_id': event.event_id if event else None,
        'event_title': event.title if event else None,
        'session_start_datetime': session.start_datetime.isoformat() if session else None,
        'full_name': reservation.full_name,
        'participants_count': reservation.participants_count,
        'checked_in_count': reservation.checked_in_count,
        'remaining_count': remaining,
        'status': status,
        'can_enter': status in ('valid', 'partially_used'),
    }


def issue_ticket(reservation):
    summary = ticket_summary(reservation)
    if summary['status'] not in ('valid', 'partially_used', 'fully_used'):
        raise TicketConflict('Билет недоступен: бронь отменена, не оплачена или событие недоступно')
    if not reservation.ticket_token:
        # Existing reservations get one stable token, even with concurrent retrievals.
        db.session.execute(update(Reservation).where(
            Reservation.reservation_id == reservation.reservation_id,
            Reservation.ticket_token.is_(None),
        ).values(ticket_token=token_urlsafe(32)))
        db.session.commit()
        db.session.refresh(reservation)
    return {
        **summary,
        'qr_payload': QR_PREFIX + reservation.ticket_token,
        'qr_svg_url': f'/api/user/reservations/{reservation.reservation_id}/ticket/qr',
    }


def ticket_svg(reservation):
    import qrcode
    from qrcode.image.svg import SvgPathFillImage

    payload = issue_ticket(reservation)['qr_payload']
    image = qrcode.make(payload, image_factory=SvgPathFillImage, border=4)
    output = BytesIO()
    image.save(output)
    return output.getvalue()


def qr_png(payload):
    """PNG works in mail clients; encode exactly the same payload as the SVG/API ticket."""
    import qrcode
    from qrcode.image.pure import PyPNGImage

    output = BytesIO()
    qrcode.make(payload, image_factory=PyPNGImage, box_size=8, border=4).save(output)
    return output.getvalue()


def ticket_png(reservation):
    return qr_png(issue_ticket(reservation)['qr_payload'])


def check_ticket(payload, session_id=None):
    if session_id is not None:
        positive_integer(session_id, 'session_id')
    return ticket_summary(_find_ticket(payload), session_id)


def admission_data(admission):
    timestamp = admission.admitted_at
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return {
        'admission_id': admission.admission_id,
        'request_id': admission.request_id,
        'participants_count': admission.participants_count,
        'admin_user_id': admission.admin_user_id,
        'admitted_at': timestamp.isoformat(),
    }


def _previous_admission(reservation, request_id, count, session_id):
    previous = ReservationAdmission.query.filter_by(
        reservation_id=reservation.reservation_id, request_id=request_id,
    ).first()
    if previous:
        if previous.participants_count != count or reservation.session_id != session_id:
            raise TicketConflict('request_id уже использован с другими параметрами')
        return {'ticket': ticket_summary(reservation, session_id),
                'admission': admission_data(previous), 'replayed': True}
    return None


def admit_ticket(payload, session_id, count, request_id, admin_user_id):
    positive_integer(session_id, 'session_id')
    positive_integer(count, 'count')
    try:
        if not isinstance(request_id, str) or str(UUID(request_id)) != request_id:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise ValidationError('request_id: укажите UUID в стандартном формате')
    reservation = _find_ticket(payload)
    previous = _previous_admission(reservation, request_id, count, session_id)
    if previous:
        return previous
    summary = ticket_summary(reservation, session_id)
    if not summary['can_enter']:
        raise TicketConflict(f"Вход недоступен: {summary['status']}")
    reservation_id = reservation.reservation_id
    try:
        # Conditional arithmetic update serializes competing scans at the database.
        # The capacity, cancellation and payment predicates are rechecked under the row lock.
        result = db.session.execute(update(Reservation).where(
            Reservation.reservation_id == reservation_id,
            Reservation.session_id == session_id,
            Reservation.is_cancelled.is_(False),
            Reservation.checked_in_count <= Reservation.participants_count - count,
            or_(Reservation.is_paid.is_(True), Reservation.session.has(EventSession.cost == 0)),
            Reservation.session.has(EventSession.event.has(
                (Event.is_active.is_(True)) & (Event.moderation_status == 'approved')
            )),
        ).values(checked_in_count=Reservation.checked_in_count + count).execution_options(synchronize_session=False))
        if result.rowcount != 1:
            db.session.rollback()
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation:
                raise NotFoundError('Билет не найден')
            previous = _previous_admission(reservation, request_id, count, session_id)
            if previous:
                return previous
            raise TicketConflict('Недостаточно оставшихся мест или билет больше недействителен')
        admission = ReservationAdmission(
            reservation_id=reservation_id, admin_user_id=admin_user_id, request_id=request_id,
            participants_count=count, admitted_at=datetime.now(timezone.utc),
        )
        db.session.add(admission)
        db.session.commit()
    except IntegrityError:
        # A simultaneous retry may have the same request_id. Its entire increment
        # is rolled back; the original, already committed admission is returned.
        db.session.rollback()
        reservation = db.session.get(Reservation, reservation_id)
        if reservation:
            previous = _previous_admission(reservation, request_id, count, session_id)
            if previous:
                return previous
        raise
    except Exception:
        db.session.rollback()
        raise
    db.session.refresh(reservation)
    return {'ticket': ticket_summary(reservation, session_id),
            'admission': admission_data(admission), 'replayed': False}
