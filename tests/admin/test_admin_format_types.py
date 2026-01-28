import json
from http import HTTPStatus


class TestAdminFormatTypes:

    def test_get_all_format_types_admin(self, client, created_format_type, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.get("/api/references/format-types", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        ids = [f["format_type_id"] for f in data]
        assert created_format_type["format_type_id"] in ids

    def test_create_format_type_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Новый формат для теста"}

        resp = client.post(
            "/api/references/format-types",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp.status_code == HTTPStatus.CREATED
        data = resp.get_json()
        assert data["format_type_id"] > 0
        assert data["format_type_name"] == payload["name"]

        # Cleanup
        client.delete(f"/api/references/format-types/{data['format_type_id']}", headers=headers)

    def test_create_format_type_duplicate(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Дублирующий формат"}

        # Первый раз
        resp1 = client.post(
            "/api/references/format-types",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp1.status_code == HTTPStatus.CREATED
        type_id = resp1.get_json()["format_type_id"]

        # Второй раз — должно быть 400
        resp2 = client.post(
            "/api/references/format-types",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        assert resp2.status_code == HTTPStatus.BAD_REQUEST
        assert "уже существует" in resp2.get_json()["message"]

        # Cleanup
        client.delete(f"/api/references/format-types/{type_id}", headers=headers)

    def test_delete_format_type_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {"name": "Формат для удаления"}

        # Создаем
        resp = client.post(
            "/api/references/format-types",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"}
        )
        type_id = resp.get_json()["format_type_id"]

        # Удаляем
        del_resp = client.delete(f"/api/references/format-types/{type_id}", headers=headers)
        assert del_resp.status_code == HTTPStatus.OK
        assert "удалён" in del_resp.get_json()["message"]

    def test_delete_format_type_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.delete("/api/references/format-types/999999", headers=headers)
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найден" in resp.get_json()["message"]
