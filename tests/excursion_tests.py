import io
import json
from http import HTTPStatus

import pytest


def _assert_excursions_list_response(response, expected_excursion_id=None):
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert "excursions" in data
    assert isinstance(data["excursions"], list)
    if expected_excursion_id is not None:
        assert any(exc["excursion_id"] == expected_excursion_id for exc in data["excursions"])


def _assert_create_excursion_bad_json(client, url):
    payload = {'data': "невалидный JSON"}
    r = client.post(url, data=payload, content_type='multipart/form-data')
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert "Неверный JSON" in r.get_json().get("message", "")


def _assert_patch_update_excursion_success(client, url, new_title="Обновленное название"):
    update_data = {"title": new_title}
    r = client.patch(url, json=update_data)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert data.get("message") == "Экскурсия обновлена"
    assert data["excursion"]["title"] == new_title


def _assert_patch_excursion_not_found(client, url):
    r = client.patch(url, json={"title": "x"})
    assert r.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST)


def _assert_get_excursion_by_id_success(client, url, expected_id):
    r = client.get(url)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "excursion" in data
    assert data["excursion"]["excursion_id"] == expected_id


def _assert_get_not_found(client, url):
    r = client.get(url)
    assert r.status_code == HTTPStatus.NOT_FOUND


def _assert_delete_success(client, url):
    r = client.delete(url)
    assert r.status_code in (
        HTTPStatus.OK,
        HTTPStatus.CREATED,
        HTTPStatus.ACCEPTED,
        HTTPStatus.NO_CONTENT
    )


def _assert_delete_not_found(client, url):
    r = client.delete(url)
    assert r.status_code == HTTPStatus.NOT_FOUND


def _test_get_sessions_for_excursion(client, url):
    r = client.get(url)
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert isinstance(data, list)


def _test_create_session_success(client, url):
    session_data = {
        "start_datetime": "2025-07-28T15:00:00",
        "max_participants": 10,
        "cost": 2000
    }
    r = client.post(
        url,
        data=json.dumps(session_data),
        content_type="application/json"
    )
    assert r.status_code in (HTTPStatus.CREATED, HTTPStatus.OK)
    data = r.get_json()
    assert "session_id" in data


def _test_patch_session(client, base_url, excursion_id, session_id):
    r = client.patch(
        f"{base_url}/excursions/{excursion_id}/sessions/{session_id}",
        json={"cost": 2500}
    )
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert float(data["cost"]) == 2500.0


def _test_delete_session(client, base_url, excursion_id, session_id):
    r = client.delete(f"{base_url}/excursions/{excursion_id}/sessions/{session_id}")
    assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED)


def _test_get_session_participants(client, base_url, excursion_id, session_id):
    r = client.get(f"{base_url}/excursions/{excursion_id}/sessions/{session_id}")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    assert "participants" in data
    assert isinstance(data["participants"], list)


def _test_upload_photo_success(client, base_url, excursion_id):
    data = {
        "photo": (io.BytesIO(b"fake image data"), "photo.jpg")
    }
    r = client.post(
        f"{base_url}/excursions/{excursion_id}/photos",
        content_type="multipart/form-data",
        data=data
    )
    assert r.status_code == HTTPStatus.OK
    resp_data = r.get_json()
    assert resp_data["message"] == "Фото добавлено"
    assert "photos" in resp_data
    assert isinstance(resp_data["photos"], list)


def _test_get_photos(client, base_url, excursion_id):
    r = client.get(f"{base_url}/excursions/{excursion_id}/photos")
    assert r.status_code == HTTPStatus.OK
    data = r.get_json()
    print("DEBUG photos response:", data)
    assert "photos" in data
    assert isinstance(data["photos"], list)


def _test_delete_photo(client, base_url, excursion_id):
    r_photos = client.get(f"{base_url}/excursions/{excursion_id}/photos")
    photos_data = r_photos.get_json()
    photos = photos_data.get("photos", [])
    if not photos:
        pytest.skip("No photos to delete")

    photo_id = photos[0]["photo_id"]
    r = client.delete(f"{base_url}/excursions/{excursion_id}/photos/{photo_id}")
    assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED)
