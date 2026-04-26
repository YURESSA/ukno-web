from http import HTTPStatus

from flask import request, current_app
from flask_restx import Resource, fields

from backend.api.frontend_logs import frontend_logs_ns

log_model = frontend_logs_ns.model('FrontendLog', {
    'message': fields.String(required=True),
    'stack': fields.String,
    'url': fields.String,
    'component': fields.String,
    'userAgent': fields.String,
    'level': fields.String(enum=['error', 'warning', 'info'], default='error')
})


@frontend_logs_ns.route('/')
class FrontendLogResource(Resource):

    @frontend_logs_ns.expect(log_model, validate=True)
    def post(self):
        data = request.json

        current_app.logger.error(
            "[FRONTEND ERROR] "
            f"level={data.get('level')} "
            f"message={data.get('message')} "
            f"url={data.get('url')} "
            f"component={data.get('component')} "
            f"UA={data.get('userAgent')}\n"
            f"stack={data.get('stack')}"
        )

        return {"status": "logged"}, HTTPStatus.CREATED
