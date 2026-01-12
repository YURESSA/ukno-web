import io
from http import HTTPStatus


class TestAdminPartners:

    def test_get_all_partners_admin(self, client, created_partner, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.get("/api/references/partners", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        ids = [p["id"] for p in data]
        assert created_partner["id"] in ids

    def test_update_partner_success(self, client, created_partner, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        partner_id = created_partner["id"]

        data = {
            "name": "Обновлённый партнёр",
            "link": "https://update.com",
            "order_index": 2
        }

        resp = client.put(
            f"/api/references/partners/{partner_id}",
            data=data,  # передаём form-data
            headers=headers,
            content_type='multipart/form-data'
        )

        assert resp.status_code == HTTPStatus.OK
        updated = resp.get_json()
        assert updated["name"] == data["name"]
        assert updated["link"] == data["link"]
        assert updated["order_index"] == data["order_index"]

    def test_delete_partner_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.delete("/api/references/partners/999999", headers=headers)
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найден" in resp.get_json()["message"]


class TestAdminPartnerPhoto:

    def test_upload_photo_success(self, client, created_partner, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        partner_id = created_partner["id"]

        file_data = io.BytesIO(b"fake image content")
        file_data.name = "test.jpg"

        resp = client.post(
            f"/api/references/partners/{partner_id}/photo",
            data={"photo": (file_data, file_data.name)},
            headers=headers,
            content_type='multipart/form-data'
        )
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert "photo_path" in data

    def test_delete_photo_success(self, client, created_partner, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        partner_id = created_partner["id"]

        # Загружаем фото
        file_data = io.BytesIO(b"fake image content")
        file_data.name = "test.jpg"
        client.post(
            f"/api/references/partners/{partner_id}/photo",
            data={"photo": (file_data, file_data.name)},
            headers=headers,
            content_type='multipart/form-data'
        )

        # Удаляем фото
        del_resp = client.delete(f"/api/references/partners/{partner_id}/photo", headers=headers)
        assert del_resp.status_code == HTTPStatus.OK
        assert "удалено" in del_resp.get_json()["message"]

    def test_delete_photo_not_found(self, client, created_partner, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        partner_id = created_partner["id"]

        # Если фото не было загружено
        del_resp = client.delete(f"/api/references/partners/{partner_id}/photo", headers=headers)
        assert del_resp.status_code == HTTPStatus.BAD_REQUEST
        assert "Фото отсутствует" in del_resp.get_json()["message"]
