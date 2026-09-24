from functools import lru_cache
from urllib.parse import unquote, urlparse

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from backend.core.config import Config


MEDIA_PREFIX = "media/uploads/"


def uses_s3() -> bool:
    return Config.STORAGE_BACKEND == "s3"


def _require_s3_settings() -> None:
    missing = [
        name
        for name, value in (
            ("S3_ACCESS_KEY", Config.S3_ACCESS_KEY),
            ("S3_SECRET_KEY", Config.S3_SECRET_KEY),
            ("S3_BUCKET/BUCKET", Config.S3_BUCKET),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing S3 settings: {', '.join(missing)}")


@lru_cache(maxsize=1)
def get_s3_client():
    _require_s3_settings()
    return boto3.client(
        "s3",
        endpoint_url=Config.S3_ENDPOINT,
        aws_access_key_id=Config.S3_ACCESS_KEY,
        aws_secret_access_key=Config.S3_SECRET_KEY,
        region_name=Config.S3_REGION,
        config=BotoConfig(
            signature_version="s3v4",
            s3={"addressing_style": Config.S3_ADDRESSING_STYLE},
        ),
    )


def object_key(relative_path: str) -> str:
    relative_path = relative_path.replace("\\", "/").lstrip("/")
    if relative_path.startswith(MEDIA_PREFIX):
        relative_path = relative_path[len(MEDIA_PREFIX):]
    prefix = Config.S3_KEY_PREFIX
    if prefix and not relative_path.startswith(f"{prefix}/"):
        return f"{prefix}/{relative_path}"
    return relative_path


def upload(file_obj, relative_path: str, content_type: str | None = None) -> None:
    client = get_s3_client()
    file_obj.seek(0)
    kwargs = {"ExtraArgs": {"ContentType": content_type}} if content_type else {}
    client.upload_fileobj(file_obj, Config.S3_BUCKET, object_key(relative_path), **kwargs)


def _owned_object_key(file_path: str) -> str | None:
    normalized = file_path.replace("\\", "/")
    if normalized.startswith(MEDIA_PREFIX) or normalized.startswith(f"/{MEDIA_PREFIX}"):
        return object_key(normalized.lstrip("/"))

    parsed = urlparse(normalized)
    if not parsed.scheme or not parsed.netloc:
        return None

    if Config.S3_PUBLIC_BASE_URL and normalized.startswith(f"{Config.S3_PUBLIC_BASE_URL}/"):
        return unquote(normalized[len(Config.S3_PUBLIC_BASE_URL) + 1:])

    endpoint = urlparse(Config.S3_ENDPOINT)
    endpoint_path = parsed.path.lstrip("/")
    if parsed.netloc == endpoint.netloc and endpoint_path.startswith(f"{Config.S3_BUCKET}/"):
        return unquote(endpoint_path[len(Config.S3_BUCKET) + 1:])
    return None


def delete(file_path: str) -> bool:
    key = _owned_object_key(file_path)
    if key is None:
        return False
    try:
        get_s3_client().head_object(Bucket=Config.S3_BUCKET, Key=key)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise
    get_s3_client().delete_object(Bucket=Config.S3_BUCKET, Key=key)
    return True


def file_url(relative_path: str) -> str:
    key = object_key(relative_path)
    if Config.S3_PUBLIC_BASE_URL:
        return f"{Config.S3_PUBLIC_BASE_URL}/{key}"
    return get_s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": Config.S3_BUCKET, "Key": key},
        ExpiresIn=Config.S3_PRESIGNED_URL_EXPIRES,
    )
