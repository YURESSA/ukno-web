import io
from http import HTTPStatus


class TestAdminRequisites:

    def test_get_all_requisites_admin(self, client, created_requisite, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        resp = client.get("/api/references/requisites", headers=headers)
        assert resp.status_code == HTTPStatus.OK

        data = resp.get_json()
        ids = [r["id"] for r in data]
        assert created_requisite["id"] in ids

    def test_create_requisite_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        data = {
            "title": "Реквизит для теста",
            "file": (io.BytesIO(b"test file content"), "test.pdf"),
        }

        resp = client.post(
            "/api/references/requisites",
            data=data,
            headers=headers,
            content_type="multipart/form-data"
        )

        assert resp.status_code == HTTPStatus.CREATED
        body = resp.get_json()
        assert body["title"] == "Реквизит для теста"
        assert body["file"] is not None

        # cleanup
        client.delete(f"/api/references/requisites/{body['id']}", headers=headers)

    def test_update_requisite_title_success(self, client, created_requisite, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        data = {
            "title": "Обновлённый реквизит"
        }

        resp = client.put(
            f"/api/references/requisites/{created_requisite['id']}",
            data=data,
            headers=headers,
            content_type="multipart/form-data"
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.get_json()["title"] == "Обновлённый реквизит"

    def test_replace_requisite_file_success(self, client, created_requisite, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        data = {
            "file": (io.BytesIO(b"new file content"), "new.pdf")
        }

        resp = client.post(
            f"/api/references/requisites/{created_requisite['id']}/file",
            data=data,
            headers=headers,
            content_type="multipart/form-data"
        )

        assert resp.status_code == HTTPStatus.OK
        assert "file_path" in resp.get_json()

    def test_delete_requisite_file_success(self, client, created_requisite, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        resp = client.delete(
            f"/api/references/requisites/{created_requisite['id']}/file",
            headers=headers
        )

        assert resp.status_code == HTTPStatus.OK
        assert "удалён" in resp.get_json()["message"]

    def test_delete_requisite_success(self, client, created_requisite, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        resp = client.delete(
            f"/api/references/requisites/{created_requisite['id']}",
            headers=headers
        )

        assert resp.status_code == HTTPStatus.OK
        assert "удалён" in resp.get_json()["message"]

    def test_delete_requisite_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        resp = client.delete("/api/references/requisites/999999", headers=headers)
        assert resp.status_code == HTTPStatus.NOT_FOUND
