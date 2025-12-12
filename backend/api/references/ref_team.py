import os
from typing import Any

from flask_restx import Resource, reqparse
from flask_restx import fields
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core import db
from backend.core.models.ref_models import TeamMember
from backend.core.utilits.file_utils import save_image, remove_file_if_exists

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
        Получение всех сотрудников компании.

        Returns:
            list[dict]: сотрудников проектов.
        """
        members = TeamMember.query.all()
        return [m.to_dict() for m in members], 200

    @admin_required
    @ref_ns.expect(upload_parser)
    @ref_ns.doc(description="Добавление сотрудника команды (photo — multipart/form-data)")
    def post(self):
        """
        Добавление сотрудника.
        """
        args = upload_parser.parse_args()

        full_name = args.get("full_name")
        description = args.get("description")
        photo = args.get("photo")

        if not full_name:
            return {'message': 'Поле full_name обязательно'}, 400

        photo_path = None

        if photo and photo.filename:
            if not photo.content_type.startswith("image/"):
                return {'message': 'Файл должен быть изображением'}, 400

            photo.seek(0, os.SEEK_END)
            size = photo.tell()
            photo.seek(0)

            if size > 5 * 1024 * 1024:
                return {'message': 'Размер файла не должен превышать 5 MB'}, 400

            photo_path = save_image(photo, "team_photos")

        member = TeamMember(
            full_name=full_name,
            description=description,
            photo=photo_path
        )

        db.session.add(member)
        db.session.commit()

        return member.to_dict(), 201


@ref_ns.route('/team/<int:id>')
class TeamResource(Resource):

    @ref_ns.doc(description="Получение сотрудника команды по ID")
    def get(self, id: int) -> tuple[dict, int]:
        """
        Получение сотрудника команды по его ID.

        Args:
            id (int): ID сотрудника

        Returns:
            dict: Данные сотрудника
            int: HTTP статус код (200 если найден, 404 если нет)
        """
        member = TeamMember.query.get(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, 404
        return member.to_dict(), 200

    @admin_required
    @ref_ns.doc(description="Удаление сотрудника команды по ID")
    def delete(self, id: int) -> tuple[dict, int]:
        """
        Удаление сотрудника компании вместе с файлом фотографии.

        Args:
            id (int): ID сотрудника для удаления

        Returns:
            dict: Сообщение о результате операции
            int: HTTP статус код (200 при успешном удалении, 404 если сотрудник не найден)
        """
        member = TeamMember.query.get(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, 404

        if member.photo:
            remove_file_if_exists(member.photo)

        db.session.delete(member)
        db.session.commit()

        return {'message': 'Сотрудник удалён'}, 200

    @admin_required
    @ref_ns.expect(upload_parser)
    @ref_ns.doc(description="Обновление данных сотрудника (без фото)")
    def put(self, id: int):
        """
        Обновление данных сотрудника. Фото обновляется отдельно через /team/<id>/photo.
        """
        member = TeamMember.query.get(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, 404

        args = upload_parser.parse_args()
        full_name = args.get('full_name')
        description = args.get('description')

        if not full_name:
            return {'message': 'Поле full_name обязательно'}, 400

        member.full_name = full_name
        member.description = description

        db.session.commit()
        return member.to_dict(), 200


photo_parser = reqparse.RequestParser()
photo_parser.add_argument('photo', type=FileStorage, required=True, location='files')


@ref_ns.route('/team/<int:id>/photo')
class TeamPhotoResource(Resource):

    @admin_required
    @ref_ns.doc(description="Удаление фото сотрудника")
    def delete(self, id: int):
        """
        Удаление фото сотрудника.
        """
        member = TeamMember.query.get(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, 404

        if not member.photo:
            return {'message': 'Фото отсутствует'}, 400

        remove_file_if_exists(member.photo)
        member.photo = None
        db.session.commit()

        return {'message': 'Фото удалено'}, 200

    @admin_required
    @ref_ns.expect(photo_parser)
    @ref_ns.doc(description="Загрузка нового фото сотрудника")
    def post(self, id: int):
        """
        Добавление/замена фото сотрудника.
        """
        member = TeamMember.query.get(id)
        if not member:
            return {'message': 'Сотрудник не найден'}, 404

        args = photo_parser.parse_args()
        photo = args.get('photo')

        if not photo or not photo.filename:
            return {'message': 'Файл не выбран'}, 400

        if not photo.content_type.startswith("image/"):
            return {'message': 'Файл должен быть изображением'}, 400

        photo.seek(0, os.SEEK_END)
        size = photo.tell()
        photo.seek(0)

        if size > 5 * 1024 * 1024:
            return {'message': 'Размер файла не должен превышать 5 MB'}, 400

        # Удаляем старое фото
        if member.photo:
            remove_file_if_exists(member.photo)

        member.photo = save_image(photo, "team_photos")
        db.session.commit()

        return {'message': 'Фото загружено', 'photo_path': member.photo}, 200
