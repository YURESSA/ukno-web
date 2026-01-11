import io
from http import HTTPStatus

import pytest


@pytest.mark.usefixtures("client")
class TestAdminCulturalSpacePhoto:

    def test_upload_photo_success(self, client, created_cultural_space, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        space_id = created_cultural_space["id"]

        file_data = io.BytesIO(b"fake image content")
        file_data.name = "test.jpg"

        resp = client.post(
            f"/api/references/cultural-space/{space_id}/photo",
            data={"photo": (file_data, file_data.name)},
            headers=headers,
            content_type='multipart/form-data'
        )

        assert resp.status_code == HTTPStatus.OK
        json_data = resp.get_json()
        assert json_data["message"] == "Фото загружено"
        assert "photo_path" in json_data

    def test_delete_photo_success(self, client, created_cultural_space, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        space_id = created_cultural_space["id"]

        # Загружаем сначала фото
        file_data = io.BytesIO(b"fake image content")
        file_data.name = "test.jpg"
        client.post(
            f"/api/references/cultural-space/{space_id}/photo",
            data={"photo": (file_data, file_data.name)},
            headers=headers,
            content_type='multipart/form-data'
        )

        del_resp = client.delete(f"/api/references/cultural-space/{space_id}/photo", headers=headers)
        assert del_resp.status_code == HTTPStatus.OK
        json_data = del_resp.get_json()
        assert json_data["message"] == "Фото удалено"

    def test_delete_photo_not_found(self, client, created_cultural_space, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        space_id = created_cultural_space["id"]

        resp = client.delete(f"/api/references/cultural-space/{space_id}/photo", headers=headers)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.get_json()["message"] == "Фото отсутствует"

    def test_upload_photo_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        file_data = io.BytesIO(b"fake image content")
        file_data.name = "test.jpg"
        resp = client.post(
            "/api/references/cultural-space/999999/photo",
            data={"photo": (file_data, file_data.name)},
            headers=headers,
            content_type='multipart/form-data'
        )
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найден" in resp.get_json()["message"]
