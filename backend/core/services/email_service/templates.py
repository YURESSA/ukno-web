"""Render editable email templates independently of Flask request context."""
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


TEMPLATE_NAMES = (
    'reservation_confirmation', 'reservation_cancellation', 'reservation_refund',
    'session_cancellation', 'session_deletion', 'event_deletion', 'password_reset',
)
TEMPLATE_DIRECTORY = Path(__file__).resolve().parents[3] / 'templates' / 'emails'


@lru_cache(maxsize=1)
def email_environment():
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIRECTORY),
        autoescape=select_autoescape(('htm', 'html', 'xml')),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        auto_reload=True,
    )


def render_email(name, context):
    if name not in TEMPLATE_NAMES:
        raise ValueError(f'Unknown email template: {name}')
    environment = email_environment()
    # Metadata blocks are rendered as plain text, independently of the HTML body.
    text_template = environment.overlay(autoescape=False).get_template(f'{name}.htm')
    text_context = text_template.new_context(context)
    subject = ''.join(text_template.blocks['subject'](text_context))
    subject = ' '.join(subject.splitlines()).strip()
    return {
        'subject': subject,
        'body': ''.join(text_template.blocks['text'](text_context)).strip(),
        'body_html': environment.get_template(f'{name}.htm').render(**context, subject=subject),
    }
