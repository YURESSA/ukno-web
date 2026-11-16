from datetime import datetime, timedelta

import pytest

from backend.core import db
from backend.core.models.auth_models import RoleEnum
from backend.core.models.event_models import Payment, Reservation
from backend.core.services.reservation_service import reservation_cancel
from tests import test_security_regressions as security


app = security.app
NOW = datetime(2026, 11, 28, 12, 0)


class Clock:
    @staticmethod
    def now(tz=None):
        return NOW.replace(tzinfo=tz)


@pytest.mark.parametrize('seconds, expected', [(-1, 409), (0, 409), (1, 200)])
def test_user_cannot_cancel_from_session_start(app, monkeypatch, seconds, expected):
    refunds, emails = [], []
    monkeypatch.setattr(reservation_cancel, 'datetime', Clock)
    monkeypatch.setattr(reservation_cancel, 'refund_yookassa_payment', lambda *args: refunds.append(args))
    monkeypatch.setattr(reservation_cancel, 'send_reservation_refund_email', lambda *args: emails.append(args))
    with app.app_context():
        admin = security.add_user('cancel-admin@example.com', RoleEnum.ADMIN)
        owner = security.add_user('cancel-owner@example.com')
        session = security.add_session(admin, capacity=10, cost=100)
        session.start_datetime = NOW + timedelta(seconds=seconds)
        reservation = Reservation(session=session, user=owner, full_name='Guest', phone_number='+70000000000',
                                  email=owner.email, participants_count=1, is_paid=True, is_cancelled=False)
        db.session.add(reservation)
        db.session.flush()
        db.session.add(Payment(payment_id='cancel-paid', reservation=reservation, session=session,
                               participants_count=1, email=owner.email, amount=100, status='succeeded'))
        db.session.commit()
        response = app.test_client().delete(
            '/api/user/v2/reservations', json={'reservation_id': reservation.reservation_id},
            headers=security.auth_header(owner),
        )
        assert response.status_code == expected, response.get_json()
        db.session.refresh(reservation)
        assert reservation.is_cancelled == (expected == 200)
        assert len(refunds) == len(emails) == (1 if expected == 200 else 0)
        if expected == 409:
            assert response.json['message'] == 'Нельзя отменить бронь после начала сеанса'
