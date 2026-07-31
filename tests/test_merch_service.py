from http import HTTPStatus
from types import SimpleNamespace

import pytest

from backend.core.services import merch_service


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "last_name is required"),
        ({"last_name": "Иванов"}, "first_name is required"),
        (
            {"last_name": "Иванов", "first_name": "Иван"},
            "contact_channel is required",
        ),
    ],
)
def test_create_order_requires_customer_fields(monkeypatch, payload, message):
    monkeypatch.setattr(
        merch_service,
        "get_current_user",
        lambda _email: (SimpleNamespace(user_id=7, email="buyer@example.test"), None),
    )

    response, status = merch_service.create_order("buyer@example.test", payload)

    assert status == HTTPStatus.BAD_REQUEST
    assert response == {"message": message}


def test_create_order_accepts_only_pickup_delivery(monkeypatch):
    monkeypatch.setattr(
        merch_service,
        "get_current_user",
        lambda _email: (SimpleNamespace(user_id=7, email="buyer@example.test"), None),
    )
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "contact_channel": "@ivan",
        "delivery_method": "courier",
        "pay_by_card": False,
    }

    response, status = merch_service.create_order("buyer@example.test", payload)

    assert status == HTTPStatus.BAD_REQUEST
    assert response == {"message": "Only pickup delivery is supported"}


def test_create_order_requires_payment_choice(monkeypatch):
    monkeypatch.setattr(
        merch_service,
        "get_current_user",
        lambda _email: (SimpleNamespace(user_id=7, email="buyer@example.test"), None),
    )
    payload = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "contact_channel": "@ivan",
    }

    response, status = merch_service.create_order("buyer@example.test", payload)

    assert status == HTTPStatus.BAD_REQUEST
    assert response == {"message": "pay_by_card is required"}


@pytest.mark.parametrize("quantity", [0, -1, "0"])
def test_cart_rejects_non_positive_quantity(monkeypatch, quantity):
    user = SimpleNamespace(user_id=7)
    variant = SimpleNamespace(
        stock=5,
        is_active=True,
        product=SimpleNamespace(is_deleted=False, is_active=True),
    )
    monkeypatch.setattr(merch_service, "get_current_user", lambda _email: (user, None))
    monkeypatch.setattr(
        merch_service.db.session,
        "get",
        lambda model, _identifier: variant if model is merch_service.MerchProductVariant else None,
    )

    response, status = merch_service.upsert_cart_item("buyer@example.test", 12, quantity)

    assert status == HTTPStatus.BAD_REQUEST
    assert response == {"message": "quantity must be greater than zero"}


def test_cart_reports_available_stock(monkeypatch):
    user = SimpleNamespace(user_id=7)
    variant = SimpleNamespace(
        stock=2,
        is_active=True,
        product=SimpleNamespace(is_deleted=False, is_active=True),
    )
    monkeypatch.setattr(merch_service, "get_current_user", lambda _email: (user, None))
    monkeypatch.setattr(
        merch_service.db.session,
        "get",
        lambda model, _identifier: variant if model is merch_service.MerchProductVariant else None,
    )

    response, status = merch_service.upsert_cart_item("buyer@example.test", 12, 3)

    assert status == HTTPStatus.BAD_REQUEST
    assert response == {"message": "Not enough stock", "available": 2}
