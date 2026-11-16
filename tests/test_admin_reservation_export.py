from datetime import datetime
from decimal import Decimal
from io import BytesIO

import pytest
from openpyxl import load_workbook

from backend.core import db
from backend.core.models.auth_models import RoleEnum
from backend.core.models.event_models import EventSession, Payment, Reservation
from tests import test_security_regressions as security


app = security.app
BASE = '/api/admin/reservations'


@pytest.fixture()
def context(app):
    with app.app_context():
        admin = security.add_user('admin@example.com', RoleEnum.ADMIN)
        user = security.add_user('user@example.com')
        first = security.add_session(admin, capacity=20, cost=Decimal('123.45'))
        first.start_datetime = datetime(2026, 11, 16, 0)
        first.event.title = '=HYPERLINK("https://example.com")'
        second = EventSession(event=first.event, start_datetime=datetime(2026, 11, 17),
                              max_participants=20, cost=Decimal('10.00'))
        db.session.add(second)
        third = security.add_session(admin, capacity=20, cost=0)
        third.start_datetime = datetime(2026, 11, 16, 23, 59, 59, 999999)
        db.session.flush()
        reservations = []
        for index, (session, paid, cancelled) in enumerate([
            (first, True, False), (second, False, True), (third, False, False),
        ], 1):
            reservation = Reservation(
                session=session, user=user, full_name='=1+1' if index == 1 else f'Гость {index}',
                phone_number='+70000000001', email=f'guest{index}@example.com', participants_count=2,
                is_paid=paid, is_cancelled=cancelled, booked_at=datetime(2026, 11, index, 23, 59, 59),
            )
            db.session.add(reservation)
            reservations.append(reservation)
        db.session.flush()
        db.session.add_all([
            Payment(payment_id='paid', reservation=reservations[0], session=first, participants_count=2,
                    email=user.email, amount=Decimal('246.90'), status='succeeded'),
            Payment(payment_id='cancelled', reservation=reservations[1], session=second, participants_count=2,
                    email=user.email, amount=20, status='canceled'),
        ])
        db.session.commit()
        yield app.test_client(), security.auth_header(admin), security.auth_header(user), reservations


def ids(response):
    assert response.status_code == 200, response.get_json()
    return [row['reservation_id'] for row in response.get_json()['reservations']]


def test_old_request_keeps_complete_response(context):
    client, headers, _, reservations = context
    response = client.get(BASE, headers=headers)
    assert response.get_json() == {'reservations': [row.to_dict() for row in reservations]}


@pytest.mark.parametrize('filters, indices', [
    ({'date_from': '2026-11-16', 'date_to': '2026-11-16'}, [0, 2]),
    ({'booked_from': '2026-11-02', 'booked_to': '2026-11-02'}, [1]),
    ({'is_paid': 'true', 'is_cancelled': 'false'}, [0]),
    ({'is_paid': '0', 'is_cancelled': '1'}, [1]),
    ({'payment_status': 'unpaid'}, [2]),
    ({'payment_status': 'succeeded'}, [0]),
    ({'payment_status': 'canceled'}, [1]),
    ({'q': 'GUEST2@EXAMPLE.COM'}, [1]),
    ({'q': 'Гость 3'}, [2]),
    ({'q': '+70000000001'}, [0, 1, 2]),
    ({'q': '%'}, []),
    ({'q': '_'}, []),
    ({'is_paid': 'true', 'payment_status': 'unpaid'}, []),
])
def test_filters_and_export_match(context, filters, indices):
    client, headers, _, reservations = context
    expected = [reservations[index].reservation_id for index in indices]
    assert ids(client.get(BASE, headers=headers, query_string=filters)) == expected
    response = client.get(BASE, headers=headers, query_string={**filters, 'format': 'xlsx'})
    assert response.status_code == 200
    workbook = load_workbook(BytesIO(response.data))
    sheet = workbook.active
    assert [row[0] for row in sheet.iter_rows(min_row=2, values_only=True)] == expected


def test_id_filters_combine(context):
    client, headers, _, rows = context
    filters = {'event_id': rows[0].session.event_id, 'user_id': rows[0].user_id}
    assert ids(client.get(BASE, headers=headers, query_string=filters)) == [row.reservation_id for row in rows[:2]]
    filters['session_id'] = rows[0].session_id
    assert ids(client.get(BASE, headers=headers, query_string=filters)) == [rows[0].reservation_id]
    filters['event_id'] = rows[2].session.event_id
    assert ids(client.get(BASE, headers=headers, query_string=filters)) == []


@pytest.mark.parametrize('filters', [
    {'event_id': 'abc'}, {'session_id': '-1'}, {'user_id': '0'}, {'event_id': '1.2'},
    {'event_id': '999999999999999'}, {'is_paid': 'yes'}, {'is_cancelled': ''},
    {'date_from': 'invalid'}, {'date_to': '2026-02-30'}, {'date_to': '9999-12-31'},
    {'date_from': '20261116'}, {'date_from': '2026-11-17', 'date_to': '2026-11-16'},
    {'booked_from': '2026-11-17', 'booked_to': '2026-11-16'},
    {'payment_status': 'unknown'}, {'format': 'csv'}, {'q': 'x' * 256},
])
def test_invalid_filters_return_400(context, filters):
    client, headers, _, _ = context
    response = client.get(BASE, headers=headers, query_string=filters)
    assert response.status_code == 400
    assert response.get_json()['message']


def test_excel_types_format_and_formula_safety(context):
    client, headers, _, rows = context
    response = client.get(BASE + '/export', headers=headers, query_string={'is_paid': 'true'})
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'attachment' in response.headers['Content-Disposition']
    sheet = load_workbook(BytesIO(response.data)).active
    assert sheet.max_row == 2
    assert sheet['A2'].value == rows[0].reservation_id
    assert sheet['C2'].data_type == sheet['H2'].data_type == sheet['I2'].data_type == 's'
    assert sheet['H2'].value == '=1+1'
    assert sheet['I2'].value == '+70000000001'
    assert sheet['E2'].value == rows[0].session.start_datetime
    assert sheet['L2'].value == rows[0].booked_at
    assert sheet['Q2'].value == 246.9
    assert sheet.freeze_panes == 'A2'
    assert sheet.auto_filter.ref == 'A1:Q2'


@pytest.mark.parametrize('url', [BASE, BASE + '?format=xlsx', BASE + '/export'])
def test_list_and_exports_require_admin(context, url):
    client, _, user_headers, _ = context
    assert client.get(url).status_code == 401
    assert client.get(url, headers=user_headers).status_code == 403


def test_export_alias_rejects_invalid_filter(context):
    client, headers, _, _ = context
    assert client.get(BASE + '/export?date_from=invalid', headers=headers).status_code == 400


def test_oversized_id_is_validation_error(context):
    client, headers, _, _ = context
    assert client.get(BASE, headers=headers, query_string={'event_id': '9' * 5000}).status_code == 400
