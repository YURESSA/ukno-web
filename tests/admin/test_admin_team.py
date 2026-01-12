import io
from http import HTTPStatus


class TestAdminTeam:

    def test_get_team_admin(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        resp = client.get("/api/references/team", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        assert isinstance(resp.get_json(), list)

    def test_create_team_member_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        data = {
            "full_name": "Тестовый сотрудник",
            "description": "Описание сотрудника",
            "photo": (io.BytesIO(b"fake image"), "photo.jpg"),
        }

        resp = client.post(
            "/api/references/team",
            data=data,
            headers=headers,
            content_type="multipart/form-data",
        )

        assert resp.status_code == HTTPStatus.CREATED
        body = resp.get_json()
        assert body["full_name"] == "Тестовый сотрудник"
        assert "id" in body

        # cleanup
        client.delete(f"/api/references/team/{body['id']}", headers=headers)

    def test_update_team_member_success(self, client, created_team_member, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        member_id = created_team_member["id"]

        data = {
            "full_name": "Обновлённое имя",
            "description": "Новое описание",
        }

        resp = client.put(
            f"/api/references/team/{member_id}",
            data=data,
            headers=headers,
            content_type="multipart/form-data",
        )

        assert resp.status_code == HTTPStatus.OK
        body = resp.get_json()
        assert body["full_name"] == data["full_name"]

    def test_delete_team_member_success(self, client, created_team_member, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        member_id = created_team_member["id"]

        resp = client.delete(f"/api/references/team/{member_id}", headers=headers)
        assert resp.status_code == HTTPStatus.OK
        assert "удалён" in resp.get_json()["message"]

    def test_upload_team_photo_success(self, client, created_team_member, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        member_id = created_team_member["id"]

        data = {
            "photo": (io.BytesIO(b"new image"), "new.jpg"),
        }

        resp = client.post(
            f"/api/references/team/{member_id}/photo",
            data=data,
            headers=headers,
            content_type="multipart/form-data",
        )

        assert resp.status_code == HTTPStatus.OK
        assert "photo_path" in resp.get_json()

    def test_delete_team_photo_success(self, client, created_team_member_with_photo, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        member_id = created_team_member_with_photo["id"]

        resp = client.delete(
            f"/api/references/team/{member_id}/photo",
            headers=headers,
        )

        assert resp.status_code == HTTPStatus.OK
        assert "удалено" in resp.get_json()["message"]
