import json
import re

import pytest
from flask_jwt_extended import create_refresh_token
from jsonschema import Draft4Validator

from backend.api.error_docs import BUSINESS_ERRORS
from backend.core import db
from backend.core.services.reservation_service import reservation_crud
from tests import test_api_error_contracts as api_contracts
from tests.test_api_error_contracts import admin_headers
from tests.test_security_regressions import add_session, add_user, auth_header

app = api_contracts.app


@pytest.fixture()
def specification(app):
    response = app.test_client().get("/swagger.json")
    assert response.status_code == 200
    spec = response.get_json()
    assert "error" not in spec
    return spec


def assert_documented_error(response, specification, path, method, status):
    assert response.status_code == status
    operation = specification["paths"][path][method]
    assert operation["responses"][str(status)]["schema"] == {"$ref": "#/definitions/ApiErrorResponse"}
    validator = Draft4Validator(specification["definitions"]["ApiErrorResponse"])
    validator.validate(response.get_json())
    assert response.get_json()["message"].strip()


def test_every_operation_documents_errors_with_schema(app, specification):
    count = 0
    for path, methods in specification["paths"].items():
        for method, operation in methods.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            count += 1
            responses = operation["responses"]
            assert "500" in responses, (path, method)
            assert any(200 <= int(code) < 300 for code in responses if code.isdigit()), (path, method)
            for code, response in responses.items():
                if code.isdigit() and int(code) >= 400:
                    assert response["description"], (path, method, code)
                    assert response["schema"] == {"$ref": "#/definitions/ApiErrorResponse"}, (path, method, code)
            if operation["security"]:
                assert {"401", "422"} <= responses.keys(), (path, method)
    assert count > 100
    schema = specification["definitions"]["ApiErrorResponse"]
    Draft4Validator.check_schema(schema)
    assert schema["required"] == ["message"]
    assert schema["properties"]["message"]["minLength"] == 1
    Draft4Validator(schema).validate({"message": "Error", "data": ["legacy", 400]})


def test_business_error_catalog_matches_published_routes(specification):
    for path, methods in BUSINESS_ERRORS.items():
        for method, statuses in methods.items():
            operation = specification["paths"][path][method]
            assert {str(status) for status in statuses} <= operation["responses"].keys(), (path, method)
    public = specification["paths"]["/api/login"]["post"]
    assert public["security"] == []
    assert specification["paths"]["/api/references/partners"]["get"]["security"] == []
    secured = specification["paths"]["/api/references/partners"]["post"]
    assert secured["security"] == [{"Bearer": []}]
    assert "403" in secured["responses"]
    legacy = specification["paths"]["/api/references/cultural-space/{id}/photo"]["post"]["responses"]["404"]
    assert "404" in legacy["description"]


def test_observed_get_errors_are_in_swagger(app, specification):
    client = app.test_client()
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith("/api/") or "GET" not in rule.methods:
            continue
        path = re.sub(r"<(?:\w+:)?(\w+)>", r"{\1}", rule.rule)
        url = re.sub(r"<[^>]+>", "999", rule.rule)
        for headers in ({}, admin_headers()):
            response = client.get(url, headers=headers)
            if response.status_code >= 400:
                assert_documented_error(response, specification, path, "get", response.status_code)


def test_bad_json_shapes_are_documented_validation_errors(app, specification):
    client = app.test_client()
    for payload in ([], ["value"], "text", 123, None):
        response = client.post("/api/login", data=json.dumps(payload), content_type="application/json")
        assert_documented_error(response, specification, "/api/login", "post", 400)
        assert response.get_json() == {"message": "JSON должен содержать объект"}
        response = client.post("/api/admin/news", headers=admin_headers(), data={"data": json.dumps(payload)})
        assert_documented_error(response, specification, "/api/admin/news", "post", 400)
    response = client.post("/api/login", data="{", content_type="application/json")
    assert_documented_error(response, specification, "/api/login", "post", 400)
    response = client.post("/api/login", data="{}", content_type="text/plain")
    assert_documented_error(response, specification, "/api/login", "post", 415)
    refresh = create_refresh_token(identity="errors@example.com")
    response = client.get("/api/user/profile", headers={"Authorization": f"Bearer {refresh}"})
    assert_documented_error(response, specification, "/api/user/profile", "get", 422)


def test_missing_product_category_response_is_documented(app, specification):
    response = app.test_client().post("/api/admin/merch/products", headers=admin_headers(), data={
        "data": json.dumps({"category_id": 999, "name": "Product", "price": 100}),
    })
    assert_documented_error(response, specification, "/api/admin/merch/products", "post", 404)
    assert response.get_json() == {"message": "Category not found"}


def test_payment_failure_and_reservation_conflict_are_documented(app, specification, monkeypatch):
    def payment_unavailable(*args, **kwargs):
        raise TimeoutError("Payment provider is unavailable")

    monkeypatch.setattr(reservation_crud, "create_yookassa_payment", payment_unavailable)
    owner = add_user("swagger-owner@example.com")
    session = add_session(owner, capacity=1, cost=100)
    payload = {
        "session_id": session.session_id, "full_name": "Booker", "phone_number": "+70000000000",
        "email": owner.email, "participants_count": 1,
    }
    client = app.test_client()
    response = client.post("/api/user/v2/reservations", headers=auth_header(owner), json=payload)
    assert_documented_error(response, specification, "/api/user/v2/reservations", "post", 502)
    # A free reservation avoids any external calls and leaves an active capacity hold.
    session.cost = 0
    db.session.commit()
    monkeypatch.setattr(reservation_crud, "send_reservation_confirmation_email", lambda *args: None)
    assert client.post("/api/user/v2/reservations", headers=auth_header(owner), json=payload).status_code == 201
    response = client.post("/api/user/v2/reservations", headers=auth_header(owner), json=payload)
    assert_documented_error(response, specification, "/api/user/v2/reservations", "post", 409)


def test_webhook_provider_failure_is_documented(app, specification, monkeypatch):
    from backend.api.webhook import routes

    def unavailable(payment_id):
        raise TimeoutError("Provider timeout")

    monkeypatch.setattr(routes, "get_yookassa_payment", unavailable)
    response = app.test_client().post("/api/webhook/yookassa", json={
        "type": "notification", "event": "payment.succeeded", "object": {"id": "test-payment"},
    })
    assert_documented_error(response, specification, "/api/webhook/yookassa", "post", 503)
