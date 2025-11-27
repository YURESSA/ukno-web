import json
from http import HTTPStatus

import pytest


@pytest.fixture()
def created_news_id(client, admin_access_token):
    data = {
        "data": json.dumps({
            "title": "Тестовая новость для набора тестов",
            "content": "Начальное содержание"
        }),
        "image": (open("tests/test_image.jpg", "rb"), "test_image.jpg")
    }
    headers = {"Authorization": f"Bearer {admin_access_token}"}

    post_resp = client.post(
        "/api/admin/news",
        data=data,
        headers=headers,
        content_type="multipart/form-data"
    )
    assert post_resp.status_code in (HTTPStatus.OK, HTTPStatus.CREATED)
    post_json = post_resp.get_json()
    news_id = post_json.get("news_id")
    assert news_id is not None

    yield news_id

    delete_resp = client.delete(
        f"/api/admin/news/{news_id}",
        headers=headers
    )
    if delete_resp.status_code not in (HTTPStatus.OK, HTTPStatus.NOT_FOUND):
        raise AssertionError("Не удалось удалить новость в фикстуре")


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
        assert put_json["news"]["title"] == "Обновлённый заголовок"
        assert put_json["news"]["content"] == "Обновлённое содержание"


def test_admin_delete_news_not_found(client, admin_access_token):
    headers = {"Authorization": f"Bearer {admin_access_token}"}
    delete_resp = client.delete("/api/admin/news/9999999", headers=headers)
    assert delete_resp.status_code == HTTPStatus.NOT_FOUND
    delete_json = delete_resp.get_json()
    assert "message" in delete_json
