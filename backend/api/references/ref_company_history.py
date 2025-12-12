from typing import Any
from datetime import datetime, date

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core import db
from backend.core.models.ref_models import CompanyHistory

history_model = ref_ns.model('CompanyHistory', {
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
        """
        items = CompanyHistory.query.all()
        return [i.to_dict() for i in items], 200

    @admin_required
    @ref_ns.expect(history_model)
    @ref_ns.doc(description="Добавление события в историю компании")
    def post(self) -> tuple[dict, int]:
        """
        Создание записи в таймлайне.

        JSON body:
            link (str): Ссылка (обязательно)
            date (str): Дата (обязательно)
            description (str): Описание (обязательно)
        """
        data = request.json or {}

        link = data.get('link')
        date_str = data.get('date')
        description = data.get('description')

        if not link:
            return {'message': 'Поле link обязательно'}, 400
        if not date_str:
            return {'message': 'Поле date обязательно'}, 400
        if not description:
            return {'message': 'Поле description обязательно'}, 400

        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Неверный формат даты. Используйте YYYY-MM-DD'}, 400

        item = CompanyHistory(
            link=link,
            date=event_date,
            description=description
        )

        db.session.add(item)
        db.session.commit()

        return item.to_dict(), 201


@ref_ns.route('/history/<int:id>')
class CompanyHistoryResource(Resource):

    @ref_ns.doc(description="Получение события по ID")
    def get(self, id: int) -> tuple[dict, int]:
        item = CompanyHistory.query.get(id)
        if not item:
            return {'message': 'Событие не найдено'}, 404
        return item.to_dict(), 200

    @admin_required
    @ref_ns.expect(history_model)
    @ref_ns.doc(description="Обновление события по ID")
    def put(self, id: int) -> tuple[dict, int]:
        item = CompanyHistory.query.get(id)
        if not item:
            return {'message': 'Событие не найдено'}, 404

        data = request.json or {}
        link = data.get('link')
        date_str = data.get('date')
        description = data.get('description')

        if not link:
            return {'message': 'Поле link обязательно'}, 400
        if not date_str:
            return {'message': 'Поле date обязательно'}, 400
        if not description:
            return {'message': 'Поле description обязательно'}, 400

        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Неверный формат даты. Используйте YYYY-MM-DD'}, 400

        item.link = link
        item.date = event_date
        item.description = description

        db.session.commit()

        return item.to_dict(), 200

    @admin_required
    @ref_ns.doc(description="Удаление события по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление записи истории компании.
        """
        item = CompanyHistory.query.get(id)
        if not item:
            return {'message': 'Событие не найдено'}, 404

        db.session.delete(item)
        db.session.commit()

        return {'message': 'Событие удалено'}, 200
