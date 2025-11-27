from typing import Optional

from flask import current_app
from itsdangerous import URLSafeTimedSerializer


def generate_reset_token(email: str, expires_sec: int = 3600) -> str:
    """
    Генерирует токен для сброса пароля.

    :param email: email пользователя
    :param expires_sec: срок действия токена в секундах
    :return: токен
    """
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt='password-reset-salt')


def verify_reset_token(token: str, max_age: int = 3600) -> Optional[str]:
    """
    Проверяет токен сброса пароля.

    :param token: токен
    :param max_age: максимальный возраст токена в секундах
    :return: email пользователя если токен валиден, иначе None
    """
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=max_age)
    except Exception:
        return None
    return email
