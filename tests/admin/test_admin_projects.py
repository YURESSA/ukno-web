import json
from http import HTTPStatus


class TestAdminProjects:

    def test_get_all_projects_admin(self, client, created_project):
        resp = client.get("/api/references/projects")

        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert isinstance(data, list)
        assert any(p["id"] == created_project["id"] for p in data)

    def test_create_project_success(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {
            "title": "Новый проект",
            "link": "https://new-project.com",
            "order_index": 2,
        }

        resp = client.post(
            "/api/references/projects",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"},
        )

        assert resp.status_code == HTTPStatus.CREATED
        data = resp.get_json()
        assert data["title"] == payload["title"]
        assert data["link"] == payload["link"]
        assert data["order_index"] == payload["order_index"]

    def test_get_project_by_id(self, client, created_project):
        resp = client.get(f"/api/references/projects/{created_project['id']}")

        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert data["id"] == created_project["id"]

    def test_get_project_not_found(self, client):
        resp = client.get("/api/references/projects/999999")

        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_update_project_success(self, client, created_project, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {
            "title": "Обновлённый проект",
            "link": "https://updated.com",
            "order_index": 3,
        }

        resp = client.put(
            f"/api/references/projects/{created_project['id']}",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"},
        )

        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert data["title"] == payload["title"]
        assert data["link"] == payload["link"]
        assert data["order_index"] == payload["order_index"]

    def test_update_project_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        payload = {
            "title": "Fail",
            "link": "https://fail.com",
        }

        resp = client.put(
            "/api/references/projects/999999",
            data=json.dumps(payload),
            headers={**headers, "Content-Type": "application/json"},
        )

        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_delete_project_success(self, client, created_project, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        resp = client.delete(
            f"/api/references/projects/{created_project['id']}",
            headers=headers,
        )

        assert resp.status_code == HTTPStatus.OK

    def test_delete_project_not_found(self, client, admin_access_token):
        headers = {"Authorization": f"Bearer {admin_access_token}"}

        resp = client.delete(
            "/api/references/projects/999999",
            headers=headers,
        )

        assert resp.status_code == HTTPStatus.NOT_FOUND
