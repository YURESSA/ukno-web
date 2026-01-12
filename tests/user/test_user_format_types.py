from http import HTTPStatus

import pytest


@pytest.mark.usefixtures("client")
class TestUserFormatTypes:

    def test_get_all_format_types_user(self, client):
        resp = client.get("/api/references/format-types")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert isinstance(data, list)

    def test_user_cannot_create_or_delete_format_type(self, client):
        payload = {"name": "Новый формат"}
        # POST
        create_resp = client.post("/api/references/format-types", json=payload)
        assert create_resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)

        # DELETE
        del_resp = client.delete("/api/references/format-types/1")
        assert del_resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
