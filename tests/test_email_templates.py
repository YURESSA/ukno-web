from html import escape

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError, select_autoescape

from backend.core.scripts.preview_emails import SAMPLE_CONTEXT, build_previews
from backend.core.services.email_service import email_service, templates


@pytest.mark.parametrize('name', templates.TEMPLATE_NAMES)
def test_every_email_renders_and_escapes_data(name):
    untrusted = '<script>alert("x")</script><img src=x onerror="alert(1)">'
    context = {**SAMPLE_CONTEXT, **{
        key: untrusted for key in ('display_name', 'event_title', 'place', 'contact_email')
    }}
    context['reset_url'] = 'https://example.com/reset-password?token=a&next=" onmouseover="bad'
    rendered = templates.render_email(name, context)

    assert rendered['subject'].strip()
    assert rendered['body'].strip()
    assert '{{' not in rendered['body_html']
    assert '<script>' not in rendered['body_html']
    assert '<img src=x' not in rendered['body_html']
    assert ' onmouseover="bad' not in rendered['body_html']
    # Escaped strings are displayed as text; macros must not bypass escaping.
    assert '&lt;script&gt;' in rendered['body_html']
    assert 'lang="ru"' in rendered['body_html']
    assert 'role="presentation"' in rendered['body_html']


@pytest.mark.parametrize('name', ('reservation_cancellation', 'session_cancellation'))
@pytest.mark.parametrize('has_refund', (True, False))
def test_cancellation_selects_payment_notice(name, has_refund):
    rendered = templates.render_email(name, {**SAMPLE_CONTEXT, 'has_refund': has_refund})
    assert ('Возврат уже оформляется' in rendered['body_html']) == has_refund
    assert ('Подтверждённой оплаты' in rendered['body_html']) != has_refund
    assert ('Подтверждённой оплаты' in rendered['body']) != has_refund


@pytest.mark.parametrize('count, label', [
    (1, 'участник'), (2, 'участника'), (5, 'участников'),
    (11, 'участников'), (21, 'участник'), (22, 'участника'),
])
def test_participant_pluralization(count, label):
    rendered = templates.render_email('reservation_confirmation', {**SAMPLE_CONTEXT, 'participants_count': count})
    assert f'{count} {label}</div>' in rendered['body_html']


def test_optional_reservation_details_have_readable_fallbacks():
    context = {**SAMPLE_CONTEXT, **{key: None for key in (
        'session_start', 'event_title', 'place', 'contact_email', 'reservation_id',
    )}}
    rendered = templates.render_email('reservation_confirmation', context)
    assert 'Уточняется' in rendered['body_html']
    assert 'Место уточняется' in rendered['body_html']
    assert 'Контакт будет указан организатором' in rendered['body_html']
    assert 'None' not in rendered['body_html']


def test_subject_strips_line_breaks():
    rendered = templates.render_email('event_deletion', {**SAMPLE_CONTEXT, 'event_title': 'Test\r\nInjected header'})
    assert '\r' not in rendered['subject'] and '\n' not in rendered['subject']


def test_missing_template_data_fails_explicitly():
    with pytest.raises(UndefinedError, match='reset_url'):
        templates.render_email('password_reset', {'display_name': 'Test'})
    with pytest.raises(ValueError):
        templates.render_email('../password_reset', SAMPLE_CONTEXT)


def test_text_and_subject_can_be_changed_without_python(monkeypatch, tmp_path):
    for name, source in {
        'base.htm': '{% block content %}{% endblock %}',
        'password_reset.htm': (
            "{% extends 'base.htm' %}"
            '{% block subject %}Новая тема для {{ display_name }}{% endblock %}'
            '{% block text %}Текст: {{ reset_url }}{% endblock %}'
            '{% block content %}<p>{{ display_name }}</p>'
            '<a href="{{ reset_url }}">Войти</a>{% endblock %}'
        ),
    }.items():
        (tmp_path / name).write_text(source, encoding='utf-8')
    environment = Environment(loader=FileSystemLoader(tmp_path), undefined=StrictUndefined,
                              autoescape=select_autoescape(('htm',)))
    monkeypatch.setattr(templates, 'email_environment', lambda: environment)
    context = {**SAMPLE_CONTEXT, 'display_name': '<b>Анна</b>'}
    message = templates.render_email('password_reset', context)
    assert message['subject'] == 'Новая тема для <b>Анна</b>'
    assert message['body'] == f"Текст: {context['reset_url']}"
    assert escape(context['display_name']) in message['body_html']


@pytest.mark.parametrize('frontend_url', ('https://example.com', 'https://example.com/'))
def test_reset_url_is_encoded_and_has_one_path_separator(monkeypatch, frontend_url):
    sent = {}
    monkeypatch.setattr(email_service, 'send_email', lambda **kwargs: sent.update(kwargs))
    monkeypatch.setattr(email_service.Config, 'FRONTEND_URL', frontend_url)
    monkeypatch.setattr(email_service, 'generate_reset_token', lambda _: 'a&b=1')
    from types import SimpleNamespace
    email_service.send_reset_email(SimpleNamespace(email='test@example.com', full_name='Test'))
    assert 'https://example.com/reset-password?token=a%26b%3D1' in sent['body']


def test_preview_generates_all_files_without_sending(monkeypatch, tmp_path):
    def forbid_send(**kwargs):
        pytest.fail('Preview must never send an email')

    monkeypatch.setattr(email_service, 'send_email', forbid_send)
    index = build_previews(tmp_path, overrides={'display_name': 'Тест'})
    assert index.is_file()
    for name in templates.TEMPLATE_NAMES:
        assert (tmp_path / f'{name}.htm').is_file()
        assert not (tmp_path / f'{name}.txt').exists()
        assert not (tmp_path / f'{name}.subject.txt').exists()
        assert f'{name}.htm' in index.read_text(encoding='utf-8')


def test_each_email_has_one_source_file():
    assert not list(templates.TEMPLATE_DIRECTORY.glob('*.txt'))
    for name in templates.TEMPLATE_NAMES:
        source = (templates.TEMPLATE_DIRECTORY / f'{name}.htm').read_text(encoding='utf-8')
        assert '{% block subject %}' in source
        assert '{% block text %}' in source
