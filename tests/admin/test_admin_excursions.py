import io
import json
from datetime import datetime
from http import HTTPStatus

import pytest

from backend.core import db
from backend.core.models.excursion_models import ExcursionSession
from tests.conftest import get_excursion_payload


@pytest.mark.usefixtures("admin_client")
class TestExcursions:
    @pytest.fixture
    def new_excursion_id(self, admin_client):
        payload = get_excursion_payload()

        r = admin_client.post("/api/admin/excursions", data=payload, content_type='multipart/form-data')
        assert r.status_code == HTTPStatus.OK, r.get_data(as_text=True)
        excursion_id: object = r.get_json()["excursion_id"]

        yield excursion_id

        admin_client.delete(f"/api/admin/excursions/{excursion_id}")

    def test_get_all_excursions(self, admin_client):
        r = admin_client.get("/api/admin/excursions")
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert "excursions" in data
        assert isinstance(data["excursions"], list)

    def test_create_excursion_bad_json(self, admin_client):
        payload = {'data': "невалидный JSON"}
        r = admin_client.post(
            "/api/admin/excursions",
            data=payload,
            content_type='multipart/form-data'
        )
        assert r.status_code == HTTPStatus.BAD_REQUEST
        data = r.get_json()
        assert "Неверный JSON" in data.get("message", "")

    def test_patch_update_excursion_success(self, admin_client, existing_excursion_id):
        update_data = {"title": "Обновленное название"}
        r = admin_client.patch(
            f"/api/admin/excursions/{existing_excursion_id}",
            json=update_data
        )
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert data.get("message") == "Экскурсия обновлена"
        assert data["excursion"]["title"] == update_data["title"]

    def test_patch_update_excursion_not_found(self, admin_client):
        r = admin_client.patch("/api/admin/excursions/999999", json={"title": "x"})
        assert r.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST)

    def test_get_excursion_by_id_success(self, admin_client, existing_excursion_id):
        r = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}")
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert "excursion" in data
        assert data["excursion"]["excursion_id"] == existing_excursion_id

    def test_get_excursion_by_id_not_found(self, admin_client):
        r = admin_client.get("/api/admin/excursions/999999")
        assert r.status_code == HTTPStatus.NOT_FOUND

    def test_delete_excursion_success(self, admin_client, existing_excursion_id):
        r = admin_client.delete(f"/api/admin/excursions/{existing_excursion_id}")
        assert r.status_code in (
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
            HTTPStatus.NO_CONTENT
        )

    def test_delete_excursion_not_found(self, admin_client):
        r = admin_client.delete("/api/admin/excursions/999999")
        assert r.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures("admin_client")
class TestExcursionSessions:

    @pytest.fixture
    def excursion_with_one_session(self, existing_excursion_id):
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

    def test_get_sessions_for_excursion(self, admin_client, existing_excursion_id):
        r = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}/sessions")
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert isinstance(data, list)

    def test_create_session_success(self, admin_client, existing_excursion_id):
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
        assert r.status_code in (HTTPStatus.CREATED, HTTPStatus.OK)
        data = r.get_json()
        assert "session_id" in data

    def test_patch_session(self, admin_client, excursion_with_one_session, existing_excursion_id):
        session_id = excursion_with_one_session.session_id
        r = admin_client.patch(
            f"/api/admin/excursions/{existing_excursion_id}/sessions/{session_id}",
            json={"cost": 2500}
        )
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert float(data["cost"]) == 2500.0

    def test_delete_session(self, admin_client, excursion_with_one_session, existing_excursion_id):
        session_id = excursion_with_one_session.session_id
        r = admin_client.delete(
            f"/api/admin/excursions/{existing_excursion_id}/sessions/{session_id}"
        )
        assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED)

    def test_get_session_participants(self, admin_client, excursion_with_one_session, existing_excursion_id):
        session_id = excursion_with_one_session.session_id
        r = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}/sessions/{session_id}")
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        assert "participants" in data
        assert isinstance(data["participants"], list)


@pytest.mark.usefixtures("admin_client")
class TestExcursionPhotos:

    def test_upload_photo_success(self, admin_client, existing_excursion_id):
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

    def test_get_photos(self, admin_client, existing_excursion_id):
        r = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}/photos")
        assert r.status_code == HTTPStatus.OK
        data = r.get_json()
        print("DEBUG photos response:", data)
        assert "photos" in data
        assert isinstance(data["photos"], list)

    def test_delete_photo(self, admin_client, existing_excursion_id):
        r_photos = admin_client.get(f"/api/admin/excursions/{existing_excursion_id}/photos")
        photos_data = r_photos.get_json()
        photos = photos_data.get("photos", [])
        if not photos:
            pytest.skip("No photos to delete")

        photo_id = photos[0]["photo_id"]
        r = admin_client.delete(
            f"/api/admin/excursions/{existing_excursion_id}/photos/{photo_id}"
        )
        assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED)
