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
    assert "Бронирование № 42 подтверждено" in captured["body_html"]
    assert "2 участника" in captured["body_html"]
    assert "Юрий &lt;b&gt;Гошуренко&lt;/b&gt;" in captured["body_html"]
    assert "<script>" not in captured["body_html"]
    assert captured["attachments"] == [("reservation.ics", b"calendar", "text/calendar")]
