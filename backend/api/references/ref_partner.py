from http import HTTPStatus

from flask_restx import Resource, reqparse
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.references import ref_ns
from backend.core.services.ref_service.partner_service import (
    get_all_partners,
    create_partner,
    update_partner,
    delete_partner,
    upload_partner_photo, get_partner_by_id, delete_partner_photo
)

partner_parser = reqparse.RequestParser()
partner_parser.add_argument('name', type=str, required=True, location='form')
partner_parser.add_argument('link', type=str, required=False, location='form')
partner_parser.add_argument('photo', type=FileStorage, required=False, location='files')
partner_parser.add_argument('order_index', type=int, required=False, location='form')

photo_parser = reqparse.RequestParser()
photo_parser.add_argument('photo', type=FileStorage, required=True, location='files')


@ref_ns.route('/partners')
class PartnerList(Resource):

    def get(self):
        items = get_all_partners()
        return [i.to_dict() for i in items], HTTPStatus.OK

    @admin_required
    @ref_ns.expect(partner_parser)
    def post(self):
        args = partner_parser.parse_args()
        try:
            item = create_partner(
                name=args.get('name'),
                link=args.get('link'),
                photo=args.get('photo'),
                order_index=args.get('order_index')
            )
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST
        return item.to_dict(), HTTPStatus.CREATED


@ref_ns.route('/partners/<int:id>')
class PartnerResource(Resource):

    def get(self, id: int):
        item = get_partner_by_id(id)
        if not item:
            return {'message': 'Партнёр не найден'}, HTTPStatus.NOT_FOUND
        return item.to_dict(), HTTPStatus.OK

    @admin_required
    @ref_ns.expect(partner_parser)
    def put(self, id: int):
        item = get_partner_by_id(id)
        if not item:
            return {'message': 'Партнёр не найден'}, HTTPStatus.NOT_FOUND

        args = partner_parser.parse_args()
        try:
            item = update_partner(
                item,
                name=args.get('name'),
                link=args.get('link'),
                order_index=args.get('order_index')
            )
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST

        return item.to_dict(), HTTPStatus.OK

    @admin_required
    def delete(self, id: int):
        item = get_partner_by_id(id)
        if not item:
            return {'message': 'Партнёр не найден'}, HTTPStatus.NOT_FOUND

        delete_partner(item)
        return {'message': 'Партнёр удалён'}, HTTPStatus.OK


@ref_ns.route('/partners/<int:id>/photo')
class PartnerPhotoResource(Resource):

    @admin_required
    def delete(self, id: int):
        try:
            delete_partner_photo(id)
        except ValueError as e:
            return ({'message': str(e)}, HTTPStatus.NOT_FOUND
            if str(e) == "Партнёр не найден" else HTTPStatus.BAD_REQUEST)

        return {'message': 'Фото удалено'}, HTTPStatus.OK

    @admin_required
    @ref_ns.expect(photo_parser)
    def post(self, id: int):
        item = get_partner_by_id(id)
        if not item:
            return {'message': 'Партнёр не найден'}, HTTPStatus.NOT_FOUND

        args = photo_parser.parse_args()
        try:
            photo_path = upload_partner_photo(item, args.get('photo'))
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST

        return {'message': 'Фото загружено', 'photo_path': photo_path}, HTTPStatus.OK
