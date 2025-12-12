import os

from flask_restx import Resource, reqparse
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core import db
from backend.core.models.ref_models import CulturalSpace
from backend.core.utilits.file_utils import save_image, remove_file_if_exists

cultural_space_parser = reqparse.RequestParser()
cultural_space_parser.add_argument('text', type=str, required=True, location='form')
cultural_space_parser.add_argument('photo', type=FileStorage, required=False, location='files')

photo_parser = reqparse.RequestParser()
photo_parser.add_argument('photo', type=FileStorage, required=True, location='files')


@ref_ns.route('/cultural-space')
class CulturalSpaceList(Resource):

    @ref_ns.doc(description="Список элементов культурного пространства")
    def get(self):
        """
        Получение всех элементов культурного пространства.

        Returns:
            list[dict]: Список элементов, каждый содержит:
                - id (int): ID элемента
                - text (str): Основной текст элемента
                - photo (str | None): Путь к загруженному изображению
        """
        items = CulturalSpace.query.all()
        return [i.to_dict() for i in items], 200

    @admin_required
    @ref_ns.expect(cultural_space_parser)
    @ref_ns.doc(description="Добавление элемента культурного пространства (photo — multipart/form-data)")
    def post(self):
        """
        Добавление нового элемента культурного пространства.

        Ожидает:
            - form-data:
                - text (str): Основной текст элемента (обязательно)
                - photo (file): Изображение (необязательно, формат image/*, макс. 5MB)

        Returns:
            dict: Добавленный элемент с полями:
                - id (int)
                - text (str)
                - photo (str | None)
            int: HTTP статус код (201 при успешном добавлении)
        """
        args = cultural_space_parser.parse_args()
        text = args.get('text')
        photo = args.get('photo')

        if not text:
            return {'message': 'Поле text обязательно'}, 400

        photo_path = None
        if photo and photo.filename:
            if not photo.content_type.startswith("image/"):
                return {'message': 'Файл должен быть изображением'}, 400

            photo.seek(0, os.SEEK_END)
            size = photo.tell()
            photo.seek(0)

            if size > 5 * 1024 * 1024:
                return {'message': 'Размер файла не должен превышать 5 MB'}, 400

            photo_path = save_image(photo, "cultural_space_photos")

        item = CulturalSpace(
            text=text,
            photo=photo_path
        )

        db.session.add(item)
        db.session.commit()

        return item.to_dict(), 201


@ref_ns.route('/cultural-space/<int:id>')
class CulturalSpaceResource(Resource):

    @admin_required
    @ref_ns.doc(description="Получение элемента культурного пространства по ID")
    def get(self, id: int):
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404
        return item.to_dict(), 200

    @admin_required
    @ref_ns.expect(cultural_space_parser)
    @ref_ns.doc(description="Обновление элемента культурного пространства (без фото)")
    def put(self, id: int):
        """
        Обновление текста элемента. Фото обновляется отдельно через /cultural-space/<id>/photo.
        """
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404

        args = cultural_space_parser.parse_args()
        text = args.get('text')
        if not text:
            return {'message': 'Поле text обязательно'}, 400

        item.text = text
        db.session.commit()
        return item.to_dict(), 200

    @admin_required
    @ref_ns.doc(description="Удаление элемента культурного пространства по ID")
    def delete(self, id: int):
        """
        Удаление элемента культурного пространства по ID вместе с файлом изображения.

        Args:
            id (int): ID элемента для удаления

        Returns:
            dict: Сообщение о результате операции
            int: HTTP статус код (200 при успешном удалении, 404 если элемент не найден)
        """
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404

        # Удаляем файл изображения, если он существует
        if item.photo:
            remove_file_if_exists(item.photo)

        db.session.delete(item)
        db.session.commit()
        return {'message': 'Элемент удалён'}, 200


@ref_ns.route('/cultural-space/<int:id>/photo')
class CulturalSpacePhotoResource(Resource):

    @admin_required
    @ref_ns.doc(description="Удаление фото элемента культурного пространства")
    def delete(self, id: int):
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404
        if not item.photo:
            return {'message': 'Фото отсутствует'}, 400

        remove_file_if_exists(item.photo)
        item.photo = None
        db.session.commit()
        return {'message': 'Фото удалено'}, 200

    @admin_required
    @ref_ns.expect(photo_parser)
    @ref_ns.doc(description="Загрузка нового фото элемента культурного пространства")
    def post(self, id: int):
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404

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

        if item.photo:
            remove_file_if_exists(item.photo)

        item.photo = save_image(photo, "cultural_space_photos")
        db.session.commit()
        return {'message': 'Фото загружено', 'photo_path': item.photo}, 200
