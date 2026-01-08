from http import HTTPStatus

import pytest


@pytest.mark.usefixtures("client")
class TestUserCategories:

    def test_get_all_categories_user(self, client, created_category):
        """Пользователь может получить список категорий"""
        resp = client.get("/api/references/categories")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert isinstance(data, list)
        category_ids = [c["category_id"] for c in data]
        assert created_category["category_id"] in category_ids

    def test_user_cannot_create_or_delete(self, client):
        """Пользователь не может создавать или удалять категории"""
        payload = {"name": "Новая категория"}
        create_resp = client.post("/api/references/categories", json=payload)
        assert create_resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)

        del_resp = client.delete("/api/references/categories/1")
        assert del_resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
