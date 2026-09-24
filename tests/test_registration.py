from http import HTTPStatus

from backend.core.models.auth_models import RoleEnum, User
from backend.core.services.user_services import auth_service


def test_user_phone_column_accepts_formatted_numbers():
    assert User.__table__.c.phone.type.length == 32


def test_registration_accepts_formatted_russian_phone(monkeypatch):
    captured = {}

    def fake_create_user(email, password, full_name, phone, role):
        captured["phone"] = phone
        return object()

    monkeypatch.setattr(auth_service, "create_user", fake_create_user)

    body, status = auth_service.register_user(
        RoleEnum.USER,
        {
            "email": "new-user@example.com",
            "password": "password",
            "full_name": "Новый пользователь",
            "phone": "+7 951 270-28-58",
        },
    )

    assert status == HTTPStatus.CREATED
    assert captured["phone"] == "+7 951 270-28-58"
    assert "message" in body


def test_registration_rejects_phone_longer_than_database_column(monkeypatch):
    create_user_called = False

    def fake_create_user(*args, **kwargs):
        nonlocal create_user_called
        create_user_called = True

    monkeypatch.setattr(auth_service, "create_user", fake_create_user)

    body, status = auth_service.register_user(
        RoleEnum.USER,
        {
            "email": "new-user@example.com",
            "password": "password",
            "full_name": "Новый пользователь",
            "phone": "+" + "1" * 32,
        },
    )

    assert status == HTTPStatus.BAD_REQUEST
    assert body == {"message": "Номер телефона не должен превышать 32 символа"}
    assert create_user_called is False


def test_registration_rejects_missing_required_fields(monkeypatch):
    create_user_called = False

    def fake_create_user(*args, **kwargs):
        nonlocal create_user_called
        create_user_called = True

    monkeypatch.setattr(auth_service, "create_user", fake_create_user)

    body, status = auth_service.register_user(RoleEnum.USER, {})

    assert status == HTTPStatus.BAD_REQUEST
    assert body == {"message": "Необходимо указать email, пароль и полное имя"}
    assert create_user_called is False
