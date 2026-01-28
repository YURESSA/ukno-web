import json
from http import HTTPStatus

import pytest


class TestAdminTrustReasons:

    @pytest.fixture
    def created_reason(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"title": "Тестовая причина", "description": "Описание"}
        resp = client.post(
            "/api/references/trust-reasons",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp.status_code == HTTPStatus.CREATED
        data = resp.get_json()
        yield data
        # Cleanup
        client.delete(f"/api/references/trust-reasons/{data['id']}", headers=headers)

    def test_get_all_trust_reasons_admin(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.get("/api/references/trust-reasons", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert isinstance(data, list)

    def test_create_trust_reason_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"title": "Новая причина", "description": "Описание"}

        resp = client.post(
            "/api/references/trust-reasons",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp.status_code == HTTPStatus.CREATED
        data = resp.get_json()
        assert data["title"] == payload["title"]

        # Cleanup
        client.delete(f"/api/references/trust-reasons/{data['id']}", headers=headers)

    def test_delete_trust_reason_success(self, client, admin_access_token, created_reason):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        reason_id = created_reason["id"]

        resp = client.delete(f"/api/references/trust-reasons/{reason_id}", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        assert "удалена" in resp.get_json()["message"]

    def test_delete_trust_reason_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.delete("/api/references/trust-reasons/999999", headers=headers)
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найдена" in resp.get_json()["message"]
