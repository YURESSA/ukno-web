from http import HTTPStatus

from flask_restx import reqparse
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.errors import ApiResource
from backend.api.references import ref_ns
from backend.core.errors import NotFoundError, ValidationError
from backend.core.services.ref_service.requisite_service import (
    get_all_requisites,
    create_requisite,
    update_requisite,
    delete_requisite,
    replace_requisite_file, delete_requisite_file, get_requisite_by_id
)

requisite_parser = reqparse.RequestParser()
requisite_parser.add_argument('title', type=str, required=True, location='form')
requisite_parser.add_argument('file', type=FileStorage, required=False, location='files')

file_parser = reqparse.RequestParser()
file_parser.add_argument('file', type=FileStorage, required=True, location='files')


@ref_ns.route('/requisites')
class RequisiteList(ApiResource):

    def get(self):
        """Список всех реквизитов"""
        items = get_all_requisites()
        return [i.to_dict() for i in items], HTTPStatus.OK

    @admin_required
    @ref_ns.expect(requisite_parser)
    def post(self):
        """Создание нового реквизита"""
        args = requisite_parser.parse_args()
        item = create_requisite(args['title'], args['file'])
        return item.to_dict(), HTTPStatus.CREATED


@ref_ns.route('/requisites/<int:id>')
class RequisiteResource(ApiResource):

    def get(self, id: int):
        """Получение реквизита по ID"""
        item = get_requisite_by_id(id)
        if not item:
            raise NotFoundError('Реквизит не найден')
        return item.to_dict(), HTTPStatus.OK

    @admin_required
    @ref_ns.expect(requisite_parser)
    def put(self, id: int):
        """Обновление названия реквизита"""
        item = get_requisite_by_id(id)
        if not item:
            raise NotFoundError('Реквизит не найден')
        args = requisite_parser.parse_args()
        update_requisite(item, args['title'])
        return item.to_dict(), HTTPStatus.OK

    @admin_required
    def delete(self, id: int):
        """Удаление реквизита вместе с файлом"""
        item = get_requisite_by_id(id)
        if not item:
            raise NotFoundError('Реквизит не найден')
        delete_requisite(item)
        return {'message': 'Реквизит удалён'}, HTTPStatus.OK


@ref_ns.route('/requisites/<int:id>/file')
class RequisiteFileResource(ApiResource):

    @admin_required
    @ref_ns.expect(file_parser)
    def post(self, id: int):
        """Загрузка или замена файла реквизита"""
        item = get_requisite_by_id(id)
        if not item:
            raise NotFoundError('Реквизит не найден')
        args = file_parser.parse_args()
        path = replace_requisite_file(item, args['file'])

        return {'message': 'Файл обновлён', 'file_path': path}, HTTPStatus.OK

    @admin_required
    def delete(self, id: int):
        """Удаление файла реквизита"""
        item = get_requisite_by_id(id)
        if not item:
            raise NotFoundError('Реквизит не найден')
        if not item.file:
            raise ValidationError('Файл отсутствует')
        delete_requisite_file(item)

        return {'message': 'Файл удалён'}, HTTPStatus.OK
