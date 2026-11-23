from datetime import datetime
from http import HTTPStatus

from backend.api.errors import ApiResource
from . import user_ns
from backend.core.models.news_models import News


@user_ns.route('/news')
class NewsList(ApiResource):
    @user_ns.doc(description="Список опубликованных новостей (без авторизации)")
    def get(self):
        """
        Возвращает список опубликованных новостей, отсортированных по дате публикации по убыванию.

        Returns:
            dict: Словарь с ключом 'news', содержащий список новостей.
        """
        news_list = (
            News.query.filter(News.created_at <= datetime.now())
            .order_by(News.created_at.desc())
            .all()
        )
        return {
            "news": [n.to_dict() for n in news_list]
        }, HTTPStatus.OK


@user_ns.route('/news/<int:news_id>')
class NewsDetail(ApiResource):
    @user_ns.doc(description="Детальный просмотр опубликованной новости по ID (без авторизации)")
    def get(self, news_id):
        """
        Возвращает полную информацию об опубликованной новости.

        Args:
            news_id (int): ID новости.

        Returns:
            dict: Информация о новости.
            tuple: Словарь с сообщением об ошибке и HTTP статус, если новость не найдена.
        """
        news = News.query.filter(
            News.news_id == news_id,
            News.created_at <= datetime.now(),
        ).first()
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
        return news.to_dict(), HTTPStatus.OK
