from io import BytesIO

import pytest
from flask_jwt_extended import create_access_token

from backend.api.references import ref_partner
from backend.core import create_app, db
from backend.core.config import Config
from backend.core.errors import NotFoundError, ValidationError
from backend.core.models.auth_models import RoleEnum, User
from backend.core.models.ref_models import CulturalSpace, Partner, Requisite, TeamMember


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "SQLALCHEMY_DATABASE_URI", f"sqlite:///{tmp_path / 'references.db'}")
    monkeypatch.setattr(Config, "STORAGE_BACKEND", "local")
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        user = User(full_name="Admin", email="admin@example.com", phone="+70000000000", role=RoleEnum.ADMIN)
        user.set_password("StrongPassword123!")
        db.session.add_all([
            user, Partner(id=1, name="Partner"), CulturalSpace(id=1, text="Space"),
            TeamMember(id=1, full_name="Member"), Requisite(id=1, title="Requisite"),
        ])
        db.session.commit()
        token = create_access_token(identity=user.email, additional_claims={"role": "admin"})
        test_client = app.test_client()
        test_client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        yield test_client
        db.session.remove()
        db.drop_all()


def assert_error(response, status, message):
    assert response.status_code == status
    assert response.get_json() == {"message": message}
    assert response.mimetype == "application/json"


def test_missing_reference_responses(client):
    for resource, message, methods in [
        ("partners", "Партнёр не найден", ("GET", "PUT", "DELETE")),
        ("cultural-space", "Элемент не найден", ("GET", "PUT", "DELETE")),
        ("team", "Сотрудник не найден", ("GET", "PUT", "DELETE")),
        ("requisites", "Реквизит не найден", ("GET", "PUT", "DELETE")),
        ("projects", "Проект не найден", ("GET", "PUT", "DELETE")),
        ("history", "Событие не найдено", ("GET", "PUT", "DELETE")),
        ("trust-reasons", "Причина не найдена", ("DELETE",)),
        ("categories", "Категория не найдена", ("DELETE",)),
        ("age-categories", "Возрастная категория не найдена", ("DELETE",)),
        ("format-types", "Тип формата не найден", ("DELETE",)),
    ]:
        for method in methods:
            assert_error(client.open(f"/api/references/{resource}/999", method=method), 404, message)

    for resource, message, suffix in [
        ("partners", "Партнёр не найден", "photo"),
        ("cultural-space", "Элемент не найден", "photo"),
        ("team", "Сотрудник не найден", "photo"),
        ("requisites", "Реквизит не найден", "file"),
    ]:
        for method in ("POST", "DELETE"):
            assert_error(client.open(f"/api/references/{resource}/999/{suffix}", method=method), 404, message)


def test_reference_validation_responses(client):
    for resource, data, message in [
        ("projects", {}, "Поле title обязательно"),
        ("projects", {"title": "Project"}, "Поле link обязательно"),
        ("history", {}, "Поле title обязательно"),
        ("history", {"title": "Event"}, "Поле date обязательно"),
        ("history", {"title": "Event", "date": "2026-10-13"}, "Поле description обязательно"),
        ("history", {"title": "Event", "date": "invalid", "description": "Text"},
         "Неверный формат даты. Используйте YYYY-MM-DD"),
        ("trust-reasons", {}, "Поле title обязательно"),
        ("format-types", {}, "Поле name обязательно"),
        ("categories", {}, "Поле name обязательно"),
        ("age-categories", {}, "Поле name обязательно"),
    ]:
        assert_error(client.post(f"/api/references/{resource}", json=data), 400, message)

    for resource in ("partners", "cultural-space", "team"):
        assert_error(client.delete(f"/api/references/{resource}/1/photo"), 400, "Фото отсутствует")
    assert_error(client.delete("/api/references/requisites/1/file"), 400, "Файл отсутствует")
    assert_error(client.post("/api/references/requisites", data={"title": "Doc"}), 400, "Файл обязателен")


def test_image_validation_preserves_route_specific_statuses(client):
    for resource, status in (("partners", 400), ("team", 400), ("cultural-space", 404)):
        for body, filename, content_type, message in [
            (b"document", "document.txt", "text/plain", "Файл должен быть изображением"),
            (b"fake", "fake.jpg", "image/jpeg", "Содержимое файла не соответствует формату изображения"),
            (b"x" * (5 * 1024 * 1024 + 1), "large.jpg", "image/jpeg", "Размер файла не должен превышать 5 MB"),
        ]:
            response = client.post(
                f"/api/references/{resource}/1/photo",
                data={"photo": (BytesIO(body), filename, content_type)},
            )
            assert_error(response, status, message)


def test_reference_parser_errors_keep_details(client):
    response = client.post("/api/references/team", data={})
    assert response.status_code == 400
    assert response.get_json() == {
        "errors": {"full_name": "Missing required parameter in the post body"},
        "message": "Input payload validation failed",
    }


@pytest.mark.parametrize("error_type, status", [(NotFoundError, 404), (ValidationError, 400)])
def test_status_depends_on_error_type_not_message(client, monkeypatch, error_type, status):
    def fail(partner_id):
        raise error_type("Changed error wording")

    monkeypatch.setattr(ref_partner, "delete_partner_photo", fail)
    assert_error(client.delete("/api/references/partners/1/photo"), status, "Changed error wording")


def test_unexpected_errors_keep_server_error_status(client, monkeypatch):
    def fail(partner_id):
        raise RuntimeError("Unexpected failure")

    monkeypatch.setattr(ref_partner, "delete_partner_photo", fail)
    assert_error(client.delete("/api/references/partners/1/photo"), 500, "Internal server error")


def test_successful_reference_crud_keeps_response_format(client):
    response = client.post("/api/references/projects", json={"title": "Project", "link": "https://example.com"})
    assert response.status_code == 201
    project = response.get_json()
    assert project == {"id": project["id"], "title": "Project", "link": "https://example.com", "order_index": 0}
    url = f"/api/references/projects/{project['id']}"
    assert client.get(url).get_json() == project
    response = client.put(url, json={"title": "Updated", "link": "https://example.com"})
    assert response.status_code == 200
    assert response.get_json() == {**project, "title": "Updated"}
    response = client.delete(url)
    assert response.status_code == 200
    assert response.get_json() == {"message": "Проект удалён"}
