from backend.api.decorators import role_required
from backend.core.models.auth_models import RoleEnum


def resident_required(fn):
    return role_required(RoleEnum.RESIDENT, "Доступ запрещён")(fn)
