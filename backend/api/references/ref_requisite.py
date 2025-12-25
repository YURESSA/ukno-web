from flask_restx import Resource, reqparse
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core.models.ref_models import Requisite
from backend.core.services.ref_service.requisite_service import (
    get_all_requisites,
    create_requisite,
    update_requisite,
    delete_requisite,
    replace_requisite_file, delete_requisite_file
)

requisite_parser = reqparse.RequestParser()
requisite_parser.add_argument('title', type=str, required=True, location='form')
requisite_parser.add_argument('file', type=FileStorage, required=False, location='files')

file_parser = reqparse.RequestParser()
file_parser.add_argument('file', type=FileStorage, required=True, location='files')


@ref_ns.route('/requisites')
class RequisiteList(Resource):

    def get(self):
        """Список всех реквизитов"""
        items = get_all_requisites()
        return [i.to_dict() for i in items], 200

    @admin_required
    @ref_ns.expect(requisite_parser)
    def post(self):
        """Создание нового реквизита"""
        args = requisite_parser.parse_args()
        try:
            item = create_requisite(args['title'], args['file'])
        except ValueError as e:
            return {'message': str(e)}, 400
        return item.to_dict(), 201


@ref_ns.route('/requisites/<int:id>')
class RequisiteResource(Resource):

    def get(self, id: int):
        """Получение реквизита по ID"""
        item = Requisite.query.get(id)
        if not item:
            return {'message': 'Реквизит не найден'}, 404
        return item.to_dict(), 200

    @admin_required
    @ref_ns.expect(requisite_parser)
    def put(self, id: int):
        """Обновление названия реквизита"""
        item = Requisite.query.get(id)
        if not item:
            return {'message': 'Реквизит не найден'}, 404

        args = requisite_parser.parse_args()
        try:
            update_requisite(item, args['title'])
        except ValueError as e:
            return {'message': str(e)}, 400
        return item.to_dict(), 200

    @admin_required
    def delete(self, id: int):
        """Удаление реквизита вместе с файлом"""
        item = Requisite.query.get(id)
        if not item:
            return {'message': 'Реквизит не найден'}, 404

        delete_requisite(item)
        return {'message': 'Реквизит удалён'}, 200


@ref_ns.route('/requisites/<int:id>/file')
class RequisiteFileResource(Resource):

    @admin_required
    @ref_ns.expect(file_parser)
    def post(self, id: int):
        """Загрузка или замена файла реквизита"""
        item = Requisite.query.get(id)
        if not item:
            return {'message': 'Реквизит не найден'}, 404

        args = file_parser.parse_args()
        try:
            path = replace_requisite_file(item, args['file'])
        except ValueError as e:
            return {'message': str(e)}, 400

        return {'message': 'Файл обновлён', 'file_path': path}, 200

    @admin_required
    def delete(self, id: int):
        """Удаление файла реквизита"""
        item = Requisite.query.get(id)
        if not item:
            return {'message': 'Реквизит не найден'}, 404

        if not item.file:
            return {'message': 'Файл отсутствует'}, 400

        delete_requisite_file(item)

        return {'message': 'Файл удалён'}, 200
