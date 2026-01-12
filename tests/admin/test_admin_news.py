import json
from http import HTTPStatus


class TestAdminNews:

    def test_create_news(self, client, admin_access_token):
        pass

    def test_update_news(self, client, admin_access_token, created_news_id):
        update_data = {
            "data": json.dumps({
                "title": "Обновлённый заголовок",
                "content": "Обновлённое содержание"
            }),
        }
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        put_resp = client.put(
            f"/api/admin/news/{created_news_id}",
            data=update_data,
            headers=headers,
            content_type="multipart/form-data"
        )
        assert put_resp.status_code == HTTPStatus.OK
        put_json = put_resp.get_json()
        assert put_json.get("message") == "Новость обновлена"
        news = put_json.get("news")

        print("Новость после обновления:", news)

        assert news is not None
        assert news["title"] == "Обновлённый заголовок"
        assert news["content"] == "Обновлённое содержание"


def test_admin_delete_news_not_found(client, admin_access_token):
    headers = {"Authorization": f"Bearer {admin_access_token}"}
    delete_resp = client.delete("/api/admin/news/9999999", headers=headers)
    assert delete_resp.status_code == HTTPStatus.NOT_FOUND
    delete_json = delete_resp.get_json()
    assert "message" in delete_json
