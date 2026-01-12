import json
from http import HTTPStatus


class TestUserProjects:

    def test_get_all_projects_user(self, client, created_project):
        resp = client.get("/api/references/projects")

        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert isinstance(data, list)
        assert any(p["id"] == created_project["id"] for p in data)

    def test_get_project_by_id_user(self, client, created_project):
        resp = client.get(
            f"/api/references/projects/{created_project['id']}"
        )

        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert data["id"] == created_project["id"]

    def test_create_project_forbidden_for_user(self, client):
        payload = {
            "title": "User project",
            "link": "https://user.com",
        }

        resp = client.post(
            "/api/references/projects",
            data=json.dumps(payload),
        )

        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_project_forbidden_for_user(
            self, client, created_project
    ):
        payload = {
            "title": "Hack",
            "link": "https://hack.com",
        }

        resp = client.put(
            f"/api/references/projects/{created_project['id']}",
            data=json.dumps(payload)
        )

        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_project_forbidden_for_user(
            self, client, created_project
    ):
        resp = client.delete(
            f"/api/references/projects/{created_project['id']}",
        )

        assert resp.status_code == HTTPStatus.UNAUTHORIZED
