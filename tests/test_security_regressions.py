from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from flask_jwt_extended import create_access_token

from backend.api.admin.decorators import admin_required
from backend.api.webhook import routes as webhook_routes
from backend.core import create_app, db
from backend.core.config import Config
from backend.core.models.auth_models import RoleEnum, User
from backend.core.models.event_models import (
    AgeCategory,
    Category,
    Event,
    EventSession,
    FormatType,
    Payment,
    Reservation,
)
from backend.core.services.reservation_service import reservation_crud
from backend.core.services.user_services.user_service import update_user


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "SQLALCHEMY_DATABASE_URI", f"sqlite:///{tmp_path / 'security.db'}")
    monkeypatch.setattr(Config, "STORAGE_BACKEND", "local")
    application = create_app(testing=True)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


def add_user(email, role=RoleEnum.USER):
    user = User(full_name=email.split("@", 1)[0], email=email, phone="+70000000000", role=role)
    user.set_password("StrongPassword123!")
    db.session.add(user)
    db.session.flush()
    return user


def add_session(owner, capacity=1, cost=0):
    category = Category(category_name="Security category")
    format_type = FormatType(format_type_name="Security format")
    age = AgeCategory(age_category_name="Security age")
    db.session.add_all([category, format_type, age])
    db.session.flush()
    event = Event(
        title="Security event",
        description="Test",
        duration=60,
        category_id=category.category_id,
        format_type_id=format_type.format_type_id,
        age_category_id=age.age_category_id,
        created_by=owner.user_id,
        is_active=True,
        place="Test place",
    )
    db.session.add(event)
    db.session.flush()
    session = EventSession(
        event_id=event.event_id,
        start_datetime=datetime.now() + timedelta(days=1),
        max_participants=capacity,
        cost=cost,
    )
    db.session.add(session)
    db.session.commit()
    return session


def auth_header(user):
    token = create_access_token(
        identity=user.email,
        additional_claims={"role": user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


def test_calendar_exports_require_owner_jwt(app):
    with app.app_context():
        owner = add_user("owner@example.com")
        stranger = add_user("stranger@example.com")
        session = add_session(owner)
        reservation = Reservation(
            session_id=session.session_id,
            user_id=owner.user_id,
            full_name="Owner",
            phone_number="+70000000000",
            email=owner.email,
            participants_count=1,
            is_paid=True,
            is_cancelled=False,
        )
        db.session.add(reservation)
        db.session.commit()
        reservation_id = reservation.reservation_id
        owner_headers = auth_header(owner)
        stranger_headers = auth_header(stranger)

        client = app.test_client()
        for suffix in ("export_ical", "google_calendar_link"):
            url = f"/api/user/reservations/{reservation_id}/{suffix}"
            assert client.get(url).status_code == 401
            assert client.get(url, headers=stranger_headers).status_code == 404
            assert client.get(url, headers=owner_headers).status_code == 200


def test_capacity_holds_prevent_overbooking_and_duplicate_booking(app, monkeypatch):
    monkeypatch.setattr(reservation_crud, "send_reservation_confirmation_email", lambda *args: None)
    with app.app_context():
        first = add_user("first@example.com")
        second = add_user("second@example.com")
        session = add_session(first, capacity=1, cost=0)

        created, created_status = reservation_crud.create_reservation_with_payment(
            first.email, session.session_id, "First", "+70000000001", first.email, 1
        )
        rejected, rejected_status = reservation_crud.create_reservation_with_payment(
            second.email, session.session_id, "Second", "+70000000002", second.email, 1
        )
        duplicate, duplicate_status = reservation_crud.create_reservation_with_payment(
            first.email, session.session_id, "First", "+70000000001", first.email, 1
        )

        assert created_status == 201
        assert created["reservation_id"]
        assert rejected_status == 409
        assert "свободных мест" in rejected["message"]
        assert duplicate_status == 409
        assert "активное бронирование" in duplicate["message"]
        assert Reservation.query.filter_by(is_cancelled=False).count() == 1


def test_reservation_rejects_invalid_participant_count(app):
    with app.app_context():
        user = add_user("count@example.com")
        session = add_session(user, capacity=10)
        for invalid in (0, -1, True, 1.5, "2"):
            response, status = reservation_crud.create_reservation_with_payment(
                user.email, session.session_id, "Count", "+70000000003", user.email, invalid
            )
            assert status == 400
            assert "положительным целым" in response["message"]


def test_forged_webhook_cannot_mark_reservation_paid(app, monkeypatch):
    with app.app_context():
        user = add_user("payer@example.com")
        session = add_session(user, capacity=2, cost=500)
        reservation = Reservation(
            session_id=session.session_id,
            user_id=user.user_id,
            full_name="Payer",
            phone_number="+70000000004",
            email=user.email,
            participants_count=1,
            is_paid=False,
            is_cancelled=False,
        )
        db.session.add(reservation)
        db.session.flush()
        payment = Payment(
            payment_id="payment-1",
            session_id=session.session_id,
            reservation_id=reservation.reservation_id,
            participants_count=1,
            email=user.email,
            amount=500,
            currency="RUB",
            status="pending",
        )
        db.session.add(payment)
        db.session.commit()
        reservation_id = reservation.reservation_id

        monkeypatch.setattr(
            webhook_routes,
            "get_yookassa_payment",
            lambda payment_id: SimpleNamespace(
                id=payment_id,
                status="pending",
                metadata={"type": "reservation", "reservation_id": reservation_id},
            ),
        )
        payload = {
            "type": "notification",
            "event": "payment.succeeded",
            "object": {
                "id": "payment-1",
                "status": "succeeded",
                "metadata": {"type": "reservation", "reservation_id": reservation_id},
            },
        }
        response = app.test_client().post("/api/webhook/yookassa", json=payload)

        assert response.status_code == 400
        assert db.session.get(Reservation, reservation_id).is_paid is False


def test_verified_webhook_is_idempotent_and_uses_trusted_metadata(app, monkeypatch):
    sent = []
    with app.app_context():
        user = add_user("verified@example.com")
        session = add_session(user, capacity=2, cost=500)
        reservation = Reservation(
            session_id=session.session_id,
            user_id=user.user_id,
            full_name="Verified",
            phone_number="+70000000005",
            email=user.email,
            participants_count=1,
            is_paid=False,
            is_cancelled=False,
        )
        db.session.add(reservation)
        db.session.flush()
        payment = Payment(
            payment_id="payment-2",
            session_id=session.session_id,
            reservation_id=reservation.reservation_id,
            participants_count=1,
            email=user.email,
            amount=500,
            currency="RUB",
            status="pending",
        )
        db.session.add(payment)
        db.session.commit()
        reservation_id = reservation.reservation_id

        monkeypatch.setattr(
            webhook_routes,
            "get_yookassa_payment",
            lambda payment_id: SimpleNamespace(
                id=payment_id,
                status="succeeded",
                metadata={"type": "reservation", "reservation_id": reservation_id},
            ),
        )
        monkeypatch.setattr(webhook_routes, "send_reservation_confirmation_email", lambda *args: sent.append(args))
        payload = {
            "type": "notification",
            "event": "payment.succeeded",
            "object": {"id": "payment-2", "metadata": {"reservation_id": 999999}},
        }
        client = app.test_client()
        assert client.post("/api/webhook/yookassa", json=payload).status_code == 200
        assert client.post("/api/webhook/yookassa", json=payload).status_code == 200

        assert db.session.get(Reservation, reservation_id).is_paid is True
        assert db.session.get(Payment, "payment-2").status == "succeeded"
        assert len(sent) == 1


def test_login_does_not_reveal_whether_email_exists(app):
    with app.app_context():
        add_user("known@example.com")
        db.session.commit()
        client = app.test_client()
        known = client.post("/api/login", json={"email": "known@example.com", "password": "wrong"})
        unknown = client.post("/api/login", json={"email": "missing@example.com", "password": "wrong"})

        assert known.status_code == unknown.status_code == 401
        assert known.get_json() == unknown.get_json() == {"message": "Неверный email или пароль"}


def test_demoted_admin_cannot_use_old_admin_token(app):
    with app.app_context():
        user = add_user("demoted@example.com", RoleEnum.ADMIN)
        db.session.commit()
        old_admin_headers = auth_header(user)
        user.role = RoleEnum.USER
        db.session.commit()

        @app.get("/_security/admin-only")
        @admin_required
        def admin_only():
            return {"ok": True}

        response = app.test_client().get("/_security/admin-only", headers=old_admin_headers)
        assert response.status_code == 403


def test_admin_user_update_accepts_role_name_and_legacy_role(app):
    with app.app_context():
        user = add_user("role-change@example.com")
        db.session.commit()

        updated = update_user(user.email, {"role": "admin"})
        assert updated.role == RoleEnum.ADMIN

        updated = update_user(user.email, {"role_name": "resident"})
        assert updated.role == RoleEnum.RESIDENT
