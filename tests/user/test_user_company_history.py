from http import HTTPStatus


class TestUserCompanyHistory:

    def test_get_all_history_user(self, client, created_history):
        resp = client.get("/api/references/history")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert any(h["id"] == created_history["id"] for h in data)

    def test_get_history_by_id_user(self, client, created_history):
        resp = client.get(f"/api/references/history/{created_history['id']}")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert data["id"] == created_history["id"]

    def test_get_history_by_id_not_found_user(self, client):
        resp = client.get("/api/references/history/999999")
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найдено" in resp.get_json()["message"]
