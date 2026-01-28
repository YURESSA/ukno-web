import json
from http import HTTPStatus


class TestAdminCategories:

    def test_get_all_categories_admin(self, client, created_category, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.get("/api/references/categories", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        category_ids = [c["category_id"] for c in data]
        assert created_category["category_id"] in category_ids

    def test_create_category_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Новая категория тест"}

        resp = client.post(
            "/api/references/categories",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp.status_code == HTTPStatus.CREATED
        data = resp.get_json()
        assert data["category_id"] > 0
        assert data["category_name"] == payload["name"]

        client.delete(f"/api/references/categories/{data['category_id']}", headers=headers)

    def test_create_category_duplicate(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Дубликат категории"}

        resp1 = client.post(
            "/api/references/categories",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp1.status_code == HTTPStatus.CREATED
        category_id = resp1.get_json()["category_id"]

        resp2 = client.post(
            "/api/references/categories",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp2.status_code == HTTPStatus.BAD_REQUEST
        assert "уже существует" in resp2.get_json()["message"]

        client.delete(f"/api/references/categories/{category_id}", headers=headers)

    def test_delete_category_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Категория для удаления"}

        resp = client.post(
            "/api/references/categories",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        category_id = resp.get_json()["category_id"]

        del_resp = client.delete(f"/api/references/categories/{category_id}", headers=headers)
        assert del_resp.status_code == HTTPStatus.OK
        assert "удалена" in del_resp.get_json()["message"]

    def test_delete_category_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.delete("/api/references/categories/999999", headers=headers)
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найдена" in resp.get_json()["message"]
