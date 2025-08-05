import os
import base64
import json
import requests

GC_API_URL = f"https://{os.getenv('GC_ACCOUNT')}.getcourse.ru/pl/api/users"
GC_SECRET_KEY = os.getenv("GC_API_KEY")


def encode_params(payload: dict) -> str:
    json_data = json.dumps(payload, ensure_ascii=False)
    encoded = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")
    return encoded


def add_user(email: str, phone: str, first_name: str, city: str = None) -> dict:
    user_params = {
        "user": {
            "email": email,
            "phone": phone,
            "first_name": first_name,
            "city": city,
            "auto_name": False,
            "auto_last_name": False
        },
        "system": {
            "refresh_if_exists": 1
        },
        "session": {
            "utm_source": "telegram",
            "utm_medium": "бот",
            "utm_campaign": "подписка"
        }
    }

    payload = {
        "action": "add",
        "key": GC_SECRET_KEY,
        "params": encode_params(user_params)
    }

    print("🔍 Отправка запроса в GetCourse:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    response = requests.post(
        GC_API_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    print("📩 Ответ от GC:")
    print(response.status_code)
    print(response.text)

    return response.json()
