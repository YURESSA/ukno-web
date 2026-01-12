from http import HTTPStatus


class TestUserTeam:

    def test_get_team_user(self, client):
        resp = client.get("/api/references/team")
        assert resp.status_code == HTTPStatus.OK
        assert isinstance(resp.get_json(), list)

    def test_get_team_member_user(self, client, created_team_member):
        member_id = created_team_member["id"]
        resp = client.get(f"/api/references/team/{member_id}")
        assert resp.status_code == HTTPStatus.OK
        assert resp.get_json()["id"] == member_id
