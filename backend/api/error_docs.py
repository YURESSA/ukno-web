"""Swagger error contracts. This module documents responses without marshalling them."""
import re
from copy import deepcopy

from flask_restx import fields
from flask_restx.model import ModelBase


# Business errors are explicit: an ID in a URL does not always imply a 404.
# Framework/authorization errors are added separately from request/decorator metadata.
BUSINESS_ERRORS = {
    "/api/login": {"post": (400, 401)},
    "/api/admin/login": {"post": (400, 401, 403)},
    "/api/resident/login": {"post": (400, 401, 403)},
    "/api/user/login": {"post": (400, 401, 403)},
    "/api/user/register": {"post": (400, 409)},
    "/api/admin/profile": {"get": (404,), "put": (400,)},
    "/api/resident/profile": {"get": (404,), "put": (400, 401, 404), "delete": (400, 404)},
    "/api/user/profile": {"get": (404,), "put": (400, 404), "delete": (400, 404)},
    "/api/user/profile/password": {"put": (400, 401, 404)},
    "/api/user/password-reset": {"post": (400, 404)},
    "/api/admin/users": {"post": (400, 409)},
    "/api/admin/users/detail/{email}": {"get": (404,), "put": (400, 404), "delete": (400, 404)},
    "/api/admin/excursions": {"get": (400,), "post": (400,)},
    "/api/admin/excursions/{excursion_id}/approve": {"post": (400, 404, 409)},
    "/api/admin/excursions/{excursion_id}/return": {"post": (400, 404, 409)},
    "/api/resident/excursions/{excursion_id}/submit": {"post": (404, 409)},
    "/api/admin/excursions/{excursion_id}": {"get": (404,), "patch": (400, 404), "delete": (404,)},
    "/api/admin/excursions/{excursion_id}/sessions": {"post": (400,)},
    "/api/admin/excursions/{excursion_id}/sessions/{session_id}": {"patch": (400, 404), "delete": (400, 404)},
    "/api/admin/excursions/{excursion_id}/photos": {"get": (404,), "post": (400, 404)},
    "/api/admin/excursions/{excursion_id}/photos/{photo_id}": {"delete": (404,)},
    "/api/resident/excursions": {"post": (400,)},
    "/api/resident/excursions/{excursion_id}": {"get": (404,), "patch": (400, 404), "delete": (404,)},
    "/api/resident/excursions/{excursion_id}/sessions": {"get": (404,), "post": (400, 404)},
    "/api/resident/excursions/{excursion_id}/sessions/{session_id}": {"patch": (400, 404), "delete": (400, 404)},
    "/api/resident/excursions/{excursion_id}/photos": {"get": (404,), "post": (400, 404)},
    "/api/resident/excursions/{excursion_id}/photos/{photo_id}": {"delete": (404,)},
    "/api/user/excursions_detail/{excursion_id}": {"get": (404,)},
    "/api/user/news/{news_id}": {"get": (404,)},
    "/api/admin/news": {"post": (400, 404)},
    "/api/admin/news/{news_id}": {"get": (404,), "put": (400, 404), "delete": (404,)},
    "/api/admin/news/{news_id}/photos": {"get": (404,), "post": (400, 404)},
    "/api/admin/news/{news_id}/photos/{photo_id}": {"delete": (404,)},
    "/api/user/v2/reservations": {"post": (400, 404, 409, 502), "delete": (400, 404)},
    "/api/user/reservations/{reservation_id}/export_ical": {"get": (404,)},
    "/api/user/reservations/{reservation_id}/google_calendar_link": {"get": (404,)},
    "/api/admin/reservations/{reservation_id}": {"get": (404,), "delete": (400, 404)},
    "/api/admin/merch/banners": {"post": (400,)},
    "/api/admin/merch/banners/{banner_id}": {"put": (400, 404), "delete": (404,)},
    "/api/admin/merch/categories": {"post": (400,)},
    "/api/admin/merch/categories/{category_id}": {"put": (400, 404), "delete": (400, 404)},
    "/api/admin/merch/products": {"post": (400, 404)},
    "/api/admin/merch/products/{product_id}": {"get": (404,), "put": (400, 404), "delete": (404,)},
    "/api/admin/merch/products/{product_id}/colors": {"post": (400, 404)},
    "/api/admin/merch/products/{product_id}/colors/{color_id}/sizes": {"post": (400, 404)},
    "/api/admin/merch/products/{product_id}/images": {"get": (404,), "post": (400, 404)},
    "/api/admin/merch/products/{product_id}/images/{image_id}": {"put": (400, 404), "delete": (404,)},
    "/api/admin/merch/orders/{order_id}": {"put": (404,), "patch": (404,)},
    "/api/user/merch/products/{product_id}": {"get": (404,)},
    "/api/user/merch/products/{product_id}/favorite": {"post": (404,)},
    "/api/user/merch/cart": {"post": (400, 404)},
    "/api/user/merch/cart/{cart_item_id}": {"put": (400, 404), "delete": (404,)},
    "/api/user/merch/orders": {"post": (400, 502)},
    "/api/webhook/yookassa": {"post": (400, 503)},
    "/api/yandex/map-helper": {"get": (400,)},
}

ERROR_DESCRIPTIONS = {
    400: "Некорректные данные, JSON или параметры; ошибка валидации или бизнес-ограничение.",
    401: "Требуется JWT, токен истёк, пользователь не найден или неверные учётные данные.",
    403: "Недостаточно прав, неверная роль или отсутствует доступ к объекту.",
    404: "Запрошенный объект не найден или недоступен текущему пользователю.",
    409: "Конфликт: запись уже существует, повторная бронь или недостаточно свободных мест.",
    413: "Превышен лимит тела запроса, размера формы или числа multipart-частей.",
    415: "Для JSON-запроса требуется Content-Type: application/json.",
    422: "JWT повреждён, имеет неверную подпись, тип или обязательные claims.",
    500: "Внутренняя ошибка: сбой БД, хранилища, внешнего сервиса или необработанное исключение.",
    502: "Не удалось создать платёж во внешнем платёжном сервисе.",
    503: "Платёжный сервис временно недоступен: не удалось проверить webhook.",
}

ERROR_CONTRACT_DESCRIPTION = """

### Ошибки API
Ошибка возвращается как JSON с непустым строковым `message`. HTTP-статус определяет
тип ошибки; текст сообщения не является стабильным машинным кодом.
Дополнительные поля сохраняются: `msg` для совместимости JWT, `errors` с ошибками
полей, `available` с остатком товара, лимиты `max_content_length` и
`max_form_memory_size`. Неизвестные дополнительные поля следует игнорировать.
Схема ошибок используется только в документации и не меняет ответы приложения.

Ожидаемые бизнес-ошибки указаны у соответствующих операций. Неожиданные сбои
покрывает ответ 500. Вне конкретной операции возможны 404 (неизвестный URL) и
405 (неподдерживаемый HTTP-метод, допустимые методы перечислены в заголовке Allow).
Ошибки прокси, веб-сервера, сетевые обрывы и отсутствие ответа находятся за пределами
контракта Flask и могут не содержать JSON. Для HEAD тело ответа не передаётся по HTTP.
"""


class JSONValue(fields.Raw):
    """A legacy body can contain any JSON value, not just an object."""
    __schema_type__ = None


def _reference_errors(path, method):
    if method == "get":
        return {404} if "{" in path else set()
    if method == "post":
        return {400, 404} if "{" in path else {400}
    if method == "put":
        return {400, 404}
    if method == "delete":
        return {400, 404} if path.endswith(("/photo", "/file")) else {404}
    return set()


def document_error_responses(api):
    """Add error schemas without response marshalling or runtime status changes."""
    model_name = "ApiErrorResponse"
    if model_name not in api.models:
        api.model(model_name, {
            "message": fields.String(
                required=True, min_length=1, description="Описание ошибки", example="Фото отсутствует",
            ),
            "msg": fields.String(description="Прежнее сообщение JWT; сохранено для совместимости"),
            "errors": fields.Raw(description="Ошибки отдельных полей формы или JSON"),
            "available": fields.Integer(description="Доступное количество товара при нехватке остатка"),
            "max_content_length": fields.Integer(description="Лимит размера запроса в байтах"),
            "max_form_memory_size": fields.Integer(description="Лимит памяти формы в байтах"),
            "data": JSONValue(description="Прежнее тело ошибки, если оно не было JSON-объектом"),
        })
    if ERROR_CONTRACT_DESCRIPTION not in api.description:
        api.description += ERROR_CONTRACT_DESCRIPTION

    for namespace in api.namespaces:
        for registration in namespace.resources:
            resource = registration.resource
            doc = deepcopy(getattr(resource, "__apidoc__", {}))
            if doc is False:
                continue
            paths = [re.sub(r"<(?:\w+:)?(\w+)>", r"{\1}", url)
                     for url in api.ns_urls(namespace, registration.urls)]
            for method in resource.methods - {"HEAD", "OPTIONS"}:
                method = method.lower()
                handler = getattr(resource, method)
                method_doc = deepcopy(getattr(handler, "__apidoc__", {}))
                if method_doc is False:
                    continue
                statuses = {500}
                for path in paths:
                    statuses.update(BUSINESS_ERRORS.get(path, {}).get(method, ()))
                    if path.startswith("/api/references/"):
                        statuses.update(_reference_errors(path, method))
                auth = getattr(handler, "api_auth", None)
                method_doc["security"] = "Bearer" if auth and auth != "optional" else []
                if auth and auth != "optional":
                    statuses.update((401, 422))
                    if auth != "jwt":
                        statuses.add(403)
                if method in {"post", "put", "patch", "delete"}:
                    statuses.update((400, 413))
                if any(isinstance(expected, ModelBase) for expected in method_doc.get("expect", [])):
                    statuses.add(415)
                responses = dict(doc.get("responses", {}))
                responses.update(method_doc.get("responses", {}))
                if not responses:
                    responses[200] = ("Success", None)
                for status in statuses:
                    # Keep existing endpoint descriptions but replace missing error schemas.
                    previous = responses.pop(str(status), responses.pop(status, None))
                    description = previous if isinstance(previous, str) else previous[0] if previous else None
                    if status == 404 and "/api/references/cultural-space/{id}/photo" in paths and method == "post":
                        description = "Элемент не найден либо фото некорректно (исторический статус 404)."
                    responses[status] = (description or ERROR_DESCRIPTIONS[status], model_name)
                method_doc["responses"] = responses
                handler.__apidoc__ = method_doc
                doc[method] = method_doc
            resource.__apidoc__ = doc
