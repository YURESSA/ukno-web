"""Optional real-PostgreSQL checks, enabled with SECURITY_TEST_DATABASE_URL."""
from uuid import uuid4

import pytest

from backend.core import db
from backend.core.models.auth_models import RoleEnum
from backend.core.models.event_models import Reservation, ReservationAdmission
from backend.core.services.reservation_service.reservation_tickets import QR_PREFIX, TicketConflict, admit_ticket
from tests import test_postgres_concurrency as concurrency
from tests import test_security_regressions as security


postgres_app = concurrency.postgres_app
pytestmark = concurrency.pytestmark


@pytest.mark.parametrize('same_request', [False, True])
def test_postgres_parallel_ticket_admissions(postgres_app, same_request):
    with postgres_app.app_context():
        suffix = uuid4().hex
        admin = security.add_user(f'ticket-admin-{suffix}@example.com', RoleEnum.ADMIN)
        owner = security.add_user(f'ticket-owner-{suffix}@example.com')
        session = security.add_session(admin, capacity=10, cost=0)
        reservation = Reservation(session=session, user=owner, full_name='Group', email=owner.email,
                                  phone_number='+70000000000', participants_count=3,
                                  is_paid=True, is_cancelled=False)
        db.session.add(reservation)
        db.session.commit()
        reservation_id, admin_id = reservation.reservation_id, admin.user_id
        token, session_id = QR_PREFIX + reservation.ticket_token, session.session_id
    request_id = str(uuid4())

    def run(key):
        try:
            return 200, admit_ticket(token, session_id, 2, key, admin_id)
        except TicketConflict as error:
            return 409, str(error)

    results = concurrency._run_together(postgres_app, [
        lambda: run(request_id), lambda: run(request_id if same_request else str(uuid4())),
    ])
    assert sorted(code for code, _ in results) == ([200, 200] if same_request else [200, 409])
    with postgres_app.app_context():
        assert db.session.get(Reservation, reservation_id).checked_in_count == 2
        assert ReservationAdmission.query.filter_by(reservation_id=reservation_id).count() == 1
