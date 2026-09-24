from datetime import datetime
from types import SimpleNamespace

from backend.core.services.email_service import email_service


def test_reservation_confirmation_email_contains_useful_details_and_escapes_html(monkeypatch):
    captured = {}
    monkeypatch.setattr(email_service, "send_email", lambda **kwargs: captured.update(kwargs))
    monkeypatch.setattr(email_service, "create_ical_from_reservation", lambda reservation: b"calendar")

    event = SimpleNamespace(
        title='Лаборатория <script>alert("x")</script>',
        place='Бюро «5 этаж», ул. 8 Марта, 203',
        contact_email='bureau@ukno.ru',
    )
    session = SimpleNamespace(
        start_datetime=datetime(2026, 9, 29, 17, 0),
        event=event,
    )
    reservation = SimpleNamespace(
        reservation_id=42,
        email='guest@example.com',
        full_name='Юрий <b>Гошуренко</b>',
        participants_count=2,
        session=session,
    )

    email_service.send_reservation_confirmation_email(
        reservation,
        SimpleNamespace(email='fallback@example.com'),
    )

    assert captured["recipient"] == "guest@example.com"
    assert captured["subject"].startswith("Вы записаны:")
    assert "Номер бронирования: № 42" in captured["body"]
    assert "29.09.2026 17:00" in captured["body"]
    assert "reservation.ics" in captured["body"]
    assert "Бронирование" in captured["body_html"]
    assert "№ 42" in captured["body_html"]
    assert "2 участника" in captured["body_html"]
    assert "Юрий &lt;b&gt;Гошуренко&lt;/b&gt;" in captured["body_html"]
    assert "<script>" not in captured["body_html"]
    assert captured["attachments"] == [("reservation.ics", b"calendar", "text/calendar")]


def test_all_transactional_emails_use_branded_layout(monkeypatch):
    sent = []
    monkeypatch.setattr(email_service, "send_email", lambda **kwargs: sent.append(kwargs))
    monkeypatch.setattr(email_service, "generate_reset_token", lambda email: "safe-token")
    monkeypatch.setattr(email_service.Config, "FRONTEND_URL", "https://example.com/")

    event = SimpleNamespace(title='Событие <b>важное</b>', place='Бюро', contact_email='bureau@ukno.ru')
    session = SimpleNamespace(
        session_id=7,
        start_datetime=datetime(2026, 10, 2, 18, 30),
        event=event,
    )
    payment = SimpleNamespace(status="succeeded", amount="1500.00", currency="RUB")
    user = SimpleNamespace(full_name='Юрий <script>x</script>', email='user@example.com')
    reservation = SimpleNamespace(
        reservation_id=15,
        full_name=user.full_name,
        email=user.email,
        session=session,
        payment=payment,
        user=user,
    )
    resident = SimpleNamespace(full_name='Администратор', email='admin@example.com')

    email_service.send_reservation_cancellation_email(user, reservation)
    email_service.send_event_deletion_email(resident, event, b"csv")
    email_service.send_session_cancellation_email(reservation, event.title, session)
    email_service.send_session_deletion_email(resident.email, event.title, session.session_id, b"csv")
    email_service.send_reservation_refund_email(reservation)
    email_service.send_reset_email(user)

    assert len(sent) == 6
    for message in sent:
        assert '<meta name="viewport"' in message["body_html"]
        assert "max-width:640px" in message["body_html"]
        assert "background:#f3f0eb" in message["body_html"]
        assert "<script>" not in message["body_html"]

    assert "Возврат уже оформляется" in sent[0]["body_html"]
    assert sent[1]["attachments"] == [("отменённые_бронирования_событие_b_важное_b_.csv", b"csv")]
    assert "Сессия отменена" in sent[2]["body_html"]
    assert sent[3]["attachments"] == [("отменённые_бронирования_событие_b_важное_b__сессия_7.csv", b"csv")]
    assert "1500.00 RUB" in sent[4]["body_html"]
    assert "https://example.com/reset-password?token=safe-token" in sent[5]["body_html"]
