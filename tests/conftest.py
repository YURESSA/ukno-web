import io

import pytest
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import FileStorage

from backend.core import create_app, db
from backend.core.models.auth_models import User
from backend.core.models.excursion_models import Excursion
from backend.core.services.excursion_services.excursion_service import create_excursion
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


class TestResidentData:
    EMAIL = "resident@example.com"
    PASSWORD = "resident123"
    FULL_NAME = "Test Resident"
    PHONE = "+78888888888"
    ROLE = "resident"


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
        resident_user = User.query.filter_by(email=TestResidentData.EMAIL).first()
        if resident_user:
            db.session.delete(resident_user)
            db.session.commit()
        create_user(
            email=TestResidentData.EMAIL,
            password=TestResidentData.PASSWORD,
            full_name=TestResidentData.FULL_NAME,
            phone=TestResidentData.PHONE,
            role_name=TestResidentData.ROLE
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


@pytest.fixture
def resident_access_token(app):
    with app.app_context():
        return create_access_token(identity=TestResidentData.EMAIL, additional_claims={"role": "resident"})


@pytest.fixture
def existing_excursion_id(app):
    with app.app_context():
        user_email = TestAdminData.EMAIL

        data = {
            "title": "Индивидуальные занятия по математике для школьников",
            "description": "Помогаем школьникам Екатеринбурга улучшить знания по математике и подготовиться к экзаменам с опытным репетитором.",
            "duration": 60,
            "category": "Воркшоп",
            "format_type": "Индивидуальная",
            "age_category": "Для школьников (7-17 лет)",
            "place": "Образовательный центр «Знание»",
            "conducted_by": "Репетитор Алексей Кузнецов",
            "is_active": True,
            "working_hours": "Пн-Пт с 16:00 до 20:00, Сб с 10:00 до 14:00",
            "contact_email": "math_tutor@ekbmail.ru",
            "iframe_url": "<iframe src='https://yandex.ru/map-widget/v1/?um=constructor%3Atutoringcenter' width='600' height='450'></iframe>",
            "telegram": "@ekb_math_tutor",
            "vk": "https://vk.com/ekbmathtutor",
            "distance_to_center": 1300,
            "time_to_nearest_stop": 9,
            "sessions": [
                {
                    "start_datetime": "2029-07-25T17:00:00",
                    "max_participants": 1,
                    "cost": 0
                }
            ],
            "tags": ["репетиторство", "математика", "школьники", "образование", "подготовка к экзаменам"],
            "additional_info": {
                "max_participants": 1,
                "materials_provided": True,
                "location_description": "Центр расположен недалеко от станции метро «Чкаловская»."
            }
        }

        file_storage = FileStorage(
            stream=io.BytesIO(b"fake image data"),
            filename="photo1.jpg",
            content_type="image/jpeg"
        )
        files = [file_storage]

        excursion, response, error_status = create_excursion(data, user_email, files)

        if error_status:
            raise RuntimeError(f"Ошибка при создании тестовой экскурсии: {response['message']}")

        db.session.commit()

        excursion_id = excursion.excursion_id
        yield excursion_id

        excursion_to_delete = db.session.get(Excursion, excursion_id)

        if excursion_to_delete:
            db.session.delete(excursion_to_delete)
            db.session.commit()
