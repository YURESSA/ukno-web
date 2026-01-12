from http import HTTPStatus


class TestUserPartners:

    def test_get_all_partners_user(self, client, created_partner):
        resp = client.get("/api/references/partners")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        ids = [p["id"] for p in data]
        assert created_partner["id"] in ids

    def test_get_partner_by_id_user(self, client, created_partner):
        partner_id = created_partner["id"]
        resp = client.get(f"/api/references/partners/{partner_id}")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert data["id"] == partner_id
        assert data["name"] == created_partner["name"]

    def test_get_partner_by_id_not_found_user(self, client):
        resp = client.get("/api/references/partners/999999")
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "не найден" in resp.get_json()["message"]
