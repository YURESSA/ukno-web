from http import HTTPStatus
from typing import Any

from flask_restx import Resource, reqparse
from flask_restx import fields
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core.services.ref_service.team_service import get_team_members, create_team_member, upload_team_photo, \
    delete_team_photo, get_team_member_by_id, update_team_member, delete_team_member

team_member_model = ref_ns.model('TeamMember', {
    'full_name': fields.String(required=True, description='ФИО сотрудника'),
    'description': fields.String(required=False, description='Описание сотрудника'),
})

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('full_name', type=str, required=True, location='form')
upload_parser.add_argument('description', type=str, required=False, location='form')
upload_parser.add_argument('photo', type=FileStorage, required=False, location='files')


@ref_ns.route('/team')
class TeamList(Resource):

    @ref_ns.doc(description="Список сотрудников команды")
    def get(self) -> tuple[list[Any], int]:
        """
        Получение всех сотрудников команды.

        **Ответ:**
            200 OK: Список объектов TeamMember
            [
                {
                    "id": 1,
                    "full_name": "Иван Иванов",
                    "description": "Описание сотрудника",
                    "photo": "/path/to/photo.jpg"
                },
                ...
            ]
        """
        members = get_team_members()
        return [m.to_dict() for m in members], HTTPStatus.OK

    @admin_required
    @ref_ns.expect(upload_parser)
    @ref_ns.doc(description="Добавление сотрудника команды (photo — multipart/form-data)")
    def post(self):
        """
        Добавление нового сотрудника команды.

        Form data:
            full_name (str, обязательное): ФИО сотрудника
            description (str, необязательное): Описание сотрудника
            photo (file, необязательное): Фото сотрудника

        **Ответы:**
            201 Created: Возвращает созданного сотрудника
            400 Bad Request: Ошибка валидации
        """
        args = upload_parser.parse_args()

        try:
            member = create_team_member(
                full_name=args.get('full_name'),
                description=args.get('description'),
                photo=args.get('photo')
            )
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST

        return member.to_dict(), HTTPStatus.CREATED


@ref_ns.route('/team/<int:id>')
class TeamResource(Resource):

    @ref_ns.doc(description="Получение сотрудника команды по ID")
    def get(self, id: int) -> tuple[dict, int]:
        """
        Получение сотрудника по ID.

        **Ответы:**
            200 OK: Возвращает объект сотрудника
            404 Not Found: Если сотрудник не найден
        """
        member = get_team_member_by_id(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, HTTPStatus.NOT_FOUND

        return member.to_dict(), HTTPStatus.OK

    @admin_required
    @ref_ns.doc(description="Удаление сотрудника команды по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление сотрудника компании вместе с фотографией.

        **Ответы:**
            200 OK: {"message": "Сотрудник удалён"}
            404 Not Found: Если сотрудник не найден
        """
        member = get_team_member_by_id(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, HTTPStatus.NOT_FOUND

        delete_team_member(member)
        return {'message': 'Сотрудник удалён'}, HTTPStatus.OK

    @admin_required
    @ref_ns.expect(upload_parser)
    @ref_ns.doc(description="Обновление данных сотрудника (без фото)")
    def put(self, id: int):
        """
        Обновление данных сотрудника по ID.

        Form data:
            full_name (str, обязательное)
            description (str, необязательное)

        **Ответы:**
            200 OK: Возвращает обновлённого сотрудника
            400 Bad Request: Если не указано обязательное поле
            404 Not Found: Если сотрудник не найден
        """
        member = get_team_member_by_id(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, HTTPStatus.NOT_FOUND

        args = upload_parser.parse_args()

        try:
            member = update_team_member(
                member,
                full_name=args.get('full_name'),
                description=args.get('description')
            )
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST

        return member.to_dict(), HTTPStatus.OK


photo_parser = reqparse.RequestParser()
photo_parser.add_argument('photo', type=FileStorage, required=True, location='files')


@ref_ns.route('/team/<int:id>/photo')
class TeamPhotoResource(Resource):

    @admin_required
    @ref_ns.doc(description="Удаление фото сотрудника")
    def delete(self, id: int):
        """
        Удаление фото сотрудника.

        **Ответы:**
            200 OK: {"message": "Фото удалено"}
            400 Bad Request: Фото отсутствует
            404 Not Found: Сотрудник не найден
        """
        member = get_team_member_by_id(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, HTTPStatus.NOT_FOUND

        try:
            delete_team_photo(member)
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST

        return {'message': 'Фото удалено'}, HTTPStatus.OK

    @admin_required
    @ref_ns.expect(photo_parser)
    @ref_ns.doc(description="Загрузка нового фото сотрудника")
    def post(self, id: int):
        """
        Добавление или замена фото сотрудника.

        Form data:
            photo (file, обязательное)

        **Ответы:**
            200 OK: {"message": "Фото загружено", "photo_path": путь к файлу}
            400 Bad Request: Некорректный файл или превышен размер
            404 Not Found: Сотрудник не найден
        """
        member = get_team_member_by_id(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, HTTPStatus.NOT_FOUND

        args = photo_parser.parse_args()

        try:
            path = upload_team_photo(member, args.get('photo'))
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST

        return {'message': 'Фото загружено', 'photo_path': path}, HTTPStatus.OK
