from http import HTTPStatus
from typing import Dict, Any, Optional, List, Tuple

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource

from backend.core.schemas.admin_schemas import create_parser, update_parser
from backend.core.services.news_service.news_image_service import (get_photos_for_news,
                                                                   add_photo_to_news, delete_photo_from_news)
from . import admin_ns
from .decorators import admin_required
from ...core.services.news_service.news_service import create_news_with_images, get_all_news, get_news_by_id, \
    update_news, delete_news


@admin_ns.route('/news')
class NewsResource(Resource):
    @admin_required
    @admin_ns.expect(create_parser)
    @admin_ns.doc(description="Создание новости")
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Создание новости с прикрепленными изображениями
        """
        data_str: str = request.form.get("data", "")
        images: List = request.files.getlist("image")
        user_email: str = get_jwt_identity()

        response, status = create_news_with_images(user_email, data_str, images)
        return response, status

    @admin_required
    @admin_ns.doc(description="Получение всех новостей")
    def get(self) -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
        """
        Получение списка всех новостей
        """
        news_data: List[Dict[str, Any]] = get_all_news()
        return {"news": news_data}, HTTPStatus.OK


@admin_ns.route('/news/<int:news_id>')
class NewsDetailResource(Resource):
    @admin_required
    def get(self, news_id: int) -> tuple[dict, int]:
        """
        Получение конкретной новости по ID.

        :param news_id: Идентификатор новости
        :return: JSON с данными новости или сообщение об ошибке
        """
        news = get_news_by_id(news_id)
        if not news:
            return {"message": "Новость не найдена"}, HTTPStatus.NOT_FOUND
        return news.to_dict(), HTTPStatus.OK

    @admin_required
    @admin_ns.expect(update_parser)
    def put(self, news_id: int) -> tuple[dict, int]:
        """
        Обновление новости по ID.

        :param news_id: Идентификатор новости
        :return: JSON с обновленной новостью или сообщение об ошибке
        """
        args = update_parser.parse_args()
        form_data: dict = {'data': args['data']}
        files: Optional[dict] = {'image': args.getlist('image')} if args.get('image') else None

        news, error = update_news(news_id, form_data, files)
        if error:
            return ({
                        "message": error}, HTTPStatus.BAD_REQUEST if "JSON" in error or "обязательно" in error
                    else HTTPStatus.NOT_FOUND)
        return {"message": "Новость обновлена", "news": news.to_dict()}, HTTPStatus.OK

    @admin_required
    def delete(self, news_id: int) -> tuple[dict, int]:
        """
        Удаление новости по ID (только для администратора).

        :param news_id: Идентификатор новости
        :return: Сообщение об успешном удалении или об ошибке
        """
        success, error = delete_news(news_id)
        if not success:
            return {"message": error}, HTTPStatus.NOT_FOUND
        return {"message": "Новость удалена"}, HTTPStatus.OK


@admin_ns.route('/news/<int:news_id>/photos')
class AdminNewsPhotosResource(Resource):
    @admin_required
    def get(self, news_id: int) -> tuple[dict, int]:
        """
        Получение списка всех фото для конкретной новости.

        :param news_id: Идентификатор новости
        :return: JSON с массивом фото или сообщение об ошибке
        """
        photos, error, status = get_photos_for_news(news_id)
        if error:
            return error, status
        return {"photos": photos}, status

    @admin_required
    @admin_ns.doc(
        description="Загрузка фото для новости",
        params={
            'photo': {
                'description': 'Файл фотографии',
                'in': 'formData',
                'type': 'file',
                'required': True
            }
        }
    )
    def post(self, news_id: int) -> tuple[dict, int]:
        """
        Загрузка нового фото для конкретной новости.

        :param news_id: Идентификатор новости
        :return: JSON с сообщением и обновленным списком фото или сообщение об ошибке
        """
        if 'photo' not in request.files:
            return {"message": "Фото не загружено"}, HTTPStatus.BAD_REQUEST

        photo_file = request.files['photo']
        photos, error, status = add_photo_to_news(news_id, photo_file)
        if error:
            return error, status

        photos, _, status = get_photos_for_news(news_id)
        return {"message": "Фото добавлено", "photos": photos}, status


@admin_ns.route('/news/<int:news_id>/photos/<int:photo_id>')
class AdminNewsPhotoResource(Resource):
    @admin_required
    def delete(self, news_id: int, photo_id: int) -> tuple[dict, int]:
        """
        Удаление конкретного фото новости по ID.

        :param news_id: Идентификатор новости
        :param photo_id: Идентификатор фото
        :return: Сообщение об успешном удалении или ошибка
        """
        result, status = delete_photo_from_news(news_id, photo_id)
        if not result:
            return {"message": "Фото не найдено или не удалось удалить"}, status
        return {"message": "Фото удалено"}, status
