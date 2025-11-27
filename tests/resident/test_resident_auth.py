from http import HTTPStatus

import pytest

from tests.conftest import TestResidentData


@pytest.mark.usefixtures("client")
class TestResidentAuth:

    def test_login_success(self, client):
        data = {"email": TestResidentData.EMAIL, "password": TestResidentData.PASSWORD}
        r = client.post("/api/resident/login", json=data)
        assert r.status_code == HTTPStatus.OK
        resp = r.get_json()
        assert "access_token" in resp

    def test_login_failure(self, client):
        data = {"email": "nope@example.com", "password": "wrong"}
        r = client.post("/api/resident/login", json=data)
        print(r.data)
        assert r.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.usefixtures("client", "resident_access_token")
class TestResidentProfile:

    @pytest.fixture
    def headers(self, resident_access_token):
        return {"Authorization": f"Bearer {resident_access_token}"}

    def test_get_profile(self, client, headers):
        r = client.get("/api/resident/profile", headers=headers)
        assert r.status_code == HTTPStatus.OK
        resp = r.get_json()
        assert resp["email"] == "resident@example.com"

    def test_update_password(self, client, headers):
        payload = {
            "old_password": TestResidentData.PASSWORD,
            "new_password": "newsecure456"
        }
        r = client.put("/api/resident/profile", headers=headers, json=payload)
        assert r.status_code == HTTPStatus.OK
