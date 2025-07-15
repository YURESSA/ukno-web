import io
import json
from datetime import datetime
from http import HTTPStatus

import pytest

from backend.core import db
from backend.core.models.excursion_models import ExcursionSession
from tests.conftest import get_excursion_payload


@pytest.fixture
def excursion_id(resident_client):
    payload = get_excursion_payload()
    r = resident_client.post(
        "/api/resident/excursions",
        data=payload,
        content_type='multipart/form-data'
    )
    assert r.status_code == HTTPStatus.OK, r.get_data(as_text=True)
    excursion_id: object = r.get_json()["excursion_id"]

    yield excursion_id

    resident_client.delete(f"/api/resident/excursions/{excursion_id}")


@pytest.mark.usefixtures("resident_client")
class TestExcursions:

    def test_get_all_excursions(self, resident_client, excursion_id):
        r = resident_client.get("/api/resident/excursions")
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert "excursions" in data
        assert isinstance(data["excursions"], list)
        assert any(exc["excursion_id"] == excursion_id for exc in data["excursions"])

    def test_create_excursion_bad_json(self, resident_client):
        payload = {'data': "невалидный JSON"}
        r = resident_client.post(
            "/api/resident/excursions",
            data=payload,
            content_type='multipart/form-data'
        )
        assert r.status_code == HTTPStatus.BAD_REQUEST
        assert "Неверный JSON" in r.get_json().get("message", "")

    def test_patch_update_excursion_success(self, resident_client, excursion_id):
        update_data = {"title": "Обновленное название"}
        r = resident_client.patch(
            f"/api/resident/excursions/{excursion_id}",
            json=update_data
        )
        assert r.status_code == HTTPStatus.OK
        body = r.get_json()
        assert body.get("message") == "Экскурсия обновлена"
        assert body["excursion"]["title"] == update_data["title"]

    def test_patch_update_excursion_not_found(self, resident_client):
        r = resident_client.patch("/api/resident/excursions/999999", json={"title": "x"})
        assert r.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST)

    def test_get_excursion_by_id_success(self, resident_client, excursion_id):
        r = resident_client.get(f"/api/resident/excursions/{excursion_id}")
        assert r.status_code == HTTPStatus.OK
        body = r.get_json()
        assert "excursion" in body
        assert body["excursion"]["excursion_id"] == excursion_id

    def test_get_excursion_by_id_not_found(self, resident_client):
        r = resident_client.get("/api/resident/excursions/999999")
        assert r.status_code == HTTPStatus.NOT_FOUND

    def test_delete_excursion_success(self, resident_client, excursion_id):
        r = resident_client.delete(f"/api/resident/excursions/{excursion_id}")
        assert r.status_code in (
            HTTPStatus.OK,
            HTTPStatus.ACCEPTED,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.CREATED
        )


@pytest.mark.usefixtures("resident_client")
class TestExcursionSessions:

    @pytest.fixture
    def excursion_with_one_session(self, app, excursion_id):
        with app.app_context():
            session_data = {
                "start_datetime": datetime.fromisoformat("2025-07-25T12:00:00"),
                "max_participants": 5,
                "cost": 1500
            }
            session = ExcursionSession(
                excursion_id=excursion_id,
                **session_data
            )
            db.session.add(session)
            db.session.commit()
            yield session
            db.session.delete(session)
            db.session.commit()

    def test_get_sessions_for_excursion(self, resident_client, excursion_id):
        r = resident_client.get(f"/api/resident/excursions/{excursion_id}/sessions")
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert isinstance(data, list)

    def test_create_session_success(self, resident_client, excursion_id):
        session_data = {
            "start_datetime": "2025-07-28T15:00:00",
            "max_participants": 10,
            "cost": 2000
        }
        r = resident_client.post(
            f"/api/resident/excursions/{excursion_id}/sessions",
            data=json.dumps(session_data),
            content_type="application/json"
        )
        assert r.status_code in (HTTPStatus.CREATED, HTTPStatus.OK)
        data = r.get_json()
        assert "session_id" in data

    def test_patch_session(self, resident_client, excursion_with_one_session, excursion_id):
        session_id = excursion_with_one_session.session_id
        r = resident_client.patch(
            f"/api/resident/excursions/{excursion_id}/sessions/{session_id}",
            json={"cost": 2500}
        )
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert float(data["cost"]) == 2500.0

    def test_delete_session(self, resident_client, excursion_with_one_session, excursion_id):
        session_id = excursion_with_one_session.session_id
        r = resident_client.delete(
            f"/api/resident/excursions/{excursion_id}/sessions/{session_id}"
        )
        assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED)


@pytest.mark.usefixtures("resident_client")
class TestExcursionPhotos:

    def test_upload_photo_success(self, resident_client, excursion_id):
        data = {
            "photo": (io.BytesIO(b"fake image data"), "photo.jpg")
        }
        r = resident_client.post(
            f"/api/resident/excursions/{excursion_id}/photos",
            content_type="multipart/form-data",
            data=data
        )
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert data["message"] == "Фото добавлено"
        assert "photos" in data
        assert isinstance(data["photos"], list)

    def test_get_photos(self, resident_client, excursion_id):
        r = resident_client.get(f"/api/resident/excursions/{excursion_id}/photos")
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        print("DEBUG photos response:", data)
        assert "photos" in data
        assert isinstance(data["photos"], list)

    def test_delete_photo(self, resident_client, excursion_id):
        r_photos = resident_client.get(f"/api/resident/excursions/{excursion_id}/photos")
        photos_data = r_photos.get_json()
        photos = photos_data.get("photos", [])
        if not photos:
            pytest.skip("No photos to delete")

        photo_id = photos[0]["photo_id"]
        r = resident_client.delete(
            f"/api/resident/excursions/{excursion_id}/photos/{photo_id}"
        )
        assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED)
