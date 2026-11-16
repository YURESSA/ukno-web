import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from backend.app import init_database
from backend.core import db
from backend.core.models.auth_models import RoleEnum
from backend.core.models.event_models import Reservation
from backend.core.scripts.check_reservation_health import check_reservation_health
from backend.core.ticket_schema import ensure_ticket_schema, verify_reservation_schema
from tests import test_security_regressions as security


app = security.app


def reservation_fixture():
    admin = security.add_user('startup-admin@example.com', RoleEnum.ADMIN)
    session = security.add_session(admin, capacity=10, cost=0)
    reservation = Reservation(session=session, user=admin, full_name='Legacy booking',
                              email=admin.email, phone_number='+70000000000', participants_count=3,
                              is_paid=True, is_cancelled=False)
    db.session.add(reservation)
    db.session.commit()
    return reservation.reservation_id


@pytest.mark.parametrize('keep_token', [False, True])
def test_init_db_repairs_partially_deployed_ticket_schema(app, keep_token):
    with app.app_context():
        reservation_id = reservation_fixture()
        original_token = db.session.get(Reservation, reservation_id).ticket_token
        db.session.remove()
        # Exact deployment failure: create_all already created the admission table,
        # while reservations still has the old schema, possibly with only one new column.
        with db.engine.begin() as connection:
            operations = Operations(MigrationContext.configure(connection))
            with operations.batch_alter_table('reservations') as batch:
                batch.drop_constraint('ck_reservation_admitted_capacity', type_='check')
                batch.drop_column('checked_in_count')
                if not keep_token:
                    batch.drop_constraint('uq_reservations_ticket_token', type_='unique')
                    batch.drop_column('ticket_token')
        with pytest.raises(RuntimeError, match='Missing columns'):
            verify_reservation_schema(db.engine)
        init_database()
        verify_reservation_schema(db.engine)
        restored = db.session.get(Reservation, reservation_id)
        assert restored.full_name == 'Legacy booking'
        assert restored.participants_count == 3 and restored.checked_in_count == 0
        assert restored.ticket_token == (original_token if keep_token else None)
        assert sa.inspect(db.engine).has_table('reservation_admissions')
        check_reservation_health(app)


def test_repeated_init_does_not_reset_live_tickets_or_counts(app):
    with app.app_context():
        reservation_id = reservation_fixture()
        reservation = db.session.get(Reservation, reservation_id)
        reservation.checked_in_count = 2
        original_token = reservation.ticket_token
        db.session.commit()
        for _ in range(2):
            init_database()
        db.session.refresh(reservation)
        assert reservation.checked_in_count == 2
        assert reservation.ticket_token == original_token
        assert reservation.participants_count == 3


def test_schema_upgrade_can_be_called_before_first_database_initialization(tmp_path):
    engine = sa.create_engine(f'sqlite:///{tmp_path / "empty.db"}')
    ensure_ticket_schema(engine)
    assert not sa.inspect(engine).has_table('reservations')
    engine.dispose()
