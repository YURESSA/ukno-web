import requests

from backend.core.config import Config


def get_yandex_suggestions(text):
    api_key = Config.YANDEX_API_KEY
    url = "https://suggest-maps.yandex.ru/v1/suggest"

    ekb_ll = "60.6057,56.8389"

    spn = "0.3,0.3"

    params = {
        "text": text,
        "ll": ekb_ll,
        "spn": spn,
        "apikey": api_key,
        "lang": "ru_RU",
        "results": 10,
        "strict_bounds": 0
    }

    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    return response.json()
