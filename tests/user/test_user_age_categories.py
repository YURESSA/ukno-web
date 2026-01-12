from http import HTTPStatus

import pytest


@pytest.mark.usefixtures("client")
class TestUserAgeCategories:

    def test_get_all_age_categories_user(self, client):
        resp = client.get("/api/references/age-categories")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert isinstance(data, list)

    def test_user_cannot_create_or_delete(self, client):
        payload = {"name": "Новая категория"}
        create_resp = client.post("/api/references/age-categories", json=payload)
        assert create_resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)

        del_resp = client.delete("/api/references/age-categories/1")
        assert del_resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
