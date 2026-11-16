from io import BytesIO

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font, PatternFill

from backend.core.errors import ValidationError
from backend.core.models.event_models import Reservation


HEADERS = (
    'ID брони', 'ID события', 'Событие', 'ID сеанса', 'Дата и время сеанса', 'Место',
    'ID пользователя', 'ФИО', 'Телефон', 'Email', 'Участников', 'Дата бронирования',
    'Оплачена', 'Отменена', 'Статус оплаты', 'Стоимость за участника, ₽', 'Сумма, ₽',
)


def export_reservations(query):
    """Generate XLSX; user-entered strings are always text, never formulas."""
    if query.count() > 1048575:
        raise ValidationError('Слишком много броней для Excel. Уточните фильтры')
    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet('Брони')
    sheet.freeze_panes = 'A2'
    for letter, width in zip('ABCDEFGHIJKLMNOPQ', (12, 12, 40, 12, 22, 35, 16, 32, 22, 35, 14, 22, 14, 14, 24, 26, 20)):
        sheet.column_dimensions[letter].width = width
    headers = []
    for title in HEADERS:
        cell = WriteOnlyCell(sheet, title)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='24527A')
        headers.append(cell)
    sheet.append(headers)
    count = 1
    for reservation in query.order_by(None).order_by(Reservation.reservation_id).yield_per(500):
        session = reservation.session
        event = session.event if session else None
        cost = session.cost if session else None
        values = (
            reservation.reservation_id, event.event_id if event else None, event.title if event else None,
            reservation.session_id, session.start_datetime if session else None, event.place if event else None,
            reservation.user_id, reservation.full_name, reservation.phone_number, reservation.email,
            reservation.participants_count, reservation.booked_at, 'Да' if reservation.is_paid else 'Нет',
            'Да' if reservation.is_cancelled else 'Нет',
            reservation.payment.status if reservation.payment else 'unpaid',
            cost, cost * reservation.participants_count if cost is not None else None,
        )
        row = []
        for index, value in enumerate(values):
            cell = WriteOnlyCell(sheet, value)
            if isinstance(value, str):
                cell.data_type = 's'
            if index in (4, 11):
                cell.number_format = 'dd.mm.yyyy hh:mm'
            if index in (15, 16):
                cell.number_format = '#,##0.00'
            row.append(cell)
        sheet.append(row)
        count += 1
    sheet.auto_filter.ref = f'A1:Q{count}'
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
