import pytest
from flask_jwt_extended import create_access_token

from backend.core import create_app, db
from backend.core.models.auth_models import User
from backend.core.services.user_services.auth_service import create_user


class TestUserData:
    EMAIL = "a@b.com"
    PASSWORD = "123"
    FULL_NAME = "Test"
    PHONE = "000"
    ROLE = "user"


class TestAdminData:
    EMAIL = "admin@test.com"
    PASSWORD = "admin123"
    FULL_NAME = "Admin"
    PHONE = "000"
    ROLE = "admin"


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        admin_user = User.query.filter_by(email=TestAdminData.EMAIL).first()
        if admin_user:
            db.session.delete(admin_user)
            db.session.commit()

        create_user(
            email=TestAdminData.EMAIL,
            password=TestAdminData.PASSWORD,
            full_name=TestAdminData.FULL_NAME,
            phone=TestAdminData.PHONE,
            role_name=TestAdminData.ROLE
        )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


import pytest


@pytest.fixture
def admin_client(client, admin_access_token):
    class AdminClient:
        def __init__(self, client, token):
            self._client = client
            self._token = token

        def get(self, *args, **kwargs):
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            return self._client.get(*args, headers=headers, **kwargs)

        def post(self, *args, **kwargs):
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            return self._client.post(*args, headers=headers, **kwargs)

        def patch(self, *args, **kwargs):
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            return self._client.patch(*args, headers=headers, **kwargs)

        def delete(self, *args, **kwargs):
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            return self._client.delete(*args, headers=headers, **kwargs)

    return AdminClient(client, admin_access_token)


@pytest.fixture
def access_token(app):
    with app.app_context():
        return create_access_token(identity="a@b.com", additional_claims={"role": "user"})


@pytest.fixture
def admin_access_token(app):
    with app.app_context():
        return create_access_token(identity="admin@test.com", additional_claims={"role": "admin"})
