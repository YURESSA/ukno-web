from datetime import datetime
from http import HTTPStatus

import pytest

from backend.core import db
from tests.conftest import get_excursion_payload, create_event_session
from tests.excursion_tests import _assert_excursions_list_response, _assert_create_excursion_bad_json, \
    _assert_patch_update_excursion_success, _assert_patch_excursion_not_found, _assert_get_excursion_by_id_success, \
    _assert_get_not_found, _assert_delete_success, _assert_delete_not_found, _test_get_sessions_for_excursion, \
    _test_create_session_success, _test_patch_session, _test_delete_session, _test_upload_photo_success, \
    _test_get_photos, _test_delete_photo


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

    def test_get_all_excursions_resident(self, resident_client, excursion_id):
        r = resident_client.get("/api/resident/excursions")
        _assert_excursions_list_response(r, expected_excursion_id=excursion_id)

    def test_create_excursion_bad_json_resident(self, resident_client):
        _assert_create_excursion_bad_json(resident_client, "/api/resident/excursions")

    def test_patch_update_excursion_success_resident(self, resident_client, excursion_id):
        _assert_patch_update_excursion_success(resident_client, f"/api/resident/excursions/{excursion_id}")

    def test_patch_update_excursion_not_found_resident(self, resident_client):
        _assert_patch_excursion_not_found(resident_client, "/api/resident/excursions/999999")

    def test_get_excursion_by_id_success_resident(self, resident_client, excursion_id):
        _assert_get_excursion_by_id_success(
            resident_client,
            f"/api/resident/excursions/{excursion_id}",
            excursion_id
        )

    def test_get_excursion_by_id_not_found_resident(self, resident_client):
        _assert_get_not_found(resident_client, "/api/resident/excursions/999999")

    def test_delete_excursion_success_resident(self, resident_client, excursion_id):
        _assert_delete_success(resident_client, f"/api/resident/excursions/{excursion_id}")

    def test_delete_excursion_not_found_resident(self, resident_client):
        _assert_delete_not_found(resident_client, "/api/resident/excursions/999999")


@pytest.mark.usefixtures("resident_client")
class TestExcursionSessions:

    @pytest.fixture
    def excursion_with_one_session(self, app, excursion_id):
        with app.app_context():
            session = create_event_session(
                excursion_id=excursion_id,
                start_datetime=datetime.fromisoformat("2025-07-25T12:00:00"),
                max_participants=5,
                cost=1500
            )
            yield session
            db.session.delete(session)
            db.session.commit()

    def test_get_sessions_for_excursion_resident(self, resident_client, excursion_id):
        _test_get_sessions_for_excursion(resident_client, f"/api/resident/excursions/{excursion_id}/sessions")

    def test_create_session_success_resident(self, resident_client, excursion_id):
        _test_create_session_success(resident_client, f"/api/resident/excursions/{excursion_id}/sessions")

    def test_patch_session_resident(self, resident_client, excursion_with_one_session, excursion_id):
        _test_patch_session(resident_client, "/api/resident", excursion_id, excursion_with_one_session.session_id)

    def test_delete_session_resident(self, resident_client, excursion_with_one_session, excursion_id):
        _test_delete_session(resident_client, "/api/resident", excursion_id, excursion_with_one_session.session_id)


@pytest.mark.usefixtures("resident_client")
class TestExcursionPhotos:

    def test_upload_photo_success_resident(self, resident_client, excursion_id):
        _test_upload_photo_success(resident_client, "/api/resident", excursion_id)

    def test_get_photos_resident(self, resident_client, excursion_id):
        _test_get_photos(resident_client, "/api/resident", excursion_id)

    def test_delete_photo_resident(self, resident_client, excursion_id):
        _test_delete_photo(resident_client, "/api/resident", excursion_id)
