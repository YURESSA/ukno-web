from http import HTTPStatus


class ApiError(ValueError):
    """An expected service error; ValueError compatibility supports existing callers."""
    status_code = HTTPStatus.BAD_REQUEST


class ValidationError(ApiError):
    """Invalid input or an operation that cannot be performed."""


class NotFoundError(ApiError):
    """The requested entity does not exist."""
    status_code = HTTPStatus.NOT_FOUND
