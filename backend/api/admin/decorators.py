from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from backend.core.messages import AuthMessages
from backend.core.models.auth_models import RoleEnum
from backend.core.services.user_services.user_service import get_user_by_email


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Проверка JWT
        verify_jwt_in_request()
        claims = get_jwt()
        email = get_jwt_identity()
        user = get_user_by_email(email)

        role_str = claims.get("role", "")
        try:
            role_enum = RoleEnum(role_str)
        except ValueError:
            role_enum = None

        if not user or role_enum != RoleEnum.ADMIN:
            return {"message": AuthMessages.AUTH_ACCESS_DENIED}, HTTPStatus.FORBIDDEN

        return fn(*args, **kwargs)

    return wrapper
