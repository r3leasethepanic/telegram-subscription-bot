import os
import json
import base64
import requests

GC_ACCOUNT  = os.getenv("GC_ACCOUNT")
GC_API_KEY  = os.getenv("GC_API_KEY")
GC_PRODUCT_ID = int(os.getenv("GC_PRODUCT_ID"))
GC_WEBHOOK_SECRET = os.getenv("GC_SECRET")

BASE_URL = f"https://{GC_ACCOUNT}.getcourse.ru/pl/api/"

def add_user(email: str, name: str) -> dict:
    payload = {
        "action": "add",
        "key": GC_API_KEY,
        "params": base64.b64encode(
            json.dumps({"user": {"email": email, "name": name}}).encode()
        ).decode()
    }
    r = requests.post(BASE_URL + "user", data=payload)
    r.raise_for_status()
    return r.json()["data"]

def create_subscription(user_id: int, success_url: str) -> str:
    params = {
        "user[id]": user_id,
        "product[id]": GC_PRODUCT_ID,
        "type": "recurring",
        "success_url": success_url
    }
    payload = {
        "action": "add",
        "key": GC_API_KEY,
        "params": base64.b64encode(json.dumps({"subscription": params}).encode()).decode()
    }
    r = requests.post(BASE_URL + "subscriptions", data=payload)
    r.raise_for_status()
    return r.json()["data"]["url"]
