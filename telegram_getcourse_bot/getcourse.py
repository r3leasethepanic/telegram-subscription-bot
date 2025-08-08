import os
import logging
import base64
import json
import requests

# Настройка логирования для отладки API-запросов
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

# Получаем конфигурацию из переменных окружения
API_KEY = os.getenv("GETCOURSE_API_KEY")
ACCOUNT = os.getenv("GETCOURSE_ACCOUNT_NAME")
BASE_URL = f"https://{ACCOUNT}.getcourse.ru/pl/api"

def _call_api(path: str, action: str, payload: dict) -> dict:
    """
    Выполняет POST-запрос к GetCourse API и логирует детали запроса и ответа.
    """
    url = f"{BASE_URL}/{path}"
    # Кодируем параметры в base64
    params_b64 = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    data = {"action": action, "key": API_KEY, "params": params_b64}

    logging.debug("→ URL        : %s", url)
    logging.debug("→ ACTION     : %s", action)
    logging.debug("→ RAW PAYLOAD: %s", payload)
    logging.debug("→ ENCODED    : %s", params_b64)

    # Выполняем запрос
    try:
        resp = requests.post(url, data=data)
    except Exception as e:
        logging.error("Request exception: %s", e, exc_info=True)
        raise

    logging.debug("← Status code: %s", resp.status_code)
    logging.debug("← Response   : %s", resp.text)

    # Бросаем ошибку, если статус не 2XX
    resp.raise_for_status()
    return resp.json()

def create_user(email: str, first_name: str, last_name: str) -> dict:
    """
    Создает пользователя в GetCourse.
    """
    payload = {
        "user": {"email": email, "first_name": first_name, "last_name": last_name},
        "system": {"refresh_if_exists": 0},
        "session": {}
    }
    return _call_api("users", "add", payload)

def create_order(email: str, offer_code: str, cost: float) -> dict:
    """
    Создает заказ и возвращает ссылку на оплату.
    """
    payload = {
        "user": {"email": email},
        "system": {"refresh_if_exists": 0, "return_payment_link": 1},
        "session": {},
        "deal": {"offer_code": offer_code, "deal_cost": cost}
    }
    return _call_api("deals", "add", payload)

