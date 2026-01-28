from http import HTTPStatus


class TestAdminCulturalSpace:

    def test_get_all_cultural_space_admin(self, client, created_cultural_space, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.get("/api/references/cultural-space", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        ids = [c["id"] for c in data]
        assert created_cultural_space["id"] in ids

    def test_create_cultural_space_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"text": "Элемент для теста", "order_index": 2}

        resp = client.post(
            "/api/references/cultural-space",
            data=payload,
            headers=headers
        )
        assert resp.status_code == HTTPStatus.CREATED
        data = resp.get_json()
        space_id = data["id"]
        assert data["text"] == payload["text"]

        # Cleanup
        client.delete(f"/api/references/cultural-space/{space_id}", headers=headers)

    def test_update_cultural_space_success(self, client, created_cultural_space, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"text": "Обновленный текст", "order_index": 5}
        space_id = created_cultural_space["id"]

        resp = client.put(
            f"/api/references/cultural-space/{space_id}",
            data=payload,
            headers=headers
        )
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert data["text"] == payload["text"]
        assert data["order_index"] == payload["order_index"]

    def test_delete_cultural_space_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.delete("/api/references/cultural-space/999999", headers=headers)
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найден" in resp.get_json()["message"]
