from http import HTTPStatus
from typing import Any

from flask import request
from flask_restx import Resource, fields

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core.services.ref_service.trust_reason_service import get_all_trust_reasons, create_trust_reason, \
    delete_trust_reason

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
        reasons = get_all_trust_reasons()
        return [r.to_dict() for r in reasons], HTTPStatus.OK

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
        try:
            reason = create_trust_reason(
                title=data.get('title'),
                description=data.get('description')
            )
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST
        return reason.to_dict(), HTTPStatus.CREATED


@ref_ns.route('/trust-reasons/<int:id>')
class TrustReasonResource(Resource):

    @admin_required
    @ref_ns.doc(description="Удаление причины доверия по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление причины доверия по ID.
        """
        try:
            delete_trust_reason(id)
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.NOT_FOUND
        return {'message': 'Причина удалена'}, HTTPStatus.OK
