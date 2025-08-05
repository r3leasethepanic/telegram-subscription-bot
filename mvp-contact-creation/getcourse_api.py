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

    resp_json = resp.json()
    result = resp_json.get("result", {})

    # Проверяем булево поле success внутри result
    if not result.get("success", False):
        logging.error(f"GetCourse Import API returned error: {resp_json}")
        raise Exception(f"GC import error: {resp_json}")

    return str(result.get("user_id"))
