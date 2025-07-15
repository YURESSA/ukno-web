from http import HTTPStatus

import pytest

from tests.conftest import get_excursion_payload


@pytest.mark.usefixtures("resident_client")
class TestExcursions:
    @pytest.fixture
    def excursion_id(self, resident_client):
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
