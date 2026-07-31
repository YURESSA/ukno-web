from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from backend.core.services import merch_service


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" Summer Collection ", "summer-collection"),
        ("Футболки & Худи", "футболки-худи"),
        ("***", "category"),
        (None, "category"),
    ],
)
def test_slugify(value, expected):
    assert merch_service.slugify(value) == expected


@pytest.mark.parametrize(
    ("raw", "expected", "error"),
    [
        ({"name": "Cap"}, {"name": "Cap"}, None),
        ("", {}, None),
        ('{"name": "Cap"}', {"name": "Cap"}, None),
        ('Пример: {"name": "Cap"}', {"name": "Cap"}, None),
        ("not-json", None, "Invalid JSON payload"),
    ],
)
def test_parse_json_payload(raw, expected, error):
    assert merch_service.parse_json_payload(raw) == (expected, error)


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [(None, False, False), (True, False, True), ("yes", False, True), ("0", True, False)],
)
def test_bool_value(value, default, expected):
    assert merch_service._bool_value(value, default) is expected


def test_create_banner_requires_image():
    assert merch_service.create_banner({}) == (
        {"message": "image_path or image is required"},
        HTTPStatus.BAD_REQUEST,
    )


def test_create_banner_saves_uploaded_image(monkeypatch):
    banner_dict = {"banner_id": 1, "image_path": "saved/banner.jpg"}
    monkeypatch.setattr(merch_service, "save_image", lambda file, folder: f"saved/{file}")
    monkeypatch.setattr(merch_service.MerchBanner, "to_dict", lambda self: banner_dict)
    add = Mock()
    commit = Mock()
    monkeypatch.setattr(merch_service.db.session, "add", add)
    monkeypatch.setattr(merch_service.db.session, "commit", commit)

    response, status = merch_service.create_banner(
        {"title": "Summer", "order_index": "2", "is_active": "false"},
        "banner.jpg",
    )

    assert (response, status) == ({"banner": banner_dict}, HTTPStatus.CREATED)
    banner = add.call_args.args[0]
    assert banner.image_path == "saved/banner.jpg"
    assert banner.order_index == 2
    assert banner.is_active is False
    commit.assert_called_once()


def test_update_and_delete_banner_not_found(monkeypatch):
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: None)
    assert merch_service.update_banner(99, {})[1] == HTTPStatus.NOT_FOUND
    assert merch_service.delete_banner(99)[1] == HTTPStatus.NOT_FOUND


def test_update_banner_replaces_image_and_fields(monkeypatch):
    banner = SimpleNamespace(image_path="old.jpg", title="Old", order_index=0, is_active=True)
    banner.to_dict = lambda: {"title": banner.title, "image_path": banner.image_path}
    removed = Mock()
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: banner)
    monkeypatch.setattr(merch_service.db.session, "commit", Mock())
    monkeypatch.setattr(merch_service, "remove_file_if_exists", removed)
    monkeypatch.setattr(merch_service, "save_image", lambda *_args: "new.jpg")

    response, status = merch_service.update_banner(
        1, {"title": "New", "order_index": "3", "is_active": "0"}, "upload"
    )

    assert status == HTTPStatus.OK
    assert response["banner"] == {"title": "New", "image_path": "new.jpg"}
    assert banner.order_index == 3
    assert banner.is_active is False
    removed.assert_called_once_with("old.jpg")


def test_create_category_requires_name():
    assert merch_service.create_category({}) == (
        {"message": "name is required"},
        HTTPStatus.BAD_REQUEST,
    )


def test_create_category_handles_duplicate(monkeypatch):
    monkeypatch.setattr(merch_service.db.session, "add", Mock())
    monkeypatch.setattr(
        merch_service.db.session,
        "commit",
        Mock(side_effect=IntegrityError("statement", "params", Exception("duplicate"))),
    )
    rollback = Mock()
    monkeypatch.setattr(merch_service.db.session, "rollback", rollback)

    response, status = merch_service.create_category({"name": "Caps"})

    assert status == HTTPStatus.BAD_REQUEST
    assert response == {"message": "Category name or slug already exists"}
    rollback.assert_called_once()


def test_update_category_generates_slug(monkeypatch):
    category = SimpleNamespace(name="Old", slug="old", description=None, order_index=0, is_active=True)
    category.to_dict = lambda: {"name": category.name, "slug": category.slug}
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: category)
    monkeypatch.setattr(merch_service.db.session, "commit", Mock())

    response, status = merch_service.update_category(1, {"name": "New Caps"})

    assert status == HTTPStatus.OK
    assert response["category"] == {"name": "New Caps", "slug": "new-caps"}


def test_delete_category_rejects_category_with_products(monkeypatch):
    category = SimpleNamespace(products=[object()])
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: category)

    response, status = merch_service.delete_category(1)

    assert status == HTTPStatus.BAD_REQUEST
    assert response == {"message": "Category has products"}


def test_product_crud_rejects_missing_entities(monkeypatch):
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: None)
    assert merch_service.update_product(1, {})[1] == HTTPStatus.NOT_FOUND
    assert merch_service.delete_product(1)[1] == HTTPStatus.NOT_FOUND
    assert merch_service.list_product_images(1)[1] == HTTPStatus.NOT_FOUND
    assert merch_service.add_product_images(1, ["file"])[1] == HTTPStatus.NOT_FOUND


def test_add_product_images_requires_files(monkeypatch):
    product = SimpleNamespace(is_deleted=False, images=[])
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: product)

    response, status = merch_service.add_product_images(1, [])

    assert status == HTTPStatus.BAD_REQUEST
    assert response == {"message": "At least one image is required"}


def test_add_product_images_saves_and_orders_files(monkeypatch):
    product = SimpleNamespace(is_deleted=False, images=[])
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: product)
    monkeypatch.setattr(merch_service.db.session, "commit", Mock())
    monkeypatch.setattr(merch_service, "save_image", lambda file, _folder: f"saved/{file}")
    monkeypatch.setattr(
        merch_service.MerchProductImage,
        "to_dict",
        lambda self: {"image_path": self.image_path, "order_index": self.order_index},
    )

    response, status = merch_service.add_product_images(1, ["a.jpg", "b.jpg"], [5, 2])

    assert status == HTTPStatus.CREATED
    assert response["images"] == [
        {"image_path": "saved/b.jpg", "order_index": 2},
        {"image_path": "saved/a.jpg", "order_index": 5},
    ]


def test_update_order_status_not_found_and_success(monkeypatch):
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: None)
    assert merch_service.update_order_status(9, "paid")[1] == HTTPStatus.NOT_FOUND

    order = SimpleNamespace(status="new", to_dict=lambda: {"status": order.status})
    commit = Mock()
    monkeypatch.setattr(merch_service.db.session, "get", lambda *_args: order)
    monkeypatch.setattr(merch_service.db.session, "commit", commit)
    response, status = merch_service.update_order_status(9, "paid")
    assert (response, status) == ({"order": {"status": "paid"}}, HTTPStatus.OK)
    commit.assert_called_once()
