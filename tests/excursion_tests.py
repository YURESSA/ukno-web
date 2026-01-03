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
    assert "excursion" in data, "В ответе отсутствует ключ 'excursion'"
    excursion = data["excursion"]

    expected_data = {
        "excursion_id": expected_id,
        "title": "Новая экскурсия",
        "description": "Описание экскурсии",
        "short_description": "Краткое описание экскурсии",
        "duration": 60,
        "category": {"category_name": "Воркшоп"},
        "format_type": {"format_type_name": "Индивидуальная"},
        "age_category": {"age_category_name": "Для школьников (7-17 лет)"},
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
            {"start_datetime": "2025-07-08T17:00:00", "max_participants": 1, "cost": 1200}
        ],
        "tags": ["репетиторство", "математика", "школьники", "образование", "подготовка к экзаменам"],
        "additional_info": {
            "max_participants": 1,
            "materials_provided": True,
            "location_description": "Центр расположен недалеко от станции метро «Чкаловская»."
        }
    }
    for field in [
        "title", "description", "short_description", "duration",
        "category", "format_type", "age_category", "place",
        "conducted_by", "is_active", "working_hours",
        "contact_email", "iframe_url", "telegram", "vk",
        "distance_to_center", "time_to_nearest_stop"
    ]:
        if field == "category":
            assert excursion[field]["category_name"] == expected_data[field][
                "category_name"], f"Поле {field} не совпадает"
        elif field == "format_type":
            assert excursion[field]["format_type_name"] == expected_data[field][
                "format_type_name"], f"Поле {field} не совпадает"
        elif field == "age_category":
            assert excursion[field]["age_category_name"] == expected_data[field][
                "age_category_name"], f"Поле {field} не совпадает"
        else:
            assert excursion[field] == expected_data[field], f"Поле {field} не совпадает"

    assert "sessions" in excursion, "В экскурсии нет ключа 'sessions'"
    assert len(excursion["sessions"]) == len(expected_data["sessions"]), "Количество сессий не совпадает"
    for got_sess, exp_sess in zip(excursion["sessions"], expected_data["sessions"]):
        for key in ["start_datetime", "max_participants", "cost"]:
            got_value = got_sess[key]
            if key == "cost":
                got_value = float(got_value)
            assert got_value == exp_sess[key], f"Сессия: поле {key} не совпадает"

    if "excursion_id" in expected_data:
        assert excursion["excursion_id"] == expected_data["excursion_id"], "ID экскурсии не совпадает"


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
