import importlib.util
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.exc import IntegrityError


def test_ticket_migration_preserves_existing_reservations_and_reverses(tmp_path):
    path = (Path(__file__).resolve().parents[1] / 'backend/migrations/versions/'
            'b4c6d8e0f2a1_reservation_tickets.py')
    spec = importlib.util.spec_from_file_location('ticket_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine(f'sqlite:///{tmp_path / "migration.db"}')
    with engine.begin() as connection:
        connection.exec_driver_sql('CREATE TABLE users (user_id INTEGER PRIMARY KEY)')
        connection.exec_driver_sql('CREATE TABLE reservations ('
                                   'reservation_id INTEGER PRIMARY KEY, participants_count INTEGER NOT NULL)')
        connection.exec_driver_sql('INSERT INTO reservations VALUES (1, 3)')
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()
        row = connection.execute(sa.text('SELECT * FROM reservations')).mappings().one()
        assert row['reservation_id'] == 1 and row['participants_count'] == 3
        assert row['ticket_token'] is None and row['checked_in_count'] == 0
        assert 'reservation_admissions' in sa.inspect(connection).get_table_names()
        with connection.begin_nested():
            with pytest.raises(IntegrityError):
                connection.exec_driver_sql('UPDATE reservations SET checked_in_count = 4')
        migration.downgrade()
        assert 'reservation_admissions' not in sa.inspect(connection).get_table_names()
        assert {col['name'] for col in sa.inspect(connection).get_columns('reservations')} == {
            'reservation_id', 'participants_count',
        }
        assert connection.execute(sa.text('SELECT participants_count FROM reservations')).scalar_one() == 3
    engine.dispose()
