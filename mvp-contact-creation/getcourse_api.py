import os
import json
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

GC_DOMAIN = os.getenv("GC_DOMAIN")          # ваш аккаунт, например "idc-education.getcourse.ru"
API_KEY   = os.getenv("GETCOURSE_API_KEY")  # ваш секретный ключ

def gc_import_user(email: str, full_name: str) -> str:
    """
    Создаёт (или обновляет, если refresh_if_exists=1) пользователя в GetCourse
    через Import API и возвращает его ID.
    """
    url = f"https://{GC_DOMAIN}/pl/api/users"
    
    # Сформируем тело запроса:
    payload_obj = {
        "user": {
            "email": email,
            "last_name": full_name,
            # опционально first_name, phone, city и т.д.
        },
        "system": {
            "refresh_if_exists": 0  # 1 — обновлять существующего, 0 — только новый
        },
        "session": {
            # здесь UTM или gcpc, не обязательно
        }
    }
    # Параметр params — это base64 от JSON-строки:
    params_b64 = base64.b64encode(
        json.dumps(payload_obj, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8")

    data = {
        "action": "add",
        "key": API_KEY,
        "params": params_b64
    }

    resp = requests.post(url, data=data)
    resp.raise_for_status()
    result = resp.json()

    # Проверяем успех
    if result.get("success") != "true":
        raise Exception(f"Ошибка импорта в GetCourse: {result}")

    # ID созданного/существующего пользователя
    return result["result"]["user_id"]
