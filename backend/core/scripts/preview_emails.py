"""Render all email templates with demo data; never connects to SMTP or the database."""
import argparse
import base64
import json
from datetime import datetime
from pathlib import Path

from backend.core.services.email_service.templates import TEMPLATE_NAMES, email_environment, render_email
from backend.core.services.reservation_service.reservation_tickets import QR_PREFIX, qr_png


SAMPLE_CONTEXT = {
    'display_name': 'Анна Смирнова',
    'reservation_id': 1042,
    'session_id': 28,
    'session_start': datetime(2026, 11, 28, 18, 30),
    'event_title': 'Город с высоты: прогулка по необычным местам',
    'place': 'Молодёжное бюро «5 этаж», ул. Мира, 12',
    'contact_email': 'events@example.com',
    'participants_count': 2,
    'has_refund': True,
    'amount': '1500.00',
    'currency': 'RUB',
    'reset_url': 'https://example.com/reset-password?token=demo-not-a-real-token',
    'ticket_image_src': None,
    'ticket_filename': 'ticket-1042.png',
}


def build_previews(output, names=TEMPLATE_NAMES, overrides=None):
    context = {**SAMPLE_CONTEXT, **(overrides or {})}
    if not context['ticket_image_src']:
        demo_png = qr_png(QR_PREFIX + 'A' * 43)
        context['ticket_image_src'] = 'data:image/png;base64,' + base64.b64encode(demo_png).decode('ascii')
    if isinstance(context['session_start'], str):
        context['session_start'] = datetime.fromisoformat(context['session_start'])
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    items = []
    for name in names:
        message = render_email(name, context)
        (output / f'{name}.htm').write_text(message['body_html'], encoding='utf-8')
        items.append({'name': name, 'subject': message['subject'], 'text': message['body']})
    index = email_environment().get_template('preview_index.htm').render(items=items)
    (output / 'index.htm').write_text(index, encoding='utf-8')
    return output / 'index.htm'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='.email-preview', help='Directory for generated preview files')
    parser.add_argument('--template', choices=TEMPLATE_NAMES, help='Render just one email')
    parser.add_argument('--data', type=Path, help='JSON file overriding the demo context')
    args = parser.parse_args()
    overrides = json.loads(args.data.read_text(encoding='utf-8')) if args.data else None
    names = (args.template,) if args.template else TEMPLATE_NAMES
    print(build_previews(args.output, names, overrides).resolve())


if __name__ == '__main__':
    main()
