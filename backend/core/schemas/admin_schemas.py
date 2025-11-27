from flask_restx import fields, reqparse
from werkzeug.datastructures import FileStorage

from backend.api.admin import admin_ns

admin_login = admin_ns.model('AdminLogin', {
    'email': fields.String(required=True, description='Электронная почта администратора', example='admin@example.com'),
    'password': fields.String(required=True, description='Пароль администратора', example='admin123')
})

create_parser = reqparse.RequestParser()
create_parser.add_argument(
    'data', type=str, location='form', required=True,
    help='JSON строка с полями title, content, photo_author'
)
create_parser.add_argument(
    'image', type=FileStorage, location='files', action='append', required=False,
    help='Файлы изображений для новости (можно несколько)'
)

update_parser = reqparse.RequestParser()
update_parser.add_argument(
    'data', type=str, location='form', required=True,
    help='JSON строка с полями title, content, photo_author'
)
update_parser.add_argument(
    'image', type=FileStorage, location='files', action='append', required=False,
    help='Файлы изображений для новости (можно несколько)'
)

update_user_model = admin_ns.model(
    "UpdateUser",
    {
        "full_name": fields.String(required=False, description="Полное имя пользователя"),
        "email": fields.String(required=False, description="Новая электронная почта"),
        "phone": fields.String(required=False, description="Телефон пользователя"),
        "password": fields.String(required=False, description="Новый пароль"),
        "role_name": fields.String(required=False, description="Роль пользователя (user, resident, admin)")
    }
)
