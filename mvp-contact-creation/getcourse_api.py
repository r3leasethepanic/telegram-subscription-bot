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
    Создаёт пользователя через Import API /pl/api/users.
    Возвращает его внутренний user_id из GetCourse.
    """
    url = f"https://{GC_DOMAIN}/pl/api/users"

    # Подготовим тело для base64
    payload = {
        "user": {
            "email": email,
            "last_name": full_name
        },
        "system": {
            "refresh_if_exists": 0
        }
    }
    params_b64 = base64.b64encode(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
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

    return str(result["result"]["user_id"])

