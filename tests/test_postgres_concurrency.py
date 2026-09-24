import os
import threading
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.core import create_app, db
from backend.core.config import Config
from backend.core.models.auth_models import RoleEnum, User
from backend.core.models.event_models import AgeCategory, Category, Event, EventSession, FormatType, Reservation
from backend.core.models.merch_models import (
    MerchCartItem,
    MerchCategory,
    MerchOrder,
    MerchProduct,
    MerchProductColor,
    MerchProductVariant,
    MerchSize,
)
from backend.core.services import merch_service
from backend.core.services.reservation_service import reservation_crud


TEST_DATABASE_URL = os.getenv("SECURITY_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="set SECURITY_TEST_DATABASE_URL to an isolated PostgreSQL database",
)


@pytest.fixture(scope="module")
def postgres_app():
    original_uri = Config.SQLALCHEMY_DATABASE_URI
    original_storage = Config.STORAGE_BACKEND
    Config.SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL
    Config.STORAGE_BACKEND = "local"
    application = create_app(testing=True)
    with application.app_context():
        db.drop_all()
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()
    Config.SQLALCHEMY_DATABASE_URI = original_uri
    Config.STORAGE_BACKEND = original_storage


def _user(email):
    user = User(full_name=email, email=email, phone="+70000000000", role=RoleEnum.USER)
    user.set_password("StrongPassword123!")
    db.session.add(user)
    db.session.flush()
    return user


def _run_together(app, calls):
    barrier = threading.Barrier(len(calls))
    results = [None] * len(calls)

    def worker(index, call):
        with app.app_context():
            barrier.wait(timeout=10)
            results[index] = call()
            db.session.remove()

    threads = [threading.Thread(target=worker, args=(index, call)) for index, call in enumerate(calls)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)
        assert not thread.is_alive(), "concurrent transaction did not finish"
    return results


def test_last_event_place_cannot_be_oversold(postgres_app, monkeypatch):
    monkeypatch.setattr(reservation_crud, "send_reservation_confirmation_email", lambda *args: None)
    with postgres_app.app_context():
        first = _user("race-first@example.com")
        second = _user("race-second@example.com")
        category = Category(category_name="Race category")
        format_type = FormatType(format_type_name="Race format")
        age = AgeCategory(age_category_name="Race age")
        db.session.add_all([category, format_type, age])
        db.session.flush()
        event = Event(
            title="Last place",
            description="Concurrency test",
            duration=60,
            category_id=category.category_id,
            format_type_id=format_type.format_type_id,
            age_category_id=age.age_category_id,
            created_by=first.user_id,
            is_active=True,
            place="Test",
        )
        db.session.add(event)
        db.session.flush()
        event_session = EventSession(
            event_id=event.event_id,
            start_datetime=datetime.now() + timedelta(days=1),
            max_participants=1,
            cost=0,
        )
        db.session.add(event_session)
        db.session.commit()
        session_id = event_session.session_id
        first_email, second_email = first.email, second.email

    def book(email):
        return reservation_crud.create_reservation_with_payment(
            email, session_id, email, "+70000000000", email, 1
        )

    results = _run_together(postgres_app, [lambda: book(first_email), lambda: book(second_email)])
    assert sorted(status for _, status in results) == [201, 409]
    with postgres_app.app_context():
        reservations = Reservation.query.filter_by(session_id=session_id, is_cancelled=False).all()
        assert sum(item.participants_count for item in reservations) == 1


def test_last_merch_item_cannot_be_sold_twice(postgres_app):
    with postgres_app.app_context():
        first = _user("stock-first@example.com")
        second = _user("stock-second@example.com")
        category = MerchCategory(name="Race merch", slug="race-merch")
        size = MerchSize(name="Race size")
        product = MerchProduct(category=category, name="Last item", price=Decimal("100.00"))
        color = MerchProductColor(product=product, name="Black")
        variant = MerchProductVariant(product=product, size=size, color=color, stock=1)
        db.session.add_all([category, size, product, color, variant])
        db.session.flush()
        db.session.add_all(
            [
                MerchCartItem(user_id=first.user_id, variant_id=variant.variant_id, quantity=1),
                MerchCartItem(user_id=second.user_id, variant_id=variant.variant_id, quantity=1),
            ]
        )
        db.session.commit()
        variant_id = variant.variant_id
        first_email, second_email = first.email, second.email

    payload = {
        "last_name": "Race",
        "first_name": "Buyer",
        "contact_channel": "race@example.com",
        "delivery_method": "pickup",
        "pay_by_card": False,
    }
    results = _run_together(
        postgres_app,
        [
            lambda: merch_service.create_order(first_email, payload),
            lambda: merch_service.create_order(second_email, payload),
        ],
    )
    assert sorted(status for _, status in results) == [201, 400]
    with postgres_app.app_context():
        assert db.session.get(MerchProductVariant, variant_id).stock == 0
        assert MerchOrder.query.count() == 1
