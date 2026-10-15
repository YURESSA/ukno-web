import json
import re
from datetime import timedelta

import pytest
from flask_jwt_extended import create_access_token

from backend.api.errors import ApiResource
from backend.core import create_app, db
from backend.core.config import Config
from backend.core.models.auth_models import RoleEnum, User
from backend.core.models.news_models import News


@pytest.fixture(params=[True, False], ids=["testing", "production"])
def app(request, tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "SQLALCHEMY_DATABASE_URI", f"sqlite:///{tmp_path / 'api-errors.db'}")
    monkeypatch.setattr(Config, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(Config, "DEBUG", False)
    monkeypatch.setattr(Config, "JWT_SECRET_KEY", "test-error-contract-secret")
    application = create_app(testing=request.param)
    with application.app_context():
        db.create_all()
        user = User(full_name="Admin", email="errors@example.com", phone="+70000000000", role=RoleEnum.ADMIN)
        user.set_password("StrongPassword123!")
        db.session.add(user)
        db.session.flush()
        db.session.add(News(news_id=1, title="News", content="Content", author_id=user.user_id))
        db.session.commit()
        yield application
        db.session.remove()
        db.drop_all()


def assert_error(response, status=None):
    if status is not None:
        assert response.status_code == status
    assert response.status_code >= 400
    assert response.mimetype == "application/json"
    payload = response.get_json()
    assert isinstance(payload, dict)
    assert isinstance(payload.get("message"), str)
    assert payload["message"].strip()
    return payload


def admin_headers():
    return {"Authorization": "Bearer " + create_access_token(
        identity="errors@example.com", additional_claims={"role": "admin"},
    )}


def test_all_application_resources_share_error_handling(app):
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith("/api/"):
            resource = app.view_functions[rule.endpoint].view_class
            assert issubclass(resource, ApiResource), rule.rule


def test_jwt_errors_preserve_legacy_field_and_add_message(app):
    client = app.test_client()
    for url in ("/api/user/profile", "/api/admin/users", "/api/resident/profile"):
        payload = assert_error(client.get(url), 401)
        assert payload["message"] == payload["msg"]

    payload = assert_error(client.get("/api/user/profile", headers={"Authorization": "Bearer invalid"}), 422)
    assert payload["message"] == payload["msg"]
    expired = create_access_token(identity="errors@example.com", expires_delta=timedelta(seconds=-1))
    payload = assert_error(client.get("/api/user/profile", headers={"Authorization": f"Bearer {expired}"}), 401)
    assert payload["message"] == payload["msg"]


def test_error_messages_across_namespaces(app):
    client = app.test_client()
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith("/api/") or "GET" not in rule.methods:
            continue
        url = re.sub(r"<[^>]+>", "999", rule.rule)
        for headers in ({}, admin_headers()):
            response = client.get(url, headers=headers)
            if response.status_code >= 400:
                assert_error(response)

    for url in ("/api/login", "/api/webhook/yookassa"):
        assert_error(client.post(url, json={}), 400)
    assert_error(client.get("/api/user/merch/products/999"), 404)
    assert_error(client.get("/api/admin/news/999", headers=admin_headers()), 404)


def test_http_and_parser_errors_keep_status_and_details(app):
    client = app.test_client()
    assert_error(client.get("/_missing-route"), 404)
    assert_error(client.get("/api/_missing-route"), 404)
    response = client.delete("/api/login")
    assert_error(response, 405)
    assert "POST" in response.headers["Allow"]
    payload = assert_error(client.post("/api/references/team", headers=admin_headers(), data={}), 400)
    assert "full_name" in payload["errors"]
    response = client.put("/api/user/profile", headers=admin_headers(), data="{", content_type="application/json")
    assert_error(response, 400)
    app.config["MAX_CONTENT_LENGTH"] = 16
    payload = assert_error(client.post("/api/login", json={"email": "too-large@example.com"}), 413)
    assert payload["max_content_length"] == 16
    assert "max_form_memory_size" in payload


def test_news_errors_contain_the_actual_failure(app):
    client = app.test_client()
    headers = admin_headers()
    for data in ("{", json.dumps({"created_at": "invalid"})):
        response = client.put("/api/admin/news/1", headers=headers, data={"data": data})
        payload = assert_error(response, 400)
        if data != "{":
            assert payload == {"message": "Неверный формат даты"}
    payload = assert_error(client.delete("/api/admin/news/1/photos/999", headers=headers), 404)
    assert payload == {"message": "Фото не найдено"}


def test_missing_users_use_the_same_error_contract(app):
    client = app.test_client()
    response = client.delete("/api/admin/users/detail/missing@example.com", headers=admin_headers())
    assert assert_error(response, 404) == {"message": "Пользователь не найден"}
    token = create_access_token(identity="missing@example.com")
    response = client.delete("/api/user/profile", headers={"Authorization": f"Bearer {token}"})
    assert assert_error(response, 404) == {"message": "Пользователь не найден"}


def test_fallback_adds_messages_without_losing_fields_or_headers(app):
    @app.get("/_error/<int:status>")
    def code_only(status):
        return {"errors": {"field": "Invalid value"}}, status, {"Retry-After": "10"}

    @app.get("/_error-empty")
    def empty_error():
        return "", 500

    @app.get("/_error-legacy")
    def legacy_error():
        return {"msg": "Legacy error", "extra": True}, 400

    @app.get("/_error-exception")
    def unexpected_error():
        raise RuntimeError("Private server details")

    client = app.test_client()
    for status in (400, 401, 403, 404, 405, 409, 413, 422, 429, 500, 503):
        response = client.get(f"/_error/{status}")
        payload = assert_error(response, status)
        assert payload["errors"] == {"field": "Invalid value"}
        assert response.headers["Retry-After"] == "10"
    assert_error(client.get("/_error-empty"), 500)
    assert assert_error(client.get("/_error-exception"), 500) == {"message": "Internal server error"}
    assert client.get("/_error-legacy").get_json() == {"msg": "Legacy error", "message": "Legacy error", "extra": True}
