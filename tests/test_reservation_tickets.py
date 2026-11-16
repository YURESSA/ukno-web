from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4
from xml.etree import ElementTree

import pytest
from sqlalchemy import event

from backend.core import db
from backend.core.models.auth_models import RoleEnum
from backend.core.models.event_models import Reservation, ReservationAdmission
from backend.core.services.reservation_service.reservation_tickets import QR_PREFIX
from tests import test_security_regressions as security


app = security.app
ADMIN = '/api/admin/reservations'


@pytest.fixture()
def context(app):
    with app.app_context():
        admin = security.add_user('ticket-admin@example.com', RoleEnum.ADMIN)
        owner = security.add_user('ticket-owner@example.com')
        other = security.add_user('ticket-other@example.com')
        session = security.add_session(admin, capacity=10, cost=100)
        reservation = Reservation(
            session=session, user=owner, full_name='Анна Смирнова', email=owner.email,
            phone_number='+70000000001', participants_count=3, is_paid=True, is_cancelled=False,
        )
        db.session.add(reservation)
        db.session.commit()
        yield app.test_client(), reservation, {
            'admin': security.auth_header(admin), 'owner': security.auth_header(owner),
            'other': security.auth_header(other),
        }, admin.user_id


def user_url(reservation):
    return f'/api/user/reservations/{reservation.reservation_id}/ticket'


def payload(reservation, **overrides):
    return {'ticket': QR_PREFIX + reservation.ticket_token, 'session_id': reservation.session_id,
            'count': 1, 'request_id': str(uuid4()), **overrides}


def enter(client, headers, data):
    return client.post(ADMIN + '/tickets/check-in', headers=headers, json=data)


def test_owner_gets_stable_private_ticket_and_real_svg(context, monkeypatch):
    import qrcode
    client, reservation, headers, _ = context
    reservation.ticket_token = None  # A reservation created before the migration.
    db.session.commit()
    first = client.get(user_url(reservation), headers=headers['owner'])
    second = client.get(user_url(reservation), headers=headers['owner'])
    assert first.status_code == second.status_code == 200
    assert first.json == second.json
    ticket = first.json['ticket']
    assert ticket['status'] == 'valid'
    assert ticket['remaining_count'] == 3
    assert ticket['qr_payload'].startswith(QR_PREFIX)
    assert len(ticket['qr_payload']) == len(QR_PREFIX) + 43
    assert 'no-store' in first.headers['Cache-Control']
    encoded = []
    original_make = qrcode.make

    def capture(data, **kwargs):
        encoded.append(data)
        return original_make(data, **kwargs)

    monkeypatch.setattr(qrcode, 'make', capture)
    image = client.get(ticket['qr_svg_url'], headers=headers['owner'])
    assert image.status_code == 200 and image.mimetype == 'image/svg+xml'
    assert ElementTree.fromstring(image.data).tag.endswith('svg')
    assert encoded == [ticket['qr_payload']]
    assert 'no-store' in image.headers['Cache-Control']
    assert reservation.full_name.encode() not in image.data


@pytest.mark.parametrize('suffix', ['', '/qr'])
def test_only_owner_can_retrieve_qr(context, suffix):
    client, reservation, headers, _ = context
    url = user_url(reservation) + suffix
    assert client.get(url).status_code == 401
    assert client.get(url, headers=headers['other']).status_code == 404
    assert client.get(url, headers=headers['admin']).status_code == 404


def test_partial_entry_and_last_guest(context):
    client, reservation, headers, admin_id = context
    data = payload(reservation, count=2)
    checked = client.post(ADMIN + '/tickets/check', headers=headers['admin'], json=data)
    assert checked.status_code == 200
    assert checked.json['ticket']['remaining_count'] == 3
    assert ReservationAdmission.query.count() == 0
    first = enter(client, headers['admin'], data)
    assert first.status_code == 200, first.json
    assert first.json['ticket']['checked_in_count'] == 2
    assert first.json['ticket']['remaining_count'] == 1
    assert first.json['ticket']['status'] == 'partially_used'
    second = enter(client, headers['admin'], payload(reservation))
    assert second.status_code == 200
    assert second.json['ticket']['status'] == 'fully_used'
    assert second.json['ticket']['can_enter'] is False
    assert enter(client, headers['admin'], payload(reservation)).status_code == 409
    history = client.get(f'{ADMIN}/{reservation.reservation_id}/admissions', headers=headers['admin'])
    assert history.status_code == 200
    assert [row['participants_count'] for row in history.json['admissions']] == [2, 1]
    assert all(row['admin_user_id'] == admin_id for row in history.json['admissions'])
    assert all(row['admitted_at'].endswith('+00:00') for row in history.json['admissions'])
    assert 'qr_payload' not in history.json['ticket']


def test_retries_never_double_count_and_payload_changes_conflict(context):
    client, reservation, headers, _ = context
    data = payload(reservation, count=2)
    first = enter(client, headers['admin'], data)
    retry = enter(client, headers['admin'], data)
    assert retry.status_code == 200
    assert retry.json['replayed'] is True
    assert retry.json['admission'] == first.json['admission']
    assert retry.json['ticket']['checked_in_count'] == 2
    assert enter(client, headers['admin'], {**data, 'count': 1}).status_code == 409
    assert enter(client, headers['admin'], payload(reservation)).status_code == 200
    assert enter(client, headers['admin'], data).json['replayed'] is True
    assert ReservationAdmission.query.count() == 2


@pytest.mark.parametrize('count', [0, -1, True, 1.5, '2', None, 2147483648])
def test_invalid_count(context, count):
    client, reservation, headers, _ = context
    assert enter(client, headers['admin'], payload(reservation, count=count)).status_code == 400
    assert ReservationAdmission.query.count() == 0


@pytest.mark.parametrize('request_id', [None, '', 'not-a-uuid', 12])
def test_invalid_request_id(context, request_id):
    client, reservation, headers, _ = context
    assert enter(client, headers['admin'], payload(reservation, request_id=request_id)).status_code == 400


def test_wrong_session_and_over_capacity_cannot_enter(context):
    client, reservation, headers, _ = context
    wrong = payload(reservation, session_id=reservation.session_id + 99)
    check = client.post(ADMIN + '/tickets/check', headers=headers['admin'], json=wrong)
    assert check.json['ticket']['status'] == 'wrong_session'
    assert enter(client, headers['admin'], wrong).status_code == 409
    assert enter(client, headers['admin'], payload(reservation, count=4)).status_code == 409
    db.session.refresh(reservation)
    assert reservation.checked_in_count == 0
    assert ReservationAdmission.query.count() == 0


def test_large_count_cannot_overflow_after_partial_entry(context):
    client, reservation, headers, _ = context
    assert enter(client, headers['admin'], payload(reservation)).status_code == 200
    assert enter(client, headers['admin'], payload(reservation, count=2147483647)).status_code == 409
    db.session.refresh(reservation)
    assert reservation.checked_in_count == 1


@pytest.mark.parametrize('state', ['cancelled', 'unpaid', 'unavailable', 'unmoderated'])
def test_invalid_reservations_cannot_issue_or_enter(context, state):
    client, reservation, headers, _ = context
    if state == 'cancelled':
        reservation.is_cancelled = True
    elif state == 'unpaid':
        reservation.is_paid = False
    elif state == 'unavailable':
        reservation.session.event.is_active = False
    else:
        reservation.session.event.moderation_status = 'returned'
    db.session.commit()
    data = payload(reservation)
    assert client.get(user_url(reservation), headers=headers['owner']).status_code == 409
    assert client.get(user_url(reservation) + '/qr', headers=headers['owner']).status_code == 409
    check = client.post(ADMIN + '/tickets/check', headers=headers['admin'], json=data)
    assert check.status_code == 200
    assert check.json['ticket']['can_enter'] is False
    assert enter(client, headers['admin'], data).status_code == 409


def test_free_legacy_reservation_does_not_require_payment(context):
    client, reservation, headers, _ = context
    reservation.is_paid = False
    reservation.session.cost = 0
    db.session.commit()
    assert client.get(user_url(reservation), headers=headers['owner']).status_code == 200
    assert enter(client, headers['admin'], payload(reservation)).status_code == 200


@pytest.mark.parametrize('endpoint', ['check', 'check-in'])
def test_only_admin_can_scan_or_admit(context, endpoint):
    client, reservation, headers, _ = context
    url = ADMIN + '/tickets/' + endpoint
    assert client.post(url, json=payload(reservation)).status_code == 401
    assert client.post(url, json=payload(reservation), headers=headers['owner']).status_code == 403
    assert client.post(url, json=payload(reservation), headers=headers['other']).status_code == 403
    assert client.get(f'{ADMIN}/{reservation.reservation_id}/admissions', headers=headers['owner']).status_code == 403


def test_missing_or_malformed_ticket(context):
    client, reservation, headers, _ = context
    for value, code in [('bad', 400), ('A' * 43, 404), (None, 400)]:
        data = payload(reservation, ticket=value)
        assert enter(client, headers['admin'], data).status_code == code
        assert client.post(ADMIN + '/tickets/check', headers=headers['admin'], json=data).status_code == code


def test_audit_failure_rolls_back_increment(context):
    client, reservation, headers, _ = context

    def fail(*args):
        raise RuntimeError('Audit persistence failed')

    event.listen(ReservationAdmission, 'before_insert', fail)
    try:
        response = enter(client, headers['admin'], payload(reservation))
    finally:
        event.remove(ReservationAdmission, 'before_insert', fail)
    assert response.status_code == 500
    db.session.refresh(reservation)
    assert reservation.checked_in_count == 0
    assert ReservationAdmission.query.count() == 0


@pytest.mark.parametrize('same_request', [False, True])
def test_concurrent_scans_cannot_oversubscribe_or_double_count(context, app, same_request):
    _, reservation, headers, _ = context
    data = payload(reservation, count=2)
    second = data if same_request else {**data, 'request_id': str(uuid4())}
    barrier = Barrier(2)

    def call(body):
        with app.test_client() as client:
            barrier.wait(timeout=10)
            response = enter(client, headers['admin'], body)
            return response.status_code, response.get_json()

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(call, body) for body in (data, second)]
        responses = [future.result(timeout=20) for future in futures]
    assert sorted(code for code, _ in responses) == ([200, 200] if same_request else [200, 409])
    db.session.refresh(reservation)
    assert reservation.checked_in_count == 2
    assert ReservationAdmission.query.count() == 1


def test_tokens_not_exposed_in_existing_reservation_apis(context):
    client, reservation, headers, _ = context
    for url, auth in [('/api/user/reservations', headers['owner']), (ADMIN, headers['admin']),
                      (f'{ADMIN}/{reservation.reservation_id}', headers['admin'])]:
        response = client.get(url, headers=auth)
        assert response.status_code == 200
        assert reservation.ticket_token.encode() not in response.data


def test_very_large_count_cannot_overflow_database_counter(context):
    client, reservation, headers, _ = context
    assert enter(client, headers['admin'], payload(reservation)).status_code == 200
    response = enter(client, headers['admin'], payload(reservation, count=2147483647))
    assert response.status_code == 409
    db.session.refresh(reservation)
    assert reservation.checked_in_count == 1
    assert ReservationAdmission.query.count() == 1


def test_scan_and_partial_entry_stay_available_after_session_started(context):
    from datetime import datetime, timedelta

    client, reservation, headers, _ = context
    reservation.session.start_datetime = datetime.now() - timedelta(minutes=5)
    db.session.commit()
    response = client.post(ADMIN + '/tickets/check', headers=headers['admin'],
                           json={'ticket': QR_PREFIX + reservation.ticket_token})
    assert response.status_code == 200 and response.json['ticket']['can_enter']
    first = enter(client, headers['admin'], payload(reservation, count=2))
    assert first.status_code == 200 and first.json['ticket']['remaining_count'] == 1
    cancelled = client.delete(
        '/api/user/v2/reservations', headers=headers['owner'],
        json={'reservation_id': reservation.reservation_id},
    )
    assert cancelled.status_code == 409
    last = enter(client, headers['admin'], payload(reservation))
    assert last.status_code == 200 and last.json['ticket']['status'] == 'fully_used'


def test_check_resolves_session_from_ticket_without_manual_selection(context):
    client, reservation, headers, _ = context
    response = client.post(ADMIN + '/tickets/check', headers=headers['admin'],
                           json={'ticket': QR_PREFIX + reservation.ticket_token})
    assert response.status_code == 200
    ticket = response.json['ticket']
    assert ticket['session_id'] == reservation.session_id
    assert ticket['event_id'] == reservation.session.event_id
    assert ticket['can_enter'] is True
    assert ticket['checked_in_count'] == 0
    admission = enter(client, headers['admin'], payload(reservation, session_id=ticket['session_id'], count=2))
    assert admission.status_code == 200
    assert admission.json['ticket']['remaining_count'] == 1


@pytest.mark.parametrize('suffix', ['', '/qr'])
def test_admin_can_view_booking_ticket_but_other_roles_cannot(context, suffix):
    client, reservation, headers, _ = context
    path = f'{ADMIN}/{reservation.reservation_id}/ticket{suffix}'
    assert client.get(path).status_code == 401
    assert client.get(path, headers=headers['owner']).status_code == 403
    assert client.get(path, headers=headers['other']).status_code == 403
    response = client.get(path, headers=headers['admin'])
    assert response.status_code == 200
    assert 'no-store' in response.headers['Cache-Control']
    if suffix:
        assert response.mimetype == 'image/svg+xml'
    else:
        assert response.json['ticket']['qr_svg_url'] == path + '/qr'
    assert client.get(f'{ADMIN}/99999/ticket{suffix}', headers=headers['admin']).status_code == 404
