import io
import json

import pytest
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import FileStorage

from backend.core import create_app, db
from backend.core.models.auth_models import User
from backend.core.models.event_models import Event, EventSession
from backend.core.services.event_services.event_crud import create_event
from backend.core.services.user_services.user_service import create_user


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


def get_excursion_payload():
    data = {
        "title": "Новая экскурсия",
        "description": "Описание экскурсии",
        "duration": 60,
        "category": "Воркшоп",
        "format_type": "Индивидуальная",
        "age_category": "Для школьников (7-17 лет)",
        "place": "Образовательный центр «Знание»",
        "conducted_by": "Репетитор Алексей Кузнецов",
        "is_active": True,
        "working_hours": "Пн-Пт с 16:00 до 20:00, Сб с 10:00 до 14:00",
        "contact_email": "math_tutor@ekbmail.ru",
        "iframe_url": "<iframe src='https://yandex.ru/map-widget/v1/?um=constructor%3Atutoringcenter' "
                      "width='600' height='450'></iframe>",
        "telegram": "@ekb_math_tutor",
        "vk": "https://vk.com/ekbmathtutor",
        "distance_to_center": 1300,
        "time_to_nearest_stop": 9,
        "sessions": [
            {
                "start_datetime": "2025-07-08T17:00:00",
                "max_participants": 1,
                "cost": 1200
            }
        ],
        "tags": ["репетиторство", "математика", "школьники", "образование", "подготовка к экзаменам"],
        "additional_info": {
            "max_participants": 1,
            "materials_provided": True,
            "location_description": "Центр расположен недалеко от станции метро «Чкаловская»."
        }
    }

    payload = {
        'data': json.dumps(data),
        'photos': (io.BytesIO(b"fake image data"), "photo1.jpg"),
    }

    return payload


def recreate_test_user(email, password, full_name, phone, role_name):
    user = User.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    create_user(
        email=email,
        password=password,
        full_name=full_name,
        phone=phone,
        role_name=role_name
    )


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        recreate_test_user(
            email=TestAdminData.EMAIL,
            password=TestAdminData.PASSWORD,
            full_name=TestAdminData.FULL_NAME,
            phone=TestAdminData.PHONE,
            role_name=TestAdminData.ROLE
        )
        recreate_test_user(
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


class AuthClient:
    def __init__(self, client, token):
        self._client = client
        self._token = token

    def _add_auth_header(self, kwargs):
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token}"
        kwargs["headers"] = headers
        return kwargs

    def get(self, *args, **kwargs):
        kwargs = self._add_auth_header(kwargs)
        return self._client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs = self._add_auth_header(kwargs)
        return self._client.post(*args, **kwargs)

    def patch(self, *args, **kwargs):
        kwargs = self._add_auth_header(kwargs)
        return self._client.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs = self._add_auth_header(kwargs)
        return self._client.delete(*args, **kwargs)


@pytest.fixture
def admin_client(client, admin_access_token):
    return AuthClient(client, admin_access_token)


@pytest.fixture
def resident_client(client, resident_access_token):
    return AuthClient(client, resident_access_token)


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
def existing_event_id(app):
    with app.app_context():
        user_email = TestAdminData.EMAIL

        data = {
            "title": "Индивидуальные занятия по математике для школьников",
            "description": "Помогаем школьникам Екатеринбурга улучшить знания по математике и "
                           "подготовиться к экзаменам с опытным репетитором.",
            "duration": 60,
            "category": "Воркшоп",
            "format_type": "Индивидуальная",
            "age_category": "Для школьников (7-17 лет)",
            "place": "Образовательный центр «Знание»",
            "conducted_by": "Репетитор Алексей Кузнецов",
            "is_active": True,
            "working_hours": "Пн-Пт с 16:00 до 20:00, Сб с 10:00 до 14:00",
            "contact_email": "math_tutor@ekbmail.ru",
            "iframe_url": "<iframe src='https://yandex.ru/map-widget/v1/?um=constructor%3Atutoringcenter' "
                          "width='600' height='450'></iframe>",
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

        excursion, response, error_status = create_event(data, user_email, files)

        if error_status:
            raise RuntimeError(f"Ошибка при создании тестовой экскурсии: {response['message']}")

        db.session.commit()

        excursion_id = excursion.event_id
        yield excursion_id

        excursion_to_delete = db.session.get(Event, excursion_id)

        if excursion_to_delete:
            db.session.delete(excursion_to_delete)
            db.session.commit()


def create_event_session(excursion_id, start_datetime, max_participants, cost):
    session = EventSession(
        event_id=excursion_id,
        start_datetime=start_datetime,
        max_participants=max_participants,
        cost=cost
    )
    db.session.add(session)
    db.session.commit()
    return session
