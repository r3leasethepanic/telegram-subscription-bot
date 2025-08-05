import os
import json
import base64
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

GC_DOMAIN = os.getenv("GC_DOMAIN")          # например "idc-education.getcourse.ru"
API_KEY   = os.getenv("GETCOURSE_API_KEY")  # ваш секретный ключ

def gc_import_user(email: str, full_name: str) -> str:
    """
    Создаёт (или только добавляет) пользователя в GetCourse через Import API.
    Возвращает его внутренний user_id.
    """
    url = f"https://{GC_DOMAIN}/pl/api/users"

    # Формируем тело запроса
    payload_obj = {
        "user": {
            "email": email,
            "last_name": full_name
        },
        "system": {
            "refresh_if_exists": 0  # 0 — не обновлять, если существует; 1 — обновлять
        }
    }
    # Параметр params — это base64 от JSON-строки
    params_b64 = base64.b64encode(
        json.dumps(payload_obj, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8")

    data = {
        "action": "add",
        "key": API_KEY,
        "params": params_b64
    }

    resp = requests.post(url, data=data)
    if resp.status_code != 200:
        logging.error(f"GetCourse Import API HTTP {resp.status_code}: {resp.text}")
    resp.raise_for_status()

    result = resp.json()
    if result.get("success") != "true":
        logging.error(f"GetCourse Import API error response: {result}")
        raise Exception(f"GC import error: {result}")

    # Возвращаем строковый ID пользователя
    return str(result["result"]["user_id"])
