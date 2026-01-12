import json
from http import HTTPStatus


class TestAdminAgeCategories:

    def test_get_all_age_categories_admin(self, client, created_age_category, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.get("/api/references/age-categories", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        category_ids = [c["age_category_id"] for c in data]
        assert created_age_category["age_category_id"] in category_ids

    def test_create_age_category_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Для подростков (13-17 лет)"}

        resp = client.post(
            "/api/references/age-categories",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp.status_code == HTTPStatus.CREATED
        data = resp.get_json()
        assert data["age_category_id"] > 0
        assert data["age_category_name"] == payload["name"]

        # Cleanup
        client.delete(f"/api/references/age-categories/{data['age_category_id']}", headers=headers)

    def test_create_age_category_duplicate(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Для малышей (0-6 лет)"}

        # Создаем первый раз
        resp1 = client.post(
            "/api/references/age-categories",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp1.status_code == HTTPStatus.CREATED
        data1 = resp1.get_json()
        category_id = data1["age_category_id"]

        # Создаем второй раз — должно быть 400
        resp2 = client.post(
            "/api/references/age-categories",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp2.status_code == HTTPStatus.BAD_REQUEST
        resp_json = resp2.get_json()
        assert "уже существует" in resp_json["message"]

        # Cleanup
        client.delete(f"/api/references/age-categories/{category_id}", headers=headers)

    def test_delete_age_category_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Для студентов (18-22)"}

        # Создаем категорию
        resp = client.post(
            "/api/references/age-categories",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        category_id = resp.get_json()["age_category_id"]

        # Удаляем
        del_resp = client.delete(f"/api/references/age-categories/{category_id}", headers=headers)
        assert del_resp.status_code == HTTPStatus.OK
        del_json = del_resp.get_json()
        assert "удалена" in del_json["message"]

    def test_delete_age_category_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.delete("/api/references/age-categories/999999", headers=headers)
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найдена" in resp.get_json()["message"]
