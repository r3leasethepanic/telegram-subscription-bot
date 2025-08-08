import os
import base64
import json
import requests

API_KEY = os.getenv("GETCOURSE_API_KEY")
ACCOUNT = os.getenv("GETCOURSE_ACCOUNT_NAME")
BASE_URL = f"https://{ACCOUNT}.getcourse.ru/pl/api"

def _call_api(path: str, action: str, payload: dict) -> dict:
    url = f"{BASE_URL}/{path}"
    params_b64 = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    data = {"action": action, "key": API_KEY, "params": params_b64}
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()

def create_user(email: str, first_name: str, last_name: str) -> dict:
    payload = {
        "user": {"email": email, "first_name": first_name, "last_name": last_name},
        "system": {"refresh_if_exists": 0},
        "session": {}
    }
    return _call_api("users", "add", payload)

def create_order(email: str, offer_code: str, cost: float) -> dict:
    payload = {
        "user": {"email": email},
        "system": {"refresh_if_exists": 0, "return_payment_link": 1},
        "session": {},
        "deal": {"offer_code": offer_code, "deal_cost": cost}
    }
    return _call_api("deals", "add", payload)

