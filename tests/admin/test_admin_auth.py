from http import HTTPStatus
from tests.conftest import TestAdminData

class TestAdminAuth:
    def test_admin_login(self, client):
        r = client.post('/api/admin/login', json={
            "email": TestAdminData.EMAIL,
            "password": TestAdminData.PASSWORD,
        })
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert "access_token" in data
        assert data["role"] == TestAdminData.ROLE


class TestAdminProfile:
    def test_admin_get_profile(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        r = client.get('/api/admin/profile', headers=headers)
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert data["email"] == TestAdminData.EMAIL
        assert data["role"] == TestAdminData.ROLE

    def test_admin_change_password(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        r = client.put('/api/admin/profile', headers=headers, json={
            "old_password": TestAdminData.PASSWORD,
            "new_password": "newadminpass"
        })
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert "успешно" in data.get("message", "").lower()
