import os
import base64
import json
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Настройки API
API_KEY = os.getenv("GETCOURSE_API_KEY")
ACCOUNT = os.getenv("GETCOURSE_ACCOUNT_NAME")
BASE_URL = f"https://{ACCOUNT}.getcourse.ru/pl/api"

def _call_api(path: str, action: str, payload: dict) -> dict:
    """
    Выполняет POST-запрос к GetCourse API и возвращает распарсенный ответ.
    """
    url = f"{BASE_URL}/{path}"
    params_b64 = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    data = {"action": action, "key": API_KEY, "params": params_b64}

    # Отправляем запрос
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    return resp.json()

def create_user(email: str, first_name: str, last_name: str) -> dict:
    """
    Создает пользователя в GetCourse.
    :param email: Email нового пользователя
    :param first_name: Имя пользователя
    :param last_name: Фамилия пользователя
    :return: Ответ API в виде dict
    """
    payload = {
        "user": {"email": email, "first_name": first_name, "last_name": last_name},
        "system": {"refresh_if_exists": 0},
        "session": {}
    }
    return _call_api("users", "add", payload)

def create_order(email: str, offer: str, cost: float) -> dict:
    """
    Создает заказ (сделку) для пользователя и возвращает ссылку на оплату.
    Поддерживает как числовой offer_id, так и строковый offer_code.

    :param email: Email пользователя
    :param offer: Идентификатор предложения (числовой ID или строковый код)
    :param cost: Сумма заказа
    :return: Ответ API в виде dict
    """
    # Формируем поле deal: используем offer_id если передано число, иначе offer_code
    deal_params = {"deal_cost": cost}
    if offer.isdigit():
        deal_params["offer_id"] = int(offer)
    else:
        deal_params["offer_code"] = offer

    payload = {
        "user": {"email": email},
        "system": {"refresh_if_exists": 0, "return_payment_link": 1},
        "session": {},
        "deal": deal_params
    }
    return _call_api("deals", "add", payload)

