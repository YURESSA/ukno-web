import pytest
from http import HTTPStatus


@pytest.mark.usefixtures("client", "created_news_id")
class TestUserNews:
    def test_get_all_news(self, client, created_news_id):
        """Тест получения списка всех новостей"""
        resp = client.get("/api/user/news")
        assert resp.status_code == HTTPStatus.OK
        data = resp.get_json()
        assert "news" in data
        assert isinstance(data["news"], list)
        news_ids = [n["news_id"] for n in data["news"]]
        assert created_news_id in news_ids

    def test_get_news_by_id_success(self, client, created_news_id):
        """Тест успешного получения новости по ID"""
        resp = client.get(f"/api/user/news/{created_news_id}")
        assert resp.status_code == HTTPStatus.OK
        news = resp.get_json()
        assert news["news_id"] == created_news_id
        assert news["title"] == "Тестовая новость для набора тестов"
        assert news["content"] == "Начальное содержание"
        assert news["short_description"] == "Краткое описание тестовой новости"
        assert news["photo_author"] == "Тестовый автор"

    def test_get_news_by_id_not_found(self, client):
        """Тест запроса несуществующей новости"""
        resp = client.get("/api/user/news/999999")
        assert resp.status_code == HTTPStatus.NOT_FOUND
        data = resp.get_json()
        assert data["message"] == "Новость не найдена"
