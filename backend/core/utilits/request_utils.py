from backend.core.errors import ValidationError


def require_json_object(value) -> dict:
    """Reject valid JSON of the wrong shape before services call dict methods."""
    if not isinstance(value, dict):
        raise ValidationError("JSON должен содержать объект")
    return value
