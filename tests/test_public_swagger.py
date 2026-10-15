import re
from urllib.parse import urlsplit

import pytest

from backend.core import create_app
from backend.core.config import Config


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setattr(Config, "SQLALCHEMY_DATABASE_URI", "sqlite://")
    monkeypatch.setattr(Config, "PUBLIC_SWAGGER_ENABLED", True)
    return create_app(testing=True)


def test_swagger_page_and_assets_use_existing_api_proxy(app):
    client = app.test_client()
    for path in ("/api/docs", "/api/docs/"):
        response = client.get(path, base_url="https://5buro.ru")
        assert response.status_code == 200
        assert response.mimetype == "text/html"
        assert response.headers["Cache-Control"] == "no-store"
        html = response.get_data(as_text=True)
        assert 'url: "/api/docs/swagger.json"' in html
        assets = re.findall(r'(?:src|href)="([^"]+)"', html)
        assert any("swagger-ui-bundle.js" in asset for asset in assets)
        for asset in assets:
            assert asset.startswith("/api/docs/assets/"), asset
            asset_response = client.get(asset)
            assert asset_response.status_code == 200, asset
            assert asset_response.mimetype != "text/html", asset


def test_swagger_schema_uses_https_behind_nginx_without_changing_cached_schema(app):
    client = app.test_client()
    # The default schema may have been cached from an internal health/test request.
    original = client.get("/swagger.json", base_url="http://internal-backend:5000").get_json()
    response = client.get("/api/docs/swagger.json", headers={"Host": "5buro.ru", "X-Forwarded-Proto": "https"})
    assert response.status_code == 200
    schema = response.get_json()
    assert schema["host"] == "5buro.ru"
    assert schema["schemes"] == ["https"]
    assert schema["paths"]["/api/login"]["post"]["responses"]["400"]["schema"] == {
        "$ref": "#/definitions/ApiErrorResponse",
    }
    assert client.get("/swagger.json").get_json() == original


def test_public_swagger_keeps_root_health_and_api_authentication(app):
    client = app.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/api/user/profile").status_code == 401
    html = client.get("/api/docs/").get_data(as_text=True)
    schema_path = re.search(r'url: "([^"]+)"', html).group(1)
    assert not urlsplit(schema_path).scheme


def test_public_swagger_can_be_disabled(monkeypatch):
    monkeypatch.setattr(Config, "SQLALCHEMY_DATABASE_URI", "sqlite://")
    monkeypatch.setattr(Config, "PUBLIC_SWAGGER_ENABLED", False)
    app = create_app(testing=True)
    client = app.test_client()
    for path in ("/api/docs", "/api/docs/", "/api/docs/swagger.json", "/api/docs/assets/swagger-ui-bundle.js"):
        assert client.get(path).status_code == 404
    assert client.get("/").status_code == 200
