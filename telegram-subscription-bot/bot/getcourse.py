import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

GC_ACCOUNT = os.getenv("GC_ACCOUNT")
GC_API_KEY = os.getenv("GC_API_KEY")

def add_user(data):
    url = f"https://{GC_ACCOUNT}.getcourse.ru/pl/api/users"
    params = {
        "user": {
            "email": data["email"],
            "phone": data["phone"],
            "first_name": data["username"],
            "city": data["city"],
        },
        "system": {
            "refresh_if_exists": 1
        }
    }
    encoded = base64.b64encode(json.dumps(params).encode("utf-8")).decode("utf-8")
    payload = {
        "action": "add",
        "key": GC_API_KEY,
        "params": encoded
    }

    response = requests.post(url, data=payload)
    print(f"[GC] Ответ: {response.text}")
    return response.json()
