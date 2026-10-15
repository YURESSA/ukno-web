from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended import jwt_required as _jwt_required

from backend.core.models.auth_models import RoleEnum
from backend.core.services.user_services.user_service import get_user_by_email


def jwt_required(*args, **kwargs):
    """Keep JWT behavior intact and expose its security requirement to Swagger."""
    decorate = _jwt_required(*args, **kwargs)

    def decorator(fn):
        wrapped = decorate(fn)
        wrapped.api_auth = "optional" if kwargs.get("optional") else "jwt"
        return wrapped

    return decorator


def role_required(required_role: RoleEnum, denied_message: str):
    """Require the role in both the JWT and the current database record."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user = get_user_by_email(get_jwt_identity())
            try:
                token_role = RoleEnum(claims.get("role", ""))
            except ValueError:
                token_role = None

            # Recheck the database so a demoted user loses access immediately.
            if not user or user.role != required_role or token_role != required_role:
                return {"message": denied_message}, HTTPStatus.FORBIDDEN
            return fn(*args, **kwargs)

        wrapper.api_auth = required_role.value
        return wrapper

    return decorator
