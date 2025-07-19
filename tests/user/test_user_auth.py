from http import HTTPStatus

from backend.core.messages import AuthMessages
from tests.conftest import TestUserData


def test_register_user(client):
    payload = {
        "email": TestUserData.EMAIL,
        "password": TestUserData.PASSWORD,
        "full_name": TestUserData.FULL_NAME,
        "phone": TestUserData.PHONE,
    }
    r = client.post("/api/user/register", json=payload)
    if r.status_code == HTTPStatus.CONFLICT:
        data = r.get_json()
        assert AuthMessages.USER_ALREADY_EXISTS in data.get("message", "")
    else:
        assert r.status_code == HTTPStatus.CREATED
        data = r.get_json()
        assert data["message"] == AuthMessages.USER_CREATED


def test_login_user(client):
    client.post("/api/user/register", json={
        "email": TestUserData.EMAIL,
        "password": TestUserData.PASSWORD,
        "full_name": TestUserData.FULL_NAME,
        "phone": TestUserData.PHONE,
    })

    r = client.post("/api/user/login", json={
        "email": TestUserData.EMAIL,
        "password": TestUserData.PASSWORD,
    })
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "access_token" in data

    r = client.post("/api/user/login", json={
        "email": "wrong_email@example.com",
        "password": TestUserData.PASSWORD,
    })
    assert r.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.BAD_REQUEST)

    r = client.post("/api/user/login", json={
        "email": TestUserData.EMAIL,
        "password": "wrong_password",
    })
    assert r.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.BAD_REQUEST)


def test_change_password(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "old_password": TestUserData.PASSWORD,
        "new_password": "new_secret"
    }
    r = client.put("/api/user/profile/password", json=payload, headers=headers)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "успешно" in data.get("message", "")


def test_get_profile(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}

    r = client.get("/api/user/profile", headers=headers)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert data["email"] == TestUserData.EMAIL
    assert data["full_name"] == TestUserData.FULL_NAME
    assert data["phone"] == TestUserData.PHONE
    assert data["role"] == TestUserData.ROLE

    payload = {
        "email": TestUserData.EMAIL,
        "full_name": "New Name",
        "phone": "1234567890"
    }
    r = client.put("/api/user/profile", headers=headers, json=payload)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert AuthMessages.PROFILE_UPDATED in data.get("message", "")

    r = client.get("/api/user/profile", headers=headers)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert data["full_name"] == "New Name"
    assert data["phone"] == "1234567890"
    assert data["email"] == TestUserData.EMAIL
    assert data["role"] == TestUserData.ROLE
