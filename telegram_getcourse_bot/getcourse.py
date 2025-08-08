import os
import base64
import json
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env при импорте модуля
load_dotenv()

# Получаем настройки
API_KEY = os.getenv("GETCOURSE_API_KEY")
ACCOUNT = os.getenv("GETCOURSE_ACCOUNT_NAME")
BASE_URL = f"https://{ACCOUNT}.getcourse.ru/pl/api"

def _call_api(path: str, action: str, payload: dict) -> dict:
    """
    Выполняет POST-запрос к GetCourse API и выводит отладочную информацию.
    """
    url = f"{BASE_URL}/{path}"
    params_b64 = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    data = {"action": action, "key": API_KEY, "params": params_b64}

    # Отладочный вывод
    print("=== GetCourse Debug ===")
    print("URL       :", url)
    print("ACTION    :", action)
    print("RAW PAYLOAD:", payload)
    print("ENCODED   :", params_b64)

    resp = requests.post(url, data=data)

    print("Status code:", resp.status_code)
    print("Response   :", resp.text)
    print("=======================")

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

