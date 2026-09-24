import re
from html import escape

from backend.core.config import Config
from backend.core.utilits.token_utils import generate_reset_token
from backend.core.utilits.email_utils import send_email
from backend.core.utilits.file_utils import create_ical_from_reservation


def _email_layout(subject, preheader, eyebrow, heading, intro_html, content_html,
                  accent="#ff6c36", footer_html=None):
    """Render an email-client friendly branded wrapper around trusted HTML blocks."""
    footer = footer_html or (
        'Это автоматическое письмо от Молодёжного бюро «5 этаж». '
        'Пожалуйста, не пересылайте письма со ссылками для доступа другим людям.'
    )
    return f"""
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{escape(str(subject))}</title>
      </head>
      <body style="margin:0;padding:0;background:#f3f0eb;color:#201f1d;font-family:Arial,Helvetica,sans-serif;">
        <div style="display:none;max-height:0;overflow:hidden;opacity:0;">{escape(str(preheader))}</div>
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#f3f0eb;">
          <tr>
            <td align="center" style="padding:32px 12px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:640px;background:#ffffff;border-radius:24px;overflow:hidden;box-shadow:0 12px 32px rgba(43,37,30,.08);">
                <tr>
                  <td style="padding:34px 40px;background:{accent};color:#ffffff;">
                    <div style="font-size:13px;line-height:18px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;opacity:.9;">{escape(str(eyebrow))}</div>
                    <div style="margin-top:14px;font-size:30px;line-height:36px;font-weight:800;">{escape(str(heading))}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:34px 40px 12px;font-size:16px;line-height:25px;">{intro_html}</td>
                </tr>
                <tr>
                  <td style="padding:10px 40px 38px;">{content_html}</td>
                </tr>
              </table>
              <div style="max-width:560px;padding:18px 20px 0;color:#8a847d;font-size:12px;line-height:18px;text-align:center;">{footer}</div>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """


def _detail_row(label, value, border=True):
    border_style = "border-bottom:1px solid #ebe7e1;" if border else ""
    return (
        f'<tr><td style="padding:17px 20px;{border_style}">'
        f'<div style="font-size:12px;line-height:18px;color:#817a72;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:.7px;">{escape(str(label))}</div>'
        f'<div style="margin-top:5px;font-size:16px;line-height:24px;font-weight:700;">{value}</div>'
        '</td></tr>'
    )


def _details_table(rows):
    rendered = ''.join(
        _detail_row(label, value, index < len(rows) - 1)
        for index, (label, value) in enumerate(rows)
    )
    return (
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" '
        f'style="border:1px solid #ebe7e1;border-radius:16px;">{rendered}</table>'
    )


def _notice(text, background="#fff3ed", color="#5d3b2d"):
    return (
        f'<div style="margin-top:18px;padding:18px 20px;background:{background};color:{color};'
        f'border-radius:16px;font-size:15px;line-height:23px;">{text}</div>'
    )


def send_reservation_confirmation_email(reservation, user):
    session = reservation.session
    event = session.event if session else None
    session_time = session.start_datetime.strftime(
        '%d.%m.%Y %H:%M') if session and session.start_datetime else 'неизвестно'
    session_date = session.start_datetime.strftime(
        '%d.%m.%Y') if session and session.start_datetime else 'уточняется'
    session_clock = session.start_datetime.strftime(
        '%H:%M') if session and session.start_datetime else 'уточняется'

    recipient = reservation.email or user.email
    display_name = reservation.full_name or recipient
    title = event.title if event else 'Событие'
    place = event.place if event and event.place else 'Место уточняется'
    contact = (event.contact_email if event and event.contact_email
               else 'Контакт будет указан организатором')
    booking_id = getattr(reservation, 'reservation_id', None)
    booking_label = f"№ {booking_id}" if booking_id is not None else 'подтверждено'
    participants = reservation.participants_count
    participant_word = (
        'участник' if participants % 10 == 1 and participants % 100 != 11
        else 'участника' if participants % 10 in (2, 3, 4) and participants % 100 not in (12, 13, 14)
        else 'участников'
    )
    subject = f"Вы записаны: {title} — {session_date}"

    body_text = (
        f"Здравствуйте, {display_name}!\n\n"
        "Готово — ваше бронирование подтверждено.\n\n"
        f"{title}\n"
        f"Дата и время: {session_time}\n"
        f"Место: {place}\n"
        f"Гостей: {participants}\n"
        f"Номер бронирования: {booking_label}\n\n"
        "Что дальше:\n"
        "1. Добавьте событие в календарь — файл reservation.ics приложен к письму.\n"
        "2. Перед поездкой ещё раз проверьте дату, время и адрес.\n"
        f"3. Если появятся вопросы, напишите организатору: {contact}\n\n"
        "До встречи в Молодёжном бюро «5 этаж»!"
    )

    safe_name = escape(str(display_name))
    safe_title = escape(str(title))
    safe_place = escape(str(place))
    safe_contact = escape(str(contact))
    safe_booking_label = escape(str(booking_label))
    contact_html = (
        f'<a href="mailto:{safe_contact}" style="color:#ff6c36;text-decoration:none;">{safe_contact}</a>'
        if '@' in str(contact) else safe_contact
    )

    body_html = _email_layout(
        subject=subject,
        preheader=f"Бронирование подтверждено — {title}, {session_date} в {session_clock}.",
        eyebrow="Молодёжное бюро · 5 этаж",
        heading="Вы записаны!",
        intro_html=(
            f'<div style="font-size:18px;line-height:27px;">Здравствуйте, <strong>{safe_name}</strong>!</div>'
            '<div style="margin-top:12px;color:#66615b;">Сохраняйте письмо — здесь собрана вся информация о вашем посещении.</div>'
            f'<div style="margin-top:26px;font-size:25px;line-height:32px;font-weight:800;">{safe_title}</div>'
        ),
        content_html=(
            _details_table([
                ("Дата и время", escape(f"{session_date} · {session_clock}")),
                ("Место проведения", safe_place),
                ("Гости", escape(f"{participants} {participant_word}")),
                ("Бронирование", safe_booking_label),
            ])
            + '<div style="margin-top:24px;font-size:18px;line-height:26px;font-weight:800;">Что дальше</div>'
            + '<ol style="margin:12px 0 0;padding-left:22px;color:#403d39;font-size:15px;line-height:24px;">'
              '<li style="padding:3px 0;">Добавьте событие в календарь — файл <strong>reservation.ics</strong> приложен к письму.</li>'
              '<li style="padding:3px 0;">Перед поездкой ещё раз проверьте дату, время и адрес.</li>'
              f'<li style="padding:3px 0;">Если появятся вопросы, напишите организатору: {contact_html}</li>'
              '</ol>'
            + _notice('До встречи в Молодёжном бюро «5 этаж»!', '#282622', '#ffffff')
        ),
        footer_html=f"Это автоматическое подтверждение бронирования. Контакт организатора: {contact_html}",
    )

    ics_bytes = create_ical_from_reservation(reservation)

    try:
        send_email(
            subject=subject,
            recipient=recipient,
            body=body_text,
            body_html=body_html,
            attachments=[("reservation.ics", ics_bytes, "text/calendar")]
        )
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def send_reservation_cancellation_email(user, reservation):
    event = reservation.session.event if reservation.session else None
    session = reservation.session

    date_str = session.start_datetime.strftime('%d.%m.%Y %H:%M') if session and session.start_datetime else 'неизвестно'
    session_id_str = session.session_id if session else 'неизвестен'
    event_title = event.title if event else 'Событие'
    booking_id = getattr(reservation, 'reservation_id', None)
    booking_label = f"№ {booking_id}" if booking_id is not None else f"сессия № {session_id_str}"
    has_refund = bool(reservation.payment and getattr(reservation.payment, 'status', '') == "succeeded")
    subject = f"Бронирование отменено: {event_title}"

    body_text = (
            f"Здравствуйте, {user.full_name}!\n\n"
            f"Ваше бронирование на событие «{event_title}» "
            f"(ID сессии: {session_id_str}), запланированную на {date_str}, было аннулировано администратором."
            + (
                "\nСредства за бронирование будут возвращены в ближайшее время."
                if has_refund
                else ""
            )
            + "\n\nПриносим извинения за возможные неудобства.\n"
              "Если у вас возникли вопросы, пожалуйста, свяжитесь с нами по указанным контактам."
    )

    safe_name = escape(str(user.full_name or user.email))
    safe_title = escape(str(event_title))
    refund_notice = _notice(
        '<strong>Возврат уже оформляется.</strong> Средства поступят на исходный способ оплаты в срок, установленный банком.',
        '#eef8f0', '#245b30'
    ) if has_refund else _notice(
        'Оплата по этому бронированию не была подтверждена, поэтому возврат не требуется.',
        '#f5f3ef', '#5f5a53'
    )
    body_html = _email_layout(
        subject=subject,
        preheader=f"Бронирование на {event_title} отменено.",
        eyebrow="Изменение бронирования",
        heading="Бронирование отменено",
        accent="#b4473b",
        intro_html=(
            f'<div style="font-size:18px;line-height:27px;">Здравствуйте, <strong>{safe_name}</strong>!</div>'
            '<div style="margin-top:12px;color:#66615b;">Администратор отменил ваше бронирование. Ниже — детали и информация о возврате.</div>'
        ),
        content_html=(
            _details_table([
                ("Событие", safe_title),
                ("Дата и время", escape(date_str)),
                ("Бронирование", escape(booking_label)),
            ])
            + refund_notice
            + '<div style="margin-top:22px;color:#66615b;font-size:14px;line-height:22px;">Приносим извинения за неудобства. Если у вас остались вопросы, ответьте организатору по указанным на сайте контактам.</div>'
        ),
    )

    try:
        send_email(subject=subject, recipient=user.email, body=body_text, body_html=body_html)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def send_event_deletion_email(resident, event, csv_data):
    subject = f"Событие удалено: {event.title}"
    recipient = resident.email

    body_text = (
        "Здравствуйте!\n\n"
        f"Событие «{event.title}» и все его сессии были удалены.\n"
        "В приложении — список всех отменённых бронирований.\n"
        "Спасибо за использование платформы!"
    )

    safe_title = escape(str(event.title))
    safe_name = escape(str(getattr(resident, 'full_name', '') or 'коллега'))
    body_html = _email_layout(
        subject=subject,
        preheader=f"Событие {event.title} и его сессии удалены.",
        eyebrow="Административное уведомление",
        heading="Событие удалено",
        accent="#3f3d39",
        intro_html=(
            f'<div style="font-size:18px;line-height:27px;">Здравствуйте, <strong>{safe_name}</strong>!</div>'
            f'<div style="margin-top:12px;color:#66615b;">Событие <strong>«{safe_title}»</strong> и все связанные с ним сессии удалены.</div>'
        ),
        content_html=(
            _notice('<strong>CSV-файл приложен к письму.</strong> В нём перечислены все отменённые бронирования.', '#fff3ed', '#5d3b2d')
            + '<div style="margin-top:20px;color:#66615b;font-size:14px;line-height:22px;">Сохраните файл для сверки с участниками и возвратами. Если список пуст, активных бронирований у события не было.</div>'
        ),
    )

    title_slug = re.sub(r'\W+', '_', event.title.lower())
    filename = f"отменённые_бронирования_{title_slug}.csv"

    try:
        send_email(
            subject=subject,
            recipient=recipient,
            body=body_text,
            body_html=body_html,
            attachments=[(filename, csv_data)]
        )
    except Exception as e:
        print(f"Ошибка при отправке письма об удалении события: {e}")


def send_session_cancellation_email(reservation, event_name, session):
    subject = f"Сессия отменена: {event_name}"
    recipient = reservation.email or (reservation.user.email if hasattr(reservation, 'user') else None)

    body_text = (
            f"Здравствуйте, {reservation.full_name}!\n\n"
            f"Сессия события «{event_name}» (ID {session.session_id}) на "
            f"{session.start_datetime.strftime('%d.%m.%Y %H:%M')} отменена.\n"
            "Ваше бронирование автоматически аннулировано."
            + (
                "\nСредства будут возвращены в ближайшее время."
                if reservation.payment and reservation.payment.status == "succeeded" else ""
            )
            + "\n\nПриносим извинения за возможные неудобства."
    )

    has_refund = bool(reservation.payment and reservation.payment.status == "succeeded")
    date_str = session.start_datetime.strftime('%d.%m.%Y %H:%M')
    refund_notice = _notice(
        '<strong>Возврат уже оформляется.</strong> Срок зачисления зависит от вашего банка.',
        '#eef8f0', '#245b30'
    ) if has_refund else _notice(
        'Подтверждённой оплаты нет — возврат средств не требуется.',
        '#f5f3ef', '#5f5a53'
    )
    body_html = _email_layout(
        subject=subject,
        preheader=f"Сессия события {event_name} на {date_str} отменена.",
        eyebrow="Изменение расписания",
        heading="Сессия отменена",
        accent="#b4473b",
        intro_html=(
            f'<div style="font-size:18px;line-height:27px;">Здравствуйте, <strong>{escape(str(reservation.full_name))}</strong>!</div>'
            '<div style="margin-top:12px;color:#66615b;">Организатор отменил эту дату. Ваше бронирование аннулировано автоматически.</div>'
        ),
        content_html=(
            _details_table([
                ("Событие", escape(str(event_name))),
                ("Дата и время", escape(date_str)),
                ("Сессия", escape(f"№ {session.session_id}")),
            ])
            + refund_notice
            + '<div style="margin-top:20px;color:#66615b;font-size:14px;line-height:22px;">Приносим извинения за изменение планов.</div>'
        ),
    )

    try:
        send_email(subject=subject, recipient=recipient, body=body_text, body_html=body_html)
    except Exception as e:
        print(f"Ошибка при отправке письма об отмене сессии: {e}")


def send_session_deletion_email(deleter_email, event_name, session_id, csv_data):
    subject = f"Сессия удалена: {event_name}"

    body_text = (
        f"Сессия события «{event_name}» (ID {session_id}) была удалена.\n\n"
        f"Во вложении — список всех отменённых по этой сессии бронирований.\n"
        f"Если возвраты были оформлены автоматически — дополнительных действий не требуется."
    )

    body_html = _email_layout(
        subject=subject,
        preheader=f"Сессия № {session_id} события {event_name} удалена.",
        eyebrow="Административное уведомление",
        heading="Сессия удалена",
        accent="#3f3d39",
        intro_html=(
            '<div style="font-size:18px;line-height:27px;">Здравствуйте!</div>'
            '<div style="margin-top:12px;color:#66615b;">Сессия удалена, а связанные бронирования отменены.</div>'
        ),
        content_html=(
            _details_table([
                ("Событие", escape(str(event_name))),
                ("Сессия", escape(f"№ {session_id}")),
            ])
            + _notice('<strong>Список бронирований — во вложении.</strong> CSV-файл поможет сверить участников и возвраты.', '#fff3ed', '#5d3b2d')
            + '<div style="margin-top:20px;color:#66615b;font-size:14px;line-height:22px;">Если возвраты были оформлены автоматически, дополнительных действий не требуется.</div>'
        ),
    )

    event_slug = re.sub(r'\W+', '_', event_name.lower())
    filename = f"отменённые_бронирования_{event_slug}_сессия_{session_id}.csv"

    try:
        send_email(
            subject=subject,
            recipient=deleter_email,
            body=body_text,
            body_html=body_html,
            attachments=[(filename, csv_data)]
        )
    except Exception as e:
        print(f"Ошибка при отправке письма об удалении сессии: {e}")


def send_reservation_refund_email(reservation):
    event_title = reservation.session.event.title
    date_str = reservation.session.start_datetime.strftime('%d.%m.%Y в %H:%M')
    amount = reservation.payment.amount if reservation.payment else 'не указана'
    currency = reservation.payment.currency if reservation.payment else 'RUB'
    subject = f"Возврат оформлен: {event_title}"

    recipient = reservation.email or (reservation.user.email if hasattr(reservation, 'user') else None)

    body_text = (
        f"Здравствуйте, {reservation.full_name}!\n\n"
        f"Ваше бронирование на событие "
        f"«{event_title}» "
        f"на {date_str} было успешно отменено.\n\n"
        f"Мы оформили возврат средств на тот же способ оплаты, который использовался при покупке.\n"
        f"Сумма возврата: {amount} {currency}\n\n"
        f"Срок зачисления зависит от банка, выпустившего карту.\n\n"
        f"Если у вас возникли вопросы, пожалуйста, свяжитесь с нашей службой поддержки.\n\n"
        f"С уважением,\nКоманда Молодёжного бюро «5 этаж»"
    )

    body_html = _email_layout(
        subject=subject,
        preheader=f"Возврат {amount} {currency} оформлен.",
        eyebrow="Статус оплаты",
        heading="Возврат оформлен",
        accent="#327a4b",
        intro_html=(
            f'<div style="font-size:18px;line-height:27px;">Здравствуйте, <strong>{escape(str(reservation.full_name))}</strong>!</div>'
            '<div style="margin-top:12px;color:#66615b;">Бронирование отменено. Мы отправили деньги на тот же способ оплаты, который использовался при покупке.</div>'
        ),
        content_html=(
            _details_table([
                ("Событие", escape(str(event_title))),
                ("Дата и время", escape(date_str)),
                ("Сумма возврата", escape(f"{amount} {currency}")),
            ])
            + _notice('<strong>Что важно:</strong> фактический срок зачисления зависит от банка, выпустившего карту.', '#eef8f0', '#245b30')
            + '<div style="margin-top:20px;color:#66615b;font-size:14px;line-height:22px;">Если деньги не поступят в срок, указанный вашим банком, обратитесь в поддержку и сообщите номер бронирования.</div>'
        ),
    )

    try:
        send_email(subject=subject, recipient=recipient, body=body_text, attachments=None, body_html=body_html)
    except Exception as e:
        print(f"Ошибка при отправке письма о возврате: {e}")


def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = f"{Config.FRONTEND_URL}reset-password?token={token}"

    subject = "Восстановление доступа к аккаунту"

    body_text = f"""Здравствуйте, {user.full_name}!

Мы получили запрос на смену пароля. Перейдите по ссылке ниже:
{reset_url}

Если вы не запрашивали смену пароля, ничего делать не нужно. Никому не пересылайте эту ссылку."""

    safe_url = escape(str(reset_url), quote=True)
    body_html = _email_layout(
        subject=subject,
        preheader="Используйте защищённую ссылку, чтобы задать новый пароль.",
        eyebrow="Безопасность аккаунта",
        heading="Сменить пароль",
        accent="#3f3d39",
        intro_html=(
            f'<div style="font-size:18px;line-height:27px;">Здравствуйте, <strong>{escape(str(user.full_name))}</strong>!</div>'
            '<div style="margin-top:12px;color:#66615b;">Мы получили запрос на смену пароля для вашего аккаунта.</div>'
        ),
        content_html=(
            '<div style="padding:8px 0 4px;text-align:center;">'
            f'<a href="{safe_url}" style="display:inline-block;padding:15px 26px;background:#ff6c36;color:#ffffff;text-decoration:none;border-radius:12px;font-size:16px;line-height:22px;font-weight:800;">Задать новый пароль</a>'
            '</div>'
            + _notice('<strong>Не запрашивали смену пароля?</strong> Просто проигнорируйте письмо. Ваш текущий пароль продолжит работать.', '#f5f3ef', '#5f5a53')
            + '<div style="margin-top:20px;color:#66615b;font-size:13px;line-height:21px;word-break:break-all;">Если кнопка не работает, скопируйте ссылку в браузер:<br>'
              f'<a href="{safe_url}" style="color:#ff6c36;">{safe_url}</a></div>'
        ),
        footer_html='Это письмо содержит персональную ссылку для доступа. Не пересылайте его другим людям.',
    )

    send_email(subject=subject, recipient=user.email, body=body_text, body_html=body_html)
