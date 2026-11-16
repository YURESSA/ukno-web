from email import policy
from email.parser import BytesParser

import png
import pytest
from flask import Flask
from flask_mail import Mail

from backend.api.webhook.routes import handle_reservation_payment_succeeded
from backend.core import db
from backend.core.models.auth_models import RoleEnum
from backend.core.models.event_models import Payment, Reservation
from backend.core.services.email_service import email_service
from backend.core.services.reservation_service.reservation_crud import create_reservation_with_payment
from backend.core.services.reservation_service.reservation_tickets import QR_PREFIX, issue_ticket
from backend.core.utilits import email_utils
from tests import test_security_regressions as security


app = security.app


@pytest.mark.parametrize('paid_event', [False, True])
def test_confirmation_contains_same_ticket_as_api_for_free_and_paid_booking(app, monkeypatch, paid_event):
    sent = []
    monkeypatch.setattr(email_service, 'send_email', lambda **kwargs: sent.append(kwargs))
    encoded = []
    from backend.core.services.reservation_service import reservation_tickets
    original_png = reservation_tickets.qr_png

    def capture(payload):
        encoded.append(payload)
        return original_png(payload)

    monkeypatch.setattr(reservation_tickets, 'qr_png', capture)
    with app.app_context():
        admin = security.add_user('mail-admin@example.com', RoleEnum.ADMIN)
        owner = security.add_user('mail-owner@example.com')
        session = security.add_session(admin, capacity=10, cost=100 if paid_event else 0)
        if paid_event:
            reservation = Reservation(session=session, user=owner, full_name='Анна', phone_number='+70000000000',
                                      email=owner.email, participants_count=3, is_paid=False, is_cancelled=False)
            db.session.add(reservation)
            db.session.flush()
            payment = Payment(payment_id='confirmation-payment', reservation=reservation, session=session,
                              participants_count=3, email=owner.email, amount=300, status='pending')
            db.session.add(payment)
            db.session.commit()
            assert not sent
            handle_reservation_payment_succeeded({'reservation_id': reservation.reservation_id}, payment.payment_id)
            handle_reservation_payment_succeeded({'reservation_id': reservation.reservation_id}, payment.payment_id)
        else:
            response, status = create_reservation_with_payment(
                owner.email, session.session_id, 'Анна', '+70000000000', owner.email, 3,
            )
            assert status == 201
            reservation = db.session.get(Reservation, response['reservation_id'])
        assert len(sent) == 1
        message = sent[0]
        expected_payload = issue_ticket(reservation)['qr_payload']
        assert encoded == [expected_payload]
        assert expected_payload == QR_PREFIX + reservation.ticket_token
        assert message['recipient'] == owner.email
        filename = f'ticket-{reservation.reservation_id}.png'
        content_id = f'reservation-ticket-{reservation.reservation_id}@5buro.ru'
        assert f'cid:{content_id}' in message['body_html']
        assert filename in message['body']
        attachments = {name: (body, mime) for name, body, mime in message['attachments']}
        image, mime = attachments[filename]
        assert mime == 'image/png' and image.startswith(b'\x89PNG\r\n\x1a\n')
        width, height, _, _ = png.Reader(bytes=image).read()
        assert width == height and width >= 240
        assert message['inline_images'][content_id] == (filename, image, 'image/png')
        assert attachments['reservation.ics'][1] == 'text/calendar'
        assert 'BEGIN:VCALENDAR' in attachments['reservation.ics'][0].decode()


def test_inline_qr_has_real_cid_mime_part_and_downloadable_attachment(monkeypatch):
    app = Flask(__name__)
    app.config.update(MAIL_DEFAULT_SENDER='noreply@example.com', MAIL_SUPPRESS_SEND=True)
    Mail(app)
    captured = []
    monkeypatch.setattr(email_utils, 'send_async_email', lambda app, message: captured.append(message))

    class InlineThread:
        def __init__(self, target, args):
            self.target, self.args = target, args

        def start(self):
            self.target(*self.args)

    monkeypatch.setattr(email_utils.threading, 'Thread', InlineThread)
    with app.app_context():
        email_utils.send_email('Билет', 'guest@example.com', 'Билет во вложении',
                               body_html='<img src="cid:ticket-42">',
                               attachments=[('ticket-42.png', b'png-bytes', 'image/png'),
                                            ('reservation.ics', b'calendar', 'text/calendar')],
                               inline_images={'ticket-42': ('ticket-42.png', b'png-bytes', 'image/png')})
        mime = BytesParser(policy=policy.default).parsebytes(captured[0].as_bytes())
    parts = list(mime.walk())
    inline = next(part for part in parts if part.get('Content-ID') == '<ticket-42>')
    assert inline.get_content_disposition() == 'inline'
    assert inline.get_content_type() == 'image/png'
    assert inline.get_payload(decode=True) == b'png-bytes'
    downloads = [part for part in parts if part.get_content_disposition() == 'attachment']
    assert {part.get_filename() for part in downloads} == {'ticket-42.png', 'reservation.ics'}
