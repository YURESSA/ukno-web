import io
import json
from datetime import datetime
from http import HTTPStatus

import pytest

from backend.core import db
from backend.core.models.excursion_models import ExcursionSession


def test_get_all_excursions(admin_client):
    r = admin_client.get("/api/admin/excursions")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "excursions" in data
    assert isinstance(data["excursions"], list)


def test_create_excursion_success(admin_client):
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
        "iframe_url": "<iframe src='https://yandex.ru/map-widget/v1/?um=constructor%3Atutoringcenter' width='600' height='450'></iframe>",
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
    r = admin_client.post(
        "/api/admin/excursions",
        data=payload,
        content_type='multipart/form-data'
    )
    assert r.status_code == HTTPStatus.OK

    resp = r.get_json()
    assert resp.get("message") == "Событие создано"
    assert "excursion_id" in resp

    excursion_id = resp["excursion_id"]
    del_resp = admin_client.delete(f"/api/admin/excursions/{excursion_id}")
    assert del_resp.status_code in (
        HTTPStatus.OK,
        HTTPStatus.ACCEPTED,
        HTTPStatus.NO_CONTENT,
        HTTPStatus.CREATED
    )


def test_create_excursion_bad_json(admin_client):
    payload = {
        'data': "невалидный JSON"
    }
    r = admin_client.post(
        "/api/admin/excursions",
        data=payload,
        content_type='multipart/form-data'
    )
    assert r.status_code == HTTPStatus.BAD_REQUEST
    data = r.get_json()
    assert "Неверный JSON" in data.get("message", "")


def test_patch_update_excursion_success(admin_client, existing_excursion_id):
    update_data = {
        "title": "Обновленное название"
    }
    r = admin_client.patch(
        f"/api/admin/excursions/{existing_excursion_id}",
        json=update_data
    )
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert data.get("message") == "Экскурсия обновлена"
    assert data["excursion"]["title"] == update_data["title"]


def test_patch_update_excursion_not_found(admin_client):
    r = admin_client.patch("/api/admin/excursions/999999", json={"title": "x"})
    assert r.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST)


def test_get_excursion_by_id_success(admin_client, existing_excursion_id):
    r = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "excursion" in data
    assert data["excursion"]["excursion_id"] == existing_excursion_id


def test_get_excursion_by_id_not_found(admin_client):
    r = admin_client.get("/api/admin/excursions/999999")
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_delete_excursion_success(admin_client, existing_excursion_id):
    r = admin_client.delete(f"/api/admin/excursions/{existing_excursion_id}")
    assert r.status_code in (
        HTTPStatus.OK,
        HTTPStatus.CREATED,
        HTTPStatus.ACCEPTED,
        HTTPStatus.NO_CONTENT  # ← это важно
    )


def test_delete_excursion_not_found(admin_client):
    r = admin_client.delete("/api/admin/excursions/999999")
    assert r.status_code == HTTPStatus.NOT_FOUND


@pytest.fixture
def excursion_with_one_session(existing_excursion_id):
    session_data = {
        "start_datetime": datetime.fromisoformat("2025-07-25T12:00:00"),
        "max_participants": 5,
        "cost": 1500
    }
    session = ExcursionSession(
        excursion_id=existing_excursion_id,
        **session_data
    )
    db.session.add(session)
    db.session.commit()
    yield session
    db.session.delete(session)
    db.session.commit()


def test_get_sessions_for_excursion(admin_client, existing_excursion_id):
    r = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}/sessions")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert isinstance(data, list)


def test_create_session_success(admin_client, existing_excursion_id):
    session_data = {
        "start_datetime": "2025-07-28T15:00:00",
        "max_participants": 10,
        "cost": 2000
    }
    r = admin_client.post(
        f"/api/admin/excursions/{existing_excursion_id}/sessions",
        data=json.dumps(session_data),
        content_type="application/json"
    )
    assert r.status_code == HTTPStatus.CREATED or r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "session_id" in data


def test_patch_session(admin_client, excursion_with_one_session, existing_excursion_id):
    session_id = excursion_with_one_session.session_id
    r = admin_client.patch(
        f"/api/admin/excursions/{existing_excursion_id}/sessions/{session_id}",
        json={"cost": 2500}
    )
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert float(data["cost"]) == 2500.0


def test_delete_session(admin_client, excursion_with_one_session, existing_excursion_id):
    session_id = excursion_with_one_session.session_id
    r = admin_client.delete(
        f"/api/admin/excursions/{existing_excursion_id}/sessions/{session_id}"
    )
    assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED)


def test_get_session_participants(admin_client, excursion_with_one_session, existing_excursion_id):
    session_id = excursion_with_one_session.session_id
    r = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}/sessions/{session_id}")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "participants" in data
    assert isinstance(data["participants"], list)


def test_upload_photo_success(admin_client, existing_excursion_id):
    data = {
        "photo": (io.BytesIO(b"fake image data"), "photo.jpg")
    }
    r = admin_client.post(
        f"/api/admin/excursions/{existing_excursion_id}/photos",
        content_type="multipart/form-data",
        data=data
    )
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert data["message"] == "Фото добавлено"
    assert "photos" in data
    assert isinstance(data["photos"], list)


def test_get_photos(admin_client, existing_excursion_id):
    r = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}/photos")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "photos" in data
    assert isinstance(data["photos"], list)


def test_delete_photo(admin_client, existing_excursion_id):
    r = admin_client.post(
        f"/api/admin/excursions/{existing_excursion_id}/photos",
        content_type="multipart/form-data",
        data={"photo": (io.BytesIO(b"test"), "test.jpg")}
    )
    assert r.status_code == HTTPStatus.OK
    photo_id = r.get_json()["photos"][0]["photo_id"]

    r = admin_client.delete(
        f"/api/admin/excursions/{existing_excursion_id}/photos/{photo_id}"
    )
    assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT)
