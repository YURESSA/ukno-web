from http import HTTPStatus

from backend.core import db
from backend.core.messages import AuthMessages
from backend.core.models.auth_models import User
from tests.conftest import TestUserData, TestAdminData


class TestAdminUsers:
    def test_admin_get_users(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        r = client.get('/api/admin/users', headers=headers)
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert isinstance(data, list)
        assert any(u["email"] == TestAdminData.EMAIL for u in data)

    def test_admin_create_user(self, client, admin_access_token):
        with client.application.app_context():
            existing_user = User.query.filter_by(email=TestUserData.EMAIL).first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()

        headers = {"Authorization": f"Bearer {admin_access_token}"}
        new_user = {
            "email": TestUserData.EMAIL,
            "password": TestUserData.PASSWORD,
            "phone": TestUserData.PHONE,
            "role": TestUserData.ROLE,
            "full_name": TestUserData.FULL_NAME
        }
        r = client.post('/api/admin/users', headers=headers, json=new_user)
        assert r.status_code in (HTTPStatus.CREATED, HTTPStatus.OK)
        data = r.get_json()
        assert data.get("message") == AuthMessages.USER_CREATED

    def test_admin_get_user_detail(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        r = client.get(f'/api/admin/users/detail/{TestUserData.EMAIL}', headers=headers)
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert data["email"] == TestUserData.EMAIL
        assert data["full_name"] == TestUserData.FULL_NAME
        assert data["role"] == TestUserData.ROLE

    def test_admin_get_user_detail_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        r = client.get('/api/admin/users/detail/notfounduser@test.com', headers=headers)
        assert r.status_code == HTTPStatus.NOT_FOUND
        data = r.get_json()
        assert data["message"] == AuthMessages.USER_NOT_FOUND

    def test_admin_update_user_success(self, client, admin_access_token):
        update_data = {
            "full_name": "Updated Name",
            "phone": "999999"
        }
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        r = client.put(f'/api/admin/users/detail/{TestUserData.EMAIL}', headers=headers, json=update_data)
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert isinstance(data, list)
        user_data = data[0]
        assert user_data["full_name"] == update_data["full_name"]
        assert user_data["phone"] == update_data["phone"]

    def test_admin_update_user_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        r = client.put('/api/admin/users/detail/ghost@test.com', headers=headers, json={"full_name": "Ghost"})
        assert r.status_code == HTTPStatus.NOT_FOUND
        data = r.get_json()
        assert data["message"] == AuthMessages.USER_NOT_FOUND

    def test_admin_update_user_empty_json(self, client, admin_access_token):
        headers = {
            "Authorization": f"Bearer {admin_access_token}",
            "Content-Type": "application/json"
        }
        r = client.put(f'/api/admin/users/detail/{TestUserData.EMAIL}', headers=headers, data="{}")
        assert r.status_code == HTTPStatus.BAD_REQUEST

    def test_admin_delete_user_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        r = client.delete(f"/api/admin/users/detail/{TestUserData.EMAIL}", headers=headers)
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert data["message"] == AuthMessages.USER_DELETED
