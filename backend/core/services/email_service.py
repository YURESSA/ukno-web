from backend.core.services.utilits import send_email


def send_reservation_confirmation_email(reservation, user):
    session = reservation.session
    excursion = session.excursion
    session_time = session.start_datetime.strftime('%d.%m.%Y %H:%M')

    subject = "Подтверждение бронирования экскурсии"
    recipient = reservation.email or user.email
    body = f"""Здравствуйте, {reservation.full_name or user.email}!

Вы успешно записались на экскурсию:
Название: {excursion.title if excursion else 'Экскурсия'}
Дата и время: {session_time}
Количество участников: {reservation.participants_count}

Место проведения: {excursion.place if excursion else 'уточняется'}
Контактный email: {excursion.contact_email if excursion and excursion.contact_email else 'не указан'}

Спасибо за бронирование!
"""

    try:
        send_email(subject, recipient, body)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
