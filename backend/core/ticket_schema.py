"""Idempotent bridge for deployments initialized with create_all, without Alembic state."""
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


def ensure_ticket_schema(engine):
    """Upgrade old reservation tables; never reset existing tokens or admission counts."""
    with engine.begin() as connection:
        if connection.dialect.name == 'postgresql':
            connection.execute(sa.text("SET LOCAL lock_timeout = '10s'"))
            connection.execute(sa.text('SELECT pg_advisory_xact_lock(510202611)'))
        inspector = sa.inspect(connection)
        if not inspector.has_table('reservations'):
            return
        columns = {column['name'] for column in inspector.get_columns('reservations')}
        unique = inspector.get_unique_constraints('reservations')
        checks = {item['name'] for item in inspector.get_check_constraints('reservations')}
        operations = Operations(MigrationContext.configure(connection))
        with operations.batch_alter_table('reservations') as batch:
            if 'ticket_token' not in columns:
                batch.add_column(sa.Column('ticket_token', sa.String(64), nullable=True))
            if 'checked_in_count' not in columns:
                batch.add_column(sa.Column('checked_in_count', sa.Integer(), nullable=False, server_default='0'))
            if not any(item['column_names'] == ['ticket_token'] for item in unique):
                batch.create_unique_constraint('uq_reservations_ticket_token', ['ticket_token'])
            if 'ck_reservation_admitted_capacity' not in checks:
                batch.create_check_constraint('ck_reservation_admitted_capacity',
                                              'checked_in_count >= 0 AND checked_in_count <= participants_count')


def verify_reservation_schema(engine):
    """Fail deployment checks for missing columns in reservation-related models."""
    from backend.core.models.event_models import Reservation, ReservationAdmission

    inspector = sa.inspect(engine)
    for model in (Reservation, ReservationAdmission):
        table = model.__table__
        if not inspector.has_table(table.name):
            raise RuntimeError(f'Missing table: {table.name}')
        present = {column['name'] for column in inspector.get_columns(table.name)}
        missing = {column.name for column in table.columns} - present
        if missing:
            raise RuntimeError(f'Missing columns in {table.name}: {", ".join(sorted(missing))}')
