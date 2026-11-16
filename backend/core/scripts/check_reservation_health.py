"""Read-only deployment smoke check for the real reservation schema and APIs."""
from datetime import timedelta

from flask_jwt_extended import create_access_token

from backend.core import create_app, db
from backend.core.models.auth_models import RoleEnum, User
from backend.core.services.reservation_service.reservation_queries import filtered_reservations
from backend.core.ticket_schema import verify_reservation_schema


def check_reservation_health(app):
    with app.app_context():
        verify_reservation_schema(db.engine)
        for reservation in filtered_reservations().limit(1):
            reservation.to_dict()
        admin = User.query.filter_by(role=RoleEnum.ADMIN).first()
        if not admin:
            print('Reservation schema and query OK; no admin account for authenticated smoke check')
            return
        token = create_access_token(identity=admin.email, additional_claims={'role': 'admin'},
                                    expires_delta=timedelta(minutes=1))
        client = app.test_client()
        for path in ('/api/admin/reservations', '/api/admin/reservations?format=xlsx', '/api/user/excursions'):
            response = client.get(path, headers={'Authorization': 'Bearer ' + token})
            if response.status_code != 200:
                raise RuntimeError(f'Deployment smoke check failed: {path} returned {response.status_code}')
            print(f'OK {path}: 200')


if __name__ == '__main__':
    check_reservation_health(create_app())
