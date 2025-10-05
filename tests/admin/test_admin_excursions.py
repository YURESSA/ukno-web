from datetime import datetime
from http import HTTPStatus

import pytest

from backend.core import db
from tests.conftest import get_excursion_payload, create_event_session
from tests.excursion_tests import _assert_excursions_list_response, _assert_create_excursion_bad_json, \
    _assert_patch_update_excursion_success, _assert_patch_excursion_not_found, _assert_get_excursion_by_id_success, \
    _assert_get_not_found, _assert_delete_success, _assert_delete_not_found, _test_get_sessions_for_excursion, \
    _test_create_session_success, _test_patch_session, _test_delete_session, _test_get_session_participants, \
    _test_upload_photo_success, _test_get_photos, _test_delete_photo


@pytest.fixture
def new_excursion_id(admin_client):
    payload = get_excursion_payload()

    r = admin_client.post(
        "/api/admin/excursions",
        data=payload,
        content_type='multipart/form-data'
    )
    assert r.status_code == HTTPStatus.OK, r.get_data(as_text=True)
    excursion_id: object = r.get_json()["excursion_id"]

    yield excursion_id

    admin_client.delete(f"/api/admin/excursions/{excursion_id}")


@pytest.mark.usefixtures("admin_client")
class TestExcursions:

    def test_get_all_excursions_admin(self, admin_client):
        r = admin_client.get("/api/admin/excursions")
        _assert_excursions_list_response(r)

    def test_create_excursion_bad_json_admin(self, admin_client):
        _assert_create_excursion_bad_json(admin_client, "/api/admin/excursions")

    def test_patch_update_excursion_success_admin(self, admin_client, new_excursion_id):
        _assert_patch_update_excursion_success(admin_client, f"/api/admin/excursions/{new_excursion_id}")

    def test_patch_update_excursion_not_found_admin(self, admin_client):
        _assert_patch_excursion_not_found(admin_client, "/api/admin/excursions/999999")

    def test_get_excursion_by_id_success_admin(self, admin_client, new_excursion_id):
        _assert_get_excursion_by_id_success(
            admin_client,
            f"/api/admin/excursions/{new_excursion_id}",
            new_excursion_id
        )

    def test_get_excursion_by_id_not_found_admin(self, admin_client):
        _assert_get_not_found(admin_client, "/api/admin/excursions/999999")

    def test_delete_excursion_success_admin(self, admin_client, new_excursion_id):
        _assert_delete_success(admin_client, f"/api/admin/excursions/{new_excursion_id}")

    def test_delete_excursion_not_found_admin(self, admin_client):
        _assert_delete_not_found(admin_client, "/api/admin/excursions/999999")


@pytest.mark.usefixtures("admin_client")
class TestExcursionSessions:

    @pytest.fixture
    def excursion_with_one_session(self, app, new_excursion_id):
        with app.app_context():
            session = create_event_session(
                excursion_id=new_excursion_id,
                start_datetime=datetime.fromisoformat("2025-07-25T12:00:00"),
                max_participants=5,
                cost=1500
            )
            yield session
            db.session.delete(session)
            db.session.commit()

    def test_get_sessions_for_excursion_admin(self, admin_client, new_excursion_id):
        _test_get_sessions_for_excursion(admin_client, f"/api/admin/excursions/{new_excursion_id}/sessions")

    def test_create_session_success_admin(self, admin_client, new_excursion_id):
        _test_create_session_success(admin_client, f"/api/admin/excursions/{new_excursion_id}/sessions")

    def test_patch_session_admin(self, admin_client, excursion_with_one_session, new_excursion_id):
        _test_patch_session(admin_client, "/api/admin", new_excursion_id, excursion_with_one_session.session_id)

    def test_delete_session_admin(self, admin_client, excursion_with_one_session, new_excursion_id):
        _test_delete_session(admin_client, "/api/admin", new_excursion_id, excursion_with_one_session.session_id)

    def test_get_session_participants_admin(self, admin_client, excursion_with_one_session, new_excursion_id):
        _test_get_session_participants(admin_client, "/api/admin", new_excursion_id,
                                       excursion_with_one_session.session_id)


@pytest.mark.usefixtures("admin_client")
class TestExcursionPhotos:

    def test_upload_photo_success_admin(self, admin_client, new_excursion_id):
        _test_upload_photo_success(admin_client, "/api/admin", new_excursion_id)

    def test_get_photos_admin(self, admin_client, new_excursion_id):
        _test_get_photos(admin_client, "/api/admin", new_excursion_id)

    def test_delete_photo_admin(self, admin_client, new_excursion_id):
        _test_delete_photo(admin_client, "/api/admin", new_excursion_id)
