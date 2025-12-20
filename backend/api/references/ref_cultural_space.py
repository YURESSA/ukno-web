from flask_restx import Resource, reqparse
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core import db
from backend.core.models.ref_models import CulturalSpace
from backend.core.services.ref_service.cultural_space_service import get_all_cultural_spaces, create_cultural_space, \
    update_cultural_space, delete_cultural_space, upload_cultural_space_photo

cultural_space_parser = reqparse.RequestParser()
cultural_space_parser.add_argument('text', type=str, required=True, location='form')
cultural_space_parser.add_argument('photo', type=FileStorage, required=False, location='files')
cultural_space_parser.add_argument('order_index', type=int, required=False, location='form')

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
        items = get_all_cultural_spaces()
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
        try:
            item = create_cultural_space(args.get('text'), args.get('photo'), args.get('order_index'))
        except ValueError as e:
            return {'message': str(e)}, 400
        return item.to_dict(), 201


@ref_ns.route('/cultural-space/<int:id>')
class CulturalSpaceResource(Resource):

    @ref_ns.doc(description="Получение элемента культурного пространства по ID")
    def get(self, id: int):
        """
        Получение элемента культурного пространства по ID.

        **Ответы:**
            200 OK: Возвращает объект элемента
            404 Not Found: Если элемент не найден
        """
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404
        return item.to_dict(), 200

    @admin_required
    @ref_ns.expect(cultural_space_parser)
    @ref_ns.doc(description="Обновление элемента культурного пространства (без фото)")
    def put(self, id: int):
        """
        Обновление текста элемента культурного пространства.
        Фото обновляется отдельно через /cultural-space/<id>/photo.

        Form data:
            text (str, обязательное): Новый текст элемента

        **Ответы:**
            200 OK: Возвращает обновлённый элемент
            400 Bad Request: Ошибка валидации
            404 Not Found: Элемент не найден
        """
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404
        args = cultural_space_parser.parse_args()
        try:
            item = update_cultural_space(item, args.get('text'), args.get('order_index'))
        except ValueError as e:
            return {'message': str(e)}, 400
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
        delete_cultural_space(item)
        return {'message': 'Элемент удалён'}, 200


@ref_ns.route('/cultural-space/<int:id>/photo')
class CulturalSpacePhotoResource(Resource):

    @admin_required
    @ref_ns.doc(description="Удаление фото элемента культурного пространства")
    def delete(self, id: int):
        """
        Удаление фото элемента культурного пространства.

        **Ответы:**
            200 OK: {"message": "Фото удалено"}
            400 Bad Request: Фото отсутствует
            404 Not Found: Элемент не найден
        """
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404
        if not item.photo:
            return {'message': 'Фото отсутствует'}, 400
        upload_cultural_space_photo(item, None)
        item.photo = None
        db.session.commit()
        return {'message': 'Фото удалено'}, 200

    @admin_required
    @ref_ns.expect(photo_parser)
    @ref_ns.doc(description="Загрузка нового фото элемента культурного пространства")
    def post(self, id: int):
        """
        Добавление или замена фото элемента культурного пространства.

        Form data:
            photo (file, обязательное)

        **Ответы:**
            200 OK: {"message": "Фото загружено", "photo_path": путь к файлу}
            400 Bad Request: Некорректный файл или превышен размер
            404 Not Found: Элемент не найден
        """
        item = CulturalSpace.query.get(id)
        if not item:
            return {'message': 'Элемент не найден'}, 404
        args = photo_parser.parse_args()
        try:
            photo_path = upload_cultural_space_photo(item, args.get('photo'))
        except ValueError as e:
            return {'message': str(e)}, 400
        return {'message': 'Фото загружено', 'photo_path': photo_path}, 200
