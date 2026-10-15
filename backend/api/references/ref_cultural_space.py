from http import HTTPStatus

from flask_restx import reqparse
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.errors import ApiResource, error_response
from backend.api.references import ref_ns
from backend.core.errors import NotFoundError, ValidationError
from backend.core.services.ref_service.cultural_space_service import get_all_cultural_spaces, create_cultural_space, \
    update_cultural_space, delete_cultural_space, upload_cultural_space_photo, get_cultural_space_by_id, \
    delete_cultural_space_photo

cultural_space_parser = reqparse.RequestParser()
cultural_space_parser.add_argument('text', type=str, required=True, location='form')
cultural_space_parser.add_argument('photo', type=FileStorage, required=False, location='files')
cultural_space_parser.add_argument('order_index', type=int, required=False, location='form')

photo_parser = reqparse.RequestParser()
photo_parser.add_argument('photo', type=FileStorage, required=True, location='files')


@ref_ns.route('/cultural-space')
class CulturalSpaceList(ApiResource):

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
        return [i.to_dict() for i in items], HTTPStatus.OK

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
        item = create_cultural_space(args.get('text'), args.get('photo'), args.get('order_index'))
        return item.to_dict(), HTTPStatus.CREATED


@ref_ns.route('/cultural-space/<int:id>')
class CulturalSpaceResource(ApiResource):

    @ref_ns.doc(description="Получение элемента культурного пространства по ID")
    def get(self, id: int):
        """
        Получение элемента культурного пространства по ID.

        **Ответы:**
            200 OK: Возвращает объект элемента
            404 Not Found: Если элемент не найден
        """
        item = get_cultural_space_by_id(id)
        if not item:
            raise NotFoundError('Элемент не найден')
        return item.to_dict(), HTTPStatus.OK

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
        item = get_cultural_space_by_id(id)
        if not item:
            raise NotFoundError('Элемент не найден')
        args = cultural_space_parser.parse_args()
        item = update_cultural_space(item, args.get('text'), args.get('order_index'))
        return item.to_dict(), HTTPStatus.OK

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
        item = get_cultural_space_by_id(id)
        if not item:
            raise NotFoundError('Элемент не найден')
        delete_cultural_space(item)
        return {'message': 'Элемент удалён'}, HTTPStatus.OK


@ref_ns.route('/cultural-space/<int:id>/photo')
class CulturalSpacePhotoResource(ApiResource):

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
        delete_cultural_space_photo(id)

        return {'message': 'Фото удалено'}, HTTPStatus.OK

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
        item = get_cultural_space_by_id(id)
        if not item:
            raise NotFoundError('Элемент не найден')
        args = photo_parser.parse_args()
        try:
            photo_path = upload_cultural_space_photo(item, args.get('photo'))
        except ValidationError as error:
            # Preserve this endpoint's legacy 404 response for invalid uploads.
            return error_response(error, HTTPStatus.NOT_FOUND)
        return {'message': 'Фото загружено', 'photo_path': photo_path}, HTTPStatus.OK
