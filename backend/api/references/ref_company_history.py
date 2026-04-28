from http import HTTPStatus
from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core.services.ref_service.company_history_service import get_all_history, create_history, \
    get_history_by_id, update_history, delete_history, validate_history_data

history_model = ref_ns.model('CompanyHistory', {
    'title': fields.String(required=True, description='Название события'),
    'link': fields.String(required=True, description='Ссылка на событие'),
    'date': fields.String(required=True, description='Дата события (YYYY-MM-DD)', example='2025-12-11'),
    'description': fields.String(required=True, description='Описание события'),
})


@ref_ns.route('/history')
class CompanyHistoryList(Resource):

    @ref_ns.doc(description="Список всех событий в истории компании")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех записей таймлайна.

        **Ответ:**
            200 OK: Список объектов CompanyHistory
            [
                {
                    "id": 1,
                    "link": "https://example.com/event1",
                    "date": "2025-12-11",
                    "description": "Описание события 1"
                },
                ...
            ]
        """
        items = get_all_history()
        return [i.to_dict() for i in items], HTTPStatus.OK

    @admin_required
    @ref_ns.expect(history_model)
    @ref_ns.doc(description="Добавление события в историю компании")
    def post(self) -> tuple[dict, int]:
        """
        Создание записи в таймлайне.

        JSON body:
            link (str): Ссылка (обязательно)
            date (str): Дата (формат YYYY-MM-DD)
            description (str): Описание (обязательно)
            title (str): Название события (обязательно)

        **Ответы:**
            201 Created: Возвращает созданное событие
            400 Bad Request: Ошибка валидации полей
        """

        data = request.json or {}
        try:
            title, link, date_str, description = validate_history_data(data)
            item = create_history(title, link, date_str, description)
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST

        return item.to_dict(), HTTPStatus.CREATED


@ref_ns.route('/history/<int:id>')
class CompanyHistoryResource(Resource):

    @ref_ns.doc(description="Получение события по ID")
    def get(self, id: int) -> tuple[dict, int]:
        """
        Получение события по его ID.

        Параметры:
            id (int): ID события

        **Ответы:**
            200 OK: Возвращает объект события
            404 Not Found: Если событие с указанным ID не найдено
        """
        item = get_history_by_id(id)
        if not item:
            return {'message': 'Событие не найдено'}, HTTPStatus.NOT_FOUND
        return item.to_dict(), HTTPStatus.OK

    @admin_required
    @ref_ns.expect(history_model)
    @ref_ns.doc(description="Обновление события по ID")
    def put(self, id: int) -> tuple[dict, int]:
        """
        Обновление события по его ID.

        Параметры:
            id (int): ID события

        JSON body:
            link (str): Ссылка
            date (str): Дата (обязательно, формат YYYY-MM-DD)
            description (str): Описание (обязательно)
            title (str): Название события (обязательно)

        **Ответы:**
            200 OK: Возвращает обновлённое событие
            400 Bad Request: Ошибка валидации полей
            404 Not Found: Если событие с указанным ID не найдено
        """
        item = get_history_by_id(id)
        if not item:
            return {'message': 'Событие не найдено'}, HTTPStatus.NOT_FOUND

        data = request.json or {}
        try:
            title, link, date_str, description = validate_history_data(data)
            update_history(item, title, link, date_str, description)
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST

        return item.to_dict(), HTTPStatus.OK

    @admin_required
    @ref_ns.doc(description="Удаление события по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление записи истории компании по ID.

        Параметры:
            id (int): ID события

        **Ответы:**
            200 OK: {"message": "Событие удалено"}
            404 Not Found: Если событие с указанным ID не найдено
        """
        item = get_history_by_id(id)
        if not item:
            return {'message': 'Событие не найдено'}, HTTPStatus.NOT_FOUND

        delete_history(item)
        return {'message': 'Событие удалено'}, HTTPStatus.OK
