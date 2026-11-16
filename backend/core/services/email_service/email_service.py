import logging
import re
from urllib.parse import urlencode

from backend.core.config import Config
from backend.core.services.email_service.templates import render_email
from backend.core.utilits.token_utils import generate_reset_token
from backend.core.utilits.email_utils import send_email
from backend.core.utilits.file_utils import create_ical_from_reservation


logger = logging.getLogger(__name__)


def _send(name, recipient, context, attachments=None, suppress_errors=True):
    message = render_email(name, context)
    try:
        send_email(recipient=recipient, attachments=attachments, **message)
    except Exception:
        if not suppress_errors:
            raise
        logger.exception('Email delivery failed: %s', name)


def _reservation_context(reservation):
    session = reservation.session
    event = session.event if session else None
    payment = getattr(reservation, 'payment', None)
    return {
        'display_name': reservation.full_name or reservation.email,
        'reservation_id': getattr(reservation, 'reservation_id', None),
        'session_id': getattr(session, 'session_id', None),
        'session_start': session.start_datetime if session else None,
        'event_title': event.title if event else None,
        'place': event.place if event else None,
        'contact_email': getattr(event, 'contact_email', None),
        'has_refund': bool(payment and payment.status == 'succeeded'),
    }


def send_reservation_confirmation_email(reservation, user):
    recipient = reservation.email or user.email
    context = _reservation_context(reservation)
    context.update(display_name=reservation.full_name or recipient, participants_count=reservation.participants_count)
    _send('reservation_confirmation', recipient, context,
          attachments=[('reservation.ics', create_ical_from_reservation(reservation), 'text/calendar')])


def send_reservation_cancellation_email(user, reservation):
    context = _reservation_context(reservation)
    context['display_name'] = user.full_name or user.email
    _send('reservation_cancellation', user.email, context)


def send_event_deletion_email(resident, event, csv_data):
    context = {'display_name': getattr(resident, 'full_name', None), 'event_title': event.title}
    title_slug = re.sub(r'\W+', '_', event.title.lower())
    filename = f'отменённые_бронирования_{title_slug}.csv'
    _send('event_deletion', resident.email, context, attachments=[(filename, csv_data)])


def send_session_cancellation_email(reservation, event_name, session):
    context = _reservation_context(reservation)
    context.update(event_title=event_name, session_id=session.session_id, session_start=session.start_datetime)
    recipient = reservation.email or (reservation.user.email if getattr(reservation, 'user', None) else None)
    _send('session_cancellation', recipient, context)


def send_session_deletion_email(deleter_email, event_name, session_id, csv_data):
    context = {'event_title': event_name, 'session_id': session_id}
    event_slug = re.sub(r'\W+', '_', event_name.lower())
    filename = f'отменённые_бронирования_{event_slug}_сессия_{session_id}.csv'
    _send('session_deletion', deleter_email, context, attachments=[(filename, csv_data)])


def send_reservation_refund_email(reservation):
    context = _reservation_context(reservation)
    payment = reservation.payment
    context.update(amount=payment.amount if payment else None, currency=payment.currency if payment else 'RUB')
    recipient = reservation.email or (reservation.user.email if getattr(reservation, 'user', None) else None)
    _send('reservation_refund', recipient, context)


def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = f"{Config.FRONTEND_URL.rstrip('/')}/reset-password?{urlencode({'token': token})}"
    _send('password_reset', user.email, {'display_name': user.full_name or user.email, 'reset_url': reset_url},
          suppress_errors=False)
