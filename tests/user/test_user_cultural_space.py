from http import HTTPStatus

import pytest


@pytest.mark.usefixtures("client")
class TestUserCulturalSpace:

    def test_get_all_cultural_space_user(self, client, created_cultural_space):
        resp = client.get("/api/references/cultural-space")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert isinstance(data, list)
        ids = [c["id"] for c in data]
        assert created_cultural_space["id"] in ids

    def test_user_cannot_create_or_delete(self, client):
        payload = {"text": "Новый элемент"}
        create_resp = client.post("/api/references/cultural-space", data=payload)
        assert create_resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)

        del_resp = client.delete("/api/references/cultural-space/1")
        assert del_resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
