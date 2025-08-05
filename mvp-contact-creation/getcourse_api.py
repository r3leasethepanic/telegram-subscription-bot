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
    Возвращает его внутренний user_id.
    """
    url = f"https://{GC_DOMAIN}/pl/api/users"
    payload = {
        "user": {"email": email, "last_name": full_name},
        "system": {"refresh_if_exists": 0}
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
    resp.raise_for_status()
    resp_json = resp.json()
    logging.info(f"Import API response: {resp_json}")

    try:
        return str(resp_json["result"]["user_id"])
    except Exception:
        logging.error(f"Unexpected Import API response: {resp_json}")
        raise

def gc_create_order(user_id: str, course_uuid: str, recurrent: bool = False) -> str:
    """
    Создаёт заказ через API /pl/api/order.add и возвращает ссылку на оплату.
    """
    url = f"https://{GC_DOMAIN}/pl/api/order.add"
    payload = {
        "course_uuid": course_uuid,
        "contact_uuid": user_id,
        "recurrent": recurrent
    }
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    resp_json = resp.json()
    logging.info(f"Order API response: {resp_json}")

    link = resp_json.get("order", {}).get("payment_link")
    if not link:
        logging.error(f"No payment link in response: {resp_json}")
        raise Exception(f"Payment link missing: {resp_json}")
    return link
