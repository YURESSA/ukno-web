from http import HTTPStatus

from flask_restx import reqparse
from werkzeug.datastructures import FileStorage

from backend.api.admin.decorators import admin_required
from backend.api.errors import ApiResource
from backend.api.references import ref_ns
from backend.core.errors import NotFoundError
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
class PartnerList(ApiResource):

    def get(self):
        items = get_all_partners()
        return [i.to_dict() for i in items], HTTPStatus.OK

    @admin_required
    @ref_ns.expect(partner_parser)
    def post(self):
        args = partner_parser.parse_args()
        item = create_partner(
            name=args.get('name'),
            link=args.get('link'),
            photo=args.get('photo'),
            order_index=args.get('order_index')
        )
        return item.to_dict(), HTTPStatus.CREATED


@ref_ns.route('/partners/<int:id>')
class PartnerResource(ApiResource):

    def get(self, id: int):
        item = get_partner_by_id(id)
        if not item:
            raise NotFoundError('Партнёр не найден')
        return item.to_dict(), HTTPStatus.OK

    @admin_required
    @ref_ns.expect(partner_parser)
    def put(self, id: int):
        item = get_partner_by_id(id)
        if not item:
            raise NotFoundError('Партнёр не найден')
        args = partner_parser.parse_args()
        item = update_partner(
            item,
            name=args.get('name'),
            link=args.get('link'),
            order_index=args.get('order_index')
        )

        return item.to_dict(), HTTPStatus.OK

    @admin_required
    def delete(self, id: int):
        item = get_partner_by_id(id)
        if not item:
            raise NotFoundError('Партнёр не найден')
        delete_partner(item)
        return {'message': 'Партнёр удалён'}, HTTPStatus.OK


@ref_ns.route('/partners/<int:id>/photo')
class PartnerPhotoResource(ApiResource):

    @admin_required
    def delete(self, id: int):
        delete_partner_photo(id)

        return {'message': 'Фото удалено'}, HTTPStatus.OK

    @admin_required
    @ref_ns.expect(photo_parser)
    def post(self, id: int):
        item = get_partner_by_id(id)
        if not item:
            raise NotFoundError('Партнёр не найден')
        args = photo_parser.parse_args()
        photo_path = upload_partner_photo(item, args.get('photo'))

        return {'message': 'Фото загружено', 'photo_path': photo_path}, HTTPStatus.OK
