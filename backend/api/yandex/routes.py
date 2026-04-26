from flask import request
from flask_restx import Resource

from backend.api.admin.decorators import admin_required
from . import yandex_ns
from backend.core.services.yandex_service.yandex_service import get_yandex_suggestions


@yandex_ns.route('/map-helper')
class MapHelperResource(Resource):

    @admin_required
    def get(self):
        suggest_query = request.args.get('suggest')

        if not suggest_query:
            return {"message": "Необходим параметр suggest"}, 400

        try:
            data = get_yandex_suggestions(suggest_query)
            return data, 200
        except Exception as e:
            return {"message": f"Ошибка сервиса Яндекса: {str(e)}"}, 500
