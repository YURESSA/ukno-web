from backend.api.decorators import role_required
from backend.core.messages import AuthMessages
from backend.core.models.auth_models import RoleEnum


def admin_required(fn):
    return role_required(RoleEnum.ADMIN, AuthMessages.AUTH_ACCESS_DENIED)(fn)
