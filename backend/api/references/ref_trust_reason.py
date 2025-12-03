from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core import db
from backend.core.models.ref_models import TrustReason

trust_reason_model = ref_ns.model('TrustReason', {
    'title': fields.String(required=True, description='Название причины доверия'),
    'description': fields.String(required=False, description='Описание причины'),
})


@ref_ns.route('/trust-reasons')
class TrustReasonList(Resource):

    @ref_ns.doc(description="Список причин, почему нам доверяют")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех причин доверия.

        Returns:
            list[dict]: Список причин.
        """
        reasons = TrustReason.query.all()
        return [r.to_dict() for r in reasons], 200

    @admin_required
    @ref_ns.expect(trust_reason_model)
    @ref_ns.doc(description="Создание новой причины доверия")
    def post(self) -> tuple[dict, int]:
        """
        Создание новой причины доверия.

        JSON body:
            title (str): Название (обязательно)
            description (str): Описание
        """
        data = request.json or {}

        title = data.get('title')
        if not title:
            return {'message': 'Поле title обязательно'}, 400

        reason = TrustReason(
            title=title,
            description=data.get('description')
        )

        db.session.add(reason)
        db.session.commit()

        return reason.to_dict(), 201


@ref_ns.route('/trust-reasons/<int:id>')
class TrustReasonResource(Resource):

    @admin_required
    @ref_ns.doc(description="Удаление причины доверия по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление причины доверия по ID.
        """
        reason = TrustReason.query.get(id)
        if not reason:
            return {'message': 'Причина не найдена'}, 404

        db.session.delete(reason)
        db.session.commit()

        return {'message': 'Причина удалена'}, 200
