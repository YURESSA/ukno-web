from http import HTTPStatus
from typing import Optional, List, Tuple, Dict

from flask_jwt_extended import create_access_token, get_jwt_identity

from backend.core import db
from backend.core.models.auth_models import User, Role
from backend.core.services.user_services.role_service import get_role_by_name


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
        query = query.filter(User.role.has(role_name=role))

    users = query.all()
    return users


def create_user(email: str, password: str, full_name: str, phone: str, role_name: str) -> Optional[User]:
    """
    Создание нового пользователя.

    :param email: Email пользователя
    :param password: Пароль пользователя
    :param full_name: Полное имя пользователя
    :param phone: Телефон пользователя
    :param role_name: Название роли пользователя
    :return: Объект User или None, если роль не найдена или пользователь с таким email уже существует
    """
    role = get_role_by_name(role_name)
    if not role or User.query.filter_by(email=email).first():
        return None

    new_user = User(
        email=email,
        full_name=full_name,
        phone=phone,
        role_id=role.role_id
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return new_user


def delete_user(email: str) -> bool:
    """
    Удаление пользователя по email.

    :param email: Email пользователя
    :return: True, если пользователь удалён, False если пользователь не найден
    """
    user = get_user_by_email(email)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False


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

    if required_role and user.role.role_name != required_role:
        return None

    return create_access_token(identity=user.email, additional_claims={"role": user.role.role_name})


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

    if 'email' in data and data['email'] != user.email:
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            raise ValueError("Email уже используется другим пользователем")
        user.email = data['email']

    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    if 'role_name' in data:
        role_name = data['role_name']
        role = Role.query.filter_by(role_name=role_name).first()
        if not role:
            raise ValueError(f"Роль '{role_name}' не найдена")
        user.role_id = role.role_id

    db.session.commit()
    return user
