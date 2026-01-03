import json
from http import HTTPStatus

import pytest


@pytest.fixture()
def created_news_id(client, admin_access_token):
    data = {
        "data": json.dumps({
            "title": "Тестовая новость для набора тестов",
            "content": "Начальное содержание",
            "short_description": "Краткое описание тестовой новости",
            "photo_author": "Тестовый автор"
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

    assert "news_id" in post_json
    news_id = post_json.get("news_id")
    assert news_id is not None

    get_resp = client.get(f"/api/admin/news/{news_id}", headers=headers)
    assert get_resp.status_code == HTTPStatus.OK
    news_data = get_resp.get_json()
    assert news_data["title"] == "Тестовая новость для набора тестов"
    assert news_data["content"] == "Начальное содержание"
    assert news_data["short_description"] == "Краткое описание тестовой новости"
    assert news_data["photo_author"] == "Тестовый автор"

    yield news_id

    delete_resp = client.delete(
        f"/api/admin/news/{news_id}",
        headers=headers
    )
    if delete_resp.status_code not in (HTTPStatus.OK, HTTPStatus.NOT_FOUND):
        raise AssertionError("Не удалось удалить новость в фикстуре")


class TestAdminNews:

    def test_create_news(self, client, admin_access_token):
        pass  # пока оставляем пустым

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
