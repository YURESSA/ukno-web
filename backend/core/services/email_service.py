from backend.core.services.utilits import send_email


def send_reservation_confirmation_email(reservation, user):
    session = reservation.session
    excursion = session.excursion
    session_time = session.start_datetime.strftime('%d.%m.%Y %H:%M')

    subject = "Подтверждение бронирования экскурсии"
    recipient = reservation.email or user.email
    body = (
        f"Здравствуйте, {reservation.full_name or user.email}!\n\n"
        f"Вы успешно записались на экскурсию:\n"
        f"Название: {excursion.title if excursion else 'Экскурсия'}\n"
        f"Дата и время: {session_time}\n"
        f"Количество участников: {reservation.participants_count}\n\n"
        f"Место проведения: {excursion.place if excursion else 'уточняется'}\n"
        f"Контактный email: {excursion.contact_email if excursion and excursion.contact_email else 'не указан'}\n\n"
        "Спасибо за бронирование!"
    )

    try:
        send_email(subject, recipient, body)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def send_reservation_cancellation_email(user, reservation):
    excursion = reservation.session.excursion if reservation.session else None
    session = reservation.session

    subject = "Бронирование аннулировано"
    body = (
            f"Здравствуйте, {user.full_name}!\n\n"
            f"Ваше бронирование на экскурсию «{excursion.title if excursion else 'Экскурсия'}» "
            f"(ID сессии: {session.session_id if session else 'неизвестен'}), запланированную на "
            f"{session.start_datetime.strftime('%d.%m.%Y %H:%M') if session else 'неизвестно'}, было аннулировано администратором.\n"
            + (
                "\nСредства за бронирование будут возвращены в ближайшее время."
                if reservation.payment and reservation.payment.status == "succeeded"
                else ""
            )
            + "\n\nПриносим извинения за возможные неудобства.\n"
              "Если у вас возникли вопросы, пожалуйста, свяжитесь с нами по указанным контактам."
    )

    try:
        send_email(subject=subject, recipient=user.email, body=body)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def send_excursion_deletion_email(resident, excursion, csv_data):
    subject = "Удалена экскурсия и отменены сессии"
    recipient = resident.email
    body = (
        "Здравствуйте!\n\n"
        f"Экскурсия «{excursion.title}» и все её сессии были удалены.\n"
        "В приложении — список всех отменённых бронирований.\n"
        "Спасибо за использование платформы!"
    )

    try:
        send_email(
            subject=subject,
            recipient=recipient,
            body=body,
            attachments=[("cancelled_reservations.csv", csv_data)]
        )
    except Exception as e:
        print(f"Ошибка при отправке письма об удалении экскурсии: {e}")


def send_session_cancellation_email(reservation, excursion_name, session):
    subject = "Отмена экскурсионной сессии"
    recipient = reservation.email or reservation.user.email
    body = (
            f"Здравствуйте, {reservation.full_name}!\n\n"
            f"Сессия экскурсии «{excursion_name}» (ID {session.session_id}) на {session.start_datetime.strftime('%d.%m.%Y %H:%M')} отменена.\n"
            "Ваше бронирование автоматически аннулировано."
            + (
                "\nСредства будут возвращены в ближайшее время." if reservation.payment and reservation.payment.status == "succeeded" else "")
            + "\n\nПриносим извинения за возможные неудобства."
    )
    try:
        send_email(subject=subject, recipient=recipient, body=body)
    except Exception as e:
        print(f"Ошибка при отправке письма об отмене сессии: {e}")


def send_session_deletion_email(deleter_email, excursion_name, session_id, csv_data):
    subject = "Список отменённых бронирований по сессии"
    body = (
        f"Сессия экскурсии «{excursion_name}» (ID {session_id}) была удалена.\n"
        "В приложении — список бронирований, которые были отменены."
    )
    try:
        send_email(
            subject=subject,
            recipient=deleter_email,
            body=body,
            attachments=[("cancelled_reservations.csv", csv_data)]
        )
    except Exception as e:
        print(f"Ошибка при отправке письма об удалении сессии: {e}")


def send_reservation_refund_email(reservation):
    subject = "Отмена бронирования и возврат средств"
    recipient = reservation.email or (reservation.user.email if hasattr(reservation, 'user') else None)

    body = (
        f"Здравствуйте, {reservation.full_name}!\n\n"
        f"Ваше бронирование №{reservation.reservation_id} на экскурсию "
        f"«{reservation.session.excursion.title}» на дату "
        f"{reservation.session.start_datetime.strftime('%d.%m.%Y %H:%M')} было успешно отменено.\n\n"
        f"Детали бронирования:\n"
        f"- Количество участников: {reservation.participants_count}\n"
        f"- ФИО: {reservation.full_name}\n"
        f"- Контактный телефон: {reservation.phone_number}\n"
        f"- Электронная почта: {reservation.email}\n\n"
        f"Сумма возврата: {reservation.payment.amount if reservation.payment else 'не указана'} "
        f"{reservation.payment.currency if reservation.payment else 'RUB'}\n"
        f"Средства будут возвращены на тот же способ оплаты, который вы использовали при покупке.\n\n"
        f"Если у вас возникли вопросы или вы считаете, что отмена произошла ошибочно, "
        f"пожалуйста, свяжитесь с нашей службой поддержки.\n\n"
        f"Спасибо, что выбираете нас!\n"
        f"С уважением,\n"
        f"Команда поддержки"
    )

    try:
        send_email(subject=subject, recipient=recipient, body=body)
    except Exception as e:
        print(f"Ошибка при отправке письма о возврате: {e}")
