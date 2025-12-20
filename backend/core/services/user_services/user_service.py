from http import HTTPStatus
from typing import Optional, List, Tuple, Dict

from flask_jwt_extended import create_access_token, get_jwt_identity

from backend.core import db
from backend.core.models.auth_models import User, RoleEnum
from backend.core.models.event_models import Event, Reservation


def get_user_by_email(email: str) -> Optional[User]:
    """
    Получение пользователя по email.

    :param email: Email пользователя
    :return: Объект User или None, если пользователь не найден
    """
    return User.query.filter_by(email=email).first()


def get_all_users(role: Optional[str] = None) -> List[User]:
    """
    Получение списка всех пользователей, с возможной фильтрацией по роли.

    :param role: Название роли для фильтрации (необязательно)
    :return: Список объектов User
    """
    query = User.query

    if role:
        query = query.filter(User.role.has(role=role))

    users = query.all()
    return users


def create_user(email: str, password: str, full_name: str, phone: str, role: RoleEnum) -> Optional[User]:
    """
    Создание нового пользователя.

    :param email: Email пользователя
    :param password: Пароль пользователя
    :param full_name: Полное имя пользователя
    :param phone: Телефон пользователя
    :param role: Название роли пользователя
    :return: Объект User или None, если роль не найдена или пользователь с таким email уже существует
    """
    if User.query.filter_by(email=email).first():
        return None

    new_user = User(
        email=email,
        full_name=full_name,
        phone=phone,
        role=role
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return new_user


def delete_user(email: str) -> Tuple[bool, str]:
    """
    Удаление пользователя по email с проверкой на созданные экскурсии и бронирования.

    :param email: Email пользователя
    :return: Кортеж (успех, сообщение)
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        return False, "Пользователь не найден"

    # Проверка, есть ли созданные экскурсии
    created_events = Event.query.filter_by(created_by=user.user_id).count()
    if created_events > 0:
        return False, f"Невозможно удалить пользователя: у него есть {created_events} созданных экскурсий"

    # Проверка активных бронирований
    active_reservations = Reservation.query.filter_by(user_id=user.user_id, is_cancelled=False).count()
    if active_reservations > 0:
        return False, f"Невозможно удалить пользователя: у него есть {active_reservations} активных бронирований"

    db.session.delete(user)
    db.session.commit()
    return True, "Пользователь успешно удалён"


def authenticate_user(email: str, password: str, required_role: Optional[str] = None) -> Optional[str]:
    """
    Аутентификация пользователя и генерация JWT токена.

    :param email: Email пользователя
    :param password: Пароль пользователя
    :param required_role: Если указано, проверяется роль пользователя
    :return: JWT токен при успешной аутентификации, иначе None
    """
    user = get_user_by_email(email)
    if not user or not user.check_password(password):
        return None

    if required_role:
        try:
            required_enum = RoleEnum(required_role)
        except ValueError:
            return None

        if user.role != required_enum:
            return None

    return create_access_token(
        identity=user.email,
        additional_claims={"role": user.role.value}
    )


def change_password(email: str, old_password: str, new_password: str) -> bool:
    """
    Изменение пароля пользователя.

    :param email: Email пользователя
    :param old_password: Текущий пароль
    :param new_password: Новый пароль
    :return: True, если пароль успешно изменён, иначе False
    """
    user = get_user_by_email(email)
    if user and user.check_password(old_password):
        user.set_password(new_password)
        db.session.commit()
        return True
    return False


def update_profile(data: dict) -> Tuple[Dict, int]:
    """
    Обновление профиля текущего пользователя.

    :param data: Словарь с новыми данными пользователя: 'email', 'phone', 'full_name'
    :return: Словарь с сообщением и HTTP-статус
    """
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    if not user:
        return {"message": "Пользователь не найден"}, HTTPStatus.NOT_FOUND

    new_email = data.get("email")
    new_phone = data.get("phone")
    new_full_name = data.get("full_name")

    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return {"message": "Этот email уже используется"}, HTTPStatus.BAD_REQUEST
        user.email = new_email

    if new_phone:
        user.phone = new_phone

    if new_full_name:
        user.full_name = new_full_name

    db.session.commit()
    return {"message": "Профиль обновлён успешно"}, HTTPStatus.OK


def update_user(email: str, data: dict) -> Optional['User']:
    """
    Обновление данных пользователя.

    :param email: текущий email пользователя для поиска
    :param data: словарь с полями для обновления. Возможные ключи:
                 - email
                 - full_name
                 - phone
                 - password
                 - role_name
    :return: объект User после обновления, либо None, если пользователь не найден
    :raises ValueError: если новый email уже используется или роль не найдена
    """
    user = get_user_by_email(email)
    if not user:
        return None

    if "email" in data and data["email"] != user.email:
        existing = User.query.filter_by(email=data["email"]).first()
        if existing:
            raise ValueError("Email уже используется другим пользователем")
        user.email = data["email"]

    if "full_name" in data:
        user.full_name = data["full_name"]

    if "phone" in data:
        user.phone = data["phone"]

    if "password" in data and data["password"]:
        user.set_password(data["password"])

    if "role_name" in data:
        role_name = data["role_name"]

        try:
            new_role = RoleEnum(role_name)
        except ValueError:
            raise ValueError(f"Роль '{role_name}' не найдена. Допустимые значения: admin, resident, user")

        user.role = new_role

    db.session.commit()
    return user
