import json
import importlib.util
from io import BytesIO
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tests import test_security_regressions
from tests.test_security_regressions import add_user, add_session, auth_header
from backend.core import db
from backend.core.models.auth_models import RoleEnum
from backend.core.models.event_models import Event, Reservation
from backend.core.services.event_services import event_photo_service


app = test_security_regressions.app


@pytest.fixture()
def context(app):
    with app.app_context():
        resident = add_user('resident@example.com', RoleEnum.RESIDENT)
        admin = add_user('admin@example.com', RoleEnum.ADMIN)
        stranger = add_user('other@example.com', RoleEnum.RESIDENT)
        visitor = add_user('visitor@example.com')
        session = add_session(resident, capacity=10)
        event = session.event
        yield app.test_client(), event, session, {
            'resident': auth_header(resident), 'admin': auth_header(admin),
            'stranger': auth_header(stranger), 'visitor': auth_header(visitor),
        }


def visible_ids(client):
    response = client.get('/api/user/excursions')
    assert response.status_code == 200
    return [event['excursion_id'] for event in response.json['excursions']]


def test_resident_creation_requires_approval_even_with_forged_status(context):
    client, event, session, headers = context
    data = {
        'title': 'New event', 'description': 'Description', 'duration': 60,
        'category': event.category.category_name, 'format_type': event.format_type.format_type_name,
        'age_category': event.age_category.age_category_name, 'place': 'Place',
        'is_active': True, 'moderation_status': 'approved',
        'sessions': [{'start_datetime': (datetime.now() + timedelta(days=2)).isoformat(),
                      'max_participants': 10, 'cost': 0}],
    }
    for role, status in [('resident', 'pending'), ('admin', 'approved')]:
        response = client.post('/api/' + role + '/excursions',
                               data={'data': json.dumps(data)}, headers=headers[role])
        assert response.status_code == 201, response.json
        created = db.session.get(Event, response.json['event_id'])
        assert created.moderation_status == status
        assert (created.event_id in visible_ids(client)) == (role == 'admin')


def test_return_correct_resubmit_and_publish_with_admin_changes(context):
    client, event, session, headers = context
    event.moderation_status = 'pending'
    db.session.commit()
    url = f'/api/admin/excursions/{event.event_id}'
    resident_url = f'/api/resident/excursions/{event.event_id}'
    assert event.event_id not in visible_ids(client)
    queue = client.get('/api/admin/excursions?moderation_status=pending', headers=headers['admin'])
    assert [e['excursion_id'] for e in queue.json['excursions']] == [event.event_id]
    assert client.post(url + '/return', json={'comment': '  '}, headers=headers['admin']).status_code == 400
    returned = client.post(url + '/return', json={'comment': ' Исправьте описание '}, headers=headers['admin'])
    assert returned.status_code == 200
    own = client.get(resident_url, headers=headers['resident']).json['excursion']
    assert own['moderation_status'] == 'returned'
    assert own['moderation_comment'] == 'Исправьте описание'
    assert client.post(url + '/approve', json={}, headers=headers['admin']).status_code == 409
    assert client.post(resident_url + '/submit', headers=headers['stranger']).status_code == 403
    updated = client.patch(resident_url, json={'description': 'Corrected', 'moderation_status': 'approved'},
                           headers=headers['resident'])
    assert updated.status_code == 200, updated.json
    assert updated.json['excursion']['moderation_status'] == 'returned'
    assert client.post(resident_url + '/submit', headers=headers['resident']).status_code == 200
    assert event.event_id not in visible_ids(client)
    approved = client.post(url + '/approve', json={'title': 'Admin corrected'}, headers=headers['admin'])
    assert approved.status_code == 200, approved.json
    assert approved.json['excursion']['moderation_comment'] is None
    assert approved.json['excursion']['title'] == 'Admin corrected'
    assert event.event_id in visible_ids(client)
    assert client.post(url + '/approve', json={}, headers=headers['admin']).status_code == 409


@pytest.mark.parametrize('role', ['resident', 'stranger', 'visitor'])
@pytest.mark.parametrize('action', ['approve', 'return'])
def test_only_admin_can_moderate(context, role, action):
    client, event, session, headers = context
    url = f'/api/admin/excursions/{event.event_id}/{action}'
    assert client.post(url, json={'comment': 'Return'}, headers=headers[role]).status_code == 403
    assert client.post(url, json={'comment': 'Return'}).status_code == 401


@pytest.mark.parametrize('status,active', [('pending', True), ('returned', True), ('approved', False)])
def test_hidden_events_cannot_be_listed_or_booked(context, status, active):
    client, event, session, headers = context
    event.moderation_status = status
    event.is_active = active
    db.session.commit()
    assert event.event_id not in visible_ids(client)
    assert client.get(f'/api/user/excursions_detail/{event.event_id}').status_code == 404
    response = client.post('/api/user/v2/reservations', headers=headers['visitor'], json={
        'session_id': session.session_id, 'full_name': 'Visitor',
        'phone_number': '+70000000000', 'email': 'visitor@example.com', 'participants_count': 1,
    })
    assert response.status_code == 400, response.json
    assert Reservation.query.count() == 0


@pytest.mark.parametrize('kind', ['event', 'session'])
def test_resident_changes_require_new_approval(context, kind):
    client, event, session, headers = context
    url = f'/api/resident/excursions/{event.event_id}'
    if kind == 'session':
        url += f'/sessions/{session.session_id}'
        data = {'cost': 200}
    else:
        data = {'title': 'Resident edited', 'is_active': True}
    response = client.patch(url, json=data, headers=headers['resident'])
    assert response.status_code == 200, response.json
    db.session.refresh(event)
    assert event.moderation_status == 'pending'
    assert event.event_id not in visible_ids(client)


def test_admin_edits_do_not_publish_until_approval(context):
    client, event, session, headers = context
    event.moderation_status = 'pending'
    db.session.commit()
    url = f'/api/admin/excursions/{event.event_id}'
    response = client.patch(url, json={'description': 'Admin edit'}, headers=headers['admin'])
    assert response.status_code == 200
    assert event.event_id not in visible_ids(client)
    response = client.post(url + '/approve', headers=headers['admin'])
    assert response.status_code == 200, response.json
    assert event.event_id in visible_ids(client)


def test_migration_preserves_existing_events_and_can_be_reversed():
    import sqlalchemy as sa
    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    path = (Path(__file__).parents[1] / 'backend/migrations/versions'
            / 'a3b5c7d9e1f2_add_event_moderation.py')
    spec = importlib.util.spec_from_file_location('moderation_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine('sqlite://')
    with engine.begin() as connection:
        connection.execute(sa.text('CREATE TABLE events (event_id INTEGER PRIMARY KEY, is_active BOOLEAN NOT NULL)'))
        connection.execute(sa.text('INSERT INTO events VALUES (1, 1), (2, 0)'))
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            rows = connection.execute(sa.text(
                'SELECT event_id, is_active, moderation_status, moderation_comment FROM events ORDER BY event_id'
            )).all()
            assert rows == [(1, 1, 'approved', None), (2, 0, 'approved', None)]
            migration.downgrade()
            columns = [column['name'] for column in sa.inspect(connection).get_columns('events')]
            assert columns == ['event_id', 'is_active']
    engine.dispose()


def test_photo_upload_checks_owner_and_requires_new_approval(context, monkeypatch):
    client, event, session, headers = context
    monkeypatch.setattr(event_photo_service, 'process_photos', lambda files: [
        {'photo_url': 'excursion_photos/test.png', 'order_index': 0}
    ])
    url = f'/api/resident/excursions/{event.event_id}/photos'
    response = client.post(url, headers=headers['stranger'],
                           data={'photo': (BytesIO(b'image'), 'test.png')})
    assert response.status_code == 403
    db.session.refresh(event)
    assert event.moderation_status == 'approved'
    response = client.post(url, headers=headers['resident'],
                           data={'photo': (BytesIO(b'image'), 'test.png')})
    assert response.status_code == 200, response.json
    db.session.refresh(event)
    assert event.moderation_status == 'pending'
    assert event.event_id not in visible_ids(client)
