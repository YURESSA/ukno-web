from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity

from backend.core.services.user_services.user_service import get_user_by_email


def resident_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        email = get_jwt_identity()
        user = get_user_by_email(email)
        if claims.get("role") != "resident" or not user:
            return {"message": "Доступ запрещён"}, HTTPStatus.FORBIDDEN
        return fn(*args, **kwargs)

    return wrapper
