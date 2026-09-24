from io import BytesIO

from werkzeug.datastructures import FileStorage

from backend.core.config import Config
from backend.core.storage import file_url, get_s3_client, object_key
from backend.core.utilits.file_utils import remove_file_if_exists, save_image


class FakeS3Client:
    def __init__(self):
        self.objects = {}
        self.deleted = []

    def upload_fileobj(self, file_obj, bucket, key, **kwargs):
        self.objects[(bucket, key)] = (file_obj.read(), kwargs)

    def head_object(self, Bucket, Key):
        assert (Bucket, Key) in self.objects

    def delete_object(self, Bucket, Key):
        self.deleted.append((Bucket, Key))
        self.objects.pop((Bucket, Key), None)

    def generate_presigned_url(self, operation, Params, ExpiresIn):
        return f"https://signed.example/{Params['Bucket']}/{Params['Key']}?expires={ExpiresIn}"


def configure_s3(monkeypatch, client):
    monkeypatch.setattr(Config, "STORAGE_BACKEND", "s3")
    monkeypatch.setattr(Config, "S3_BUCKET", "test-bucket")
    monkeypatch.setattr(Config, "S3_KEY_PREFIX", "ukno")
    monkeypatch.setattr(Config, "S3_PUBLIC_BASE_URL", "")
    monkeypatch.setattr(Config, "S3_PRESIGNED_URL_EXPIRES", 900)
    get_s3_client.cache_clear()
    monkeypatch.setattr("backend.core.storage.get_s3_client", lambda: client)


def test_s3_image_upload_and_delete(monkeypatch):
    client = FakeS3Client()
    configure_s3(monkeypatch, client)
    image = FileStorage(
        stream=BytesIO(b"image-bytes"),
        filename="photo.jpg",
        content_type="image/jpeg",
    )

    saved_path = save_image(image, "news")

    assert saved_path.startswith("media/uploads/news/photo_")
    key = object_key(saved_path)
    body, kwargs = client.objects[("test-bucket", key)]
    assert body == b"image-bytes"
    assert kwargs == {"ExtraArgs": {"ContentType": "image/jpeg"}}

    remove_file_if_exists(saved_path)

    assert client.deleted == [("test-bucket", key)]
    assert ("test-bucket", key) not in client.objects


def test_s3_file_url_is_presigned(monkeypatch):
    client = FakeS3Client()
    configure_s3(monkeypatch, client)

    url = file_url("news/example.jpg")

    assert url == "https://signed.example/test-bucket/ukno/news/example.jpg?expires=900"


def test_external_url_is_not_deleted_from_bucket(monkeypatch):
    client = FakeS3Client()
    configure_s3(monkeypatch, client)

    remove_file_if_exists("https://cdn.example/external.jpg")

    assert client.deleted == []
