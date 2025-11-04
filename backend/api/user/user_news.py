from http import HTTPStatus

from flask_restx import Resource

from . import user_ns
from backend.core.models.news_models import News


@user_ns.route('/news')
class NewsList(Resource):
    @user_ns.doc(description="Список всех новостей (без авторизации)")
    def get(self):
        """
        Возвращает список всех новостей, отсортированных по дате создания по убыванию.

        Returns:
            dict: Словарь с ключом 'news', содержащий список новостей.
        """
        news_list = News.query.order_by(News.created_at.desc()).all()
        return {
            "news": [n.to_dict() for n in news_list]
        }, HTTPStatus.OK


@user_ns.route('/news/<int:news_id>')
class NewsDetail(Resource):
    @user_ns.doc(description="Детальный просмотр новости по ID (без авторизации)")
    def get(self, news_id):
        """
        Возвращает полную информацию о конкретной новости.

        Args:
            news_id (int): ID новости.

        Returns:
            dict: Информация о новости.
            tuple: Словарь с сообщением об ошибке и HTTP статус, если новость не найдена.
        """
        news = News.query.get(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
        return news.to_dict(), HTTPStatus.OK
