import json
from http import HTTPStatus

class TestAdminCompanyHistory:

    def test_get_all_history_admin(self, client, admin_access_token, created_history):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.get("/api/references/history", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert any(h["id"] == created_history["id"] for h in data)

    def test_create_history_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {
            "title": "Новое событие",
            "link": "https://example.com/new-event",
            "date": "2025-12-12",
            "description": "Описание нового события"
        }
        resp = client.post(
            "/api/references/history",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp.status_code == HTTPStatus.CREATED
        data = resp.get_json()
        assert data["title"] == payload["title"]

        # Cleanup
        client.delete(f"/api/references/history/{data['id']}", headers=headers)

    def test_update_history_success(self, client, admin_access_token, created_history):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {
            "title": "Обновлённое событие",
            "link": "https://example.com/updated-event",
            "date": "2025-12-13",
            "description": "Описание обновлённого события"
        }
        resp = client.put(
            f"/api/references/history/{created_history['id']}",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert data["title"] == payload["title"]

    def test_delete_history_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.delete("/api/references/history/999999", headers=headers)
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найдено" in resp.get_json()["message"]
