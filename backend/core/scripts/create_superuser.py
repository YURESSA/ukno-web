import os
import sys
from getpass import getpass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(BASE_DIR)

from backend.core import create_app, db
from backend.core.models.auth_models import Role, User

def create_superuser():
    print("=== Создание суперпользователя ===")
    username = input("Имя пользователя: ").strip()
    full_name = input("Полное имя: ").strip()
    email = input("Email: ").strip()
    phone = input("Телефон (необязательно): ").strip()
    password = getpass("Пароль: ")
    confirm_password = getpass("Подтвердите пароль: ")

    if password != confirm_password:
        print("❌ Пароли не совпадают.")
        return

    if User.query.filter((User.username == username) | (User.email == email)).first():
        print("❌ Пользователь с таким именем или email уже существует.")
        return

    admin_role = Role.query.filter_by(role_name='admin').first()
    if not admin_role:
        print("❌ Роль 'admin' не найдена.")
        return

    new_user = User(
        username=username,
        full_name=full_name,
        email=email,
        phone=phone,
        role_id=admin_role.role_id
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    print(f"✅ Суперпользователь '{username}' успешно создан.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_superuser()
