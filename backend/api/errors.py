from http import HTTPStatus

from flask import current_app, request
from flask_restx import Resource
from werkzeug.exceptions import HTTPException

from backend.core.errors import ApiError
from backend.core.utilits.request_utils import require_json_object


def error_response(error: ApiError, status_code: int | None = None) -> tuple[dict, int]:
    """Preserve the public API's message-only JSON error format."""
    return {"message": str(error)}, error.status_code if status_code is None else status_code


def http_error_response(error: HTTPException):
    payload = dict(getattr(error, "data", None) or {})
    payload.setdefault("message", error.description)
    headers = [(key, value) for key, value in error.get_headers() if key.lower() != "content-type"]
    return payload, error.code or HTTPStatus.INTERNAL_SERVER_ERROR, headers


def ensure_error_message(response):
    """Guarantee a JSON message on error responses while retaining existing fields."""
    if response.status_code < 400:
        return response

    payload = response.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = {"data": payload} if payload is not None else {}
    if isinstance(payload.get("message"), str) and payload["message"].strip():
        return response

    message = next((payload[key] for key in ("msg", "error", "detail")
                    if isinstance(payload.get(key), str) and payload[key].strip()), None)
    if message is None:
        try:
            message = HTTPStatus(response.status_code).phrase
        except ValueError:
            message = "Request failed"
    payload["message"] = message
    response.set_data(current_app.json.dumps(payload))
    response.mimetype = "application/json"
    return response


class ApiResource(Resource):
    def validate_payload(self, func):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.is_json and request.content_length:
            require_json_object(request.get_json())
        return super().validate_payload(func)

    def dispatch_request(self, *args, **kwargs):
        try:
            return super().dispatch_request(*args, **kwargs)
        except Exception as error:
            # Use Flask's registered handlers, including JWT callbacks, in every mode.
            # This also preserves parser details and avoids RESTX's 404 suggestions.
            return current_app.extensions["flask_error_handler"](error)
