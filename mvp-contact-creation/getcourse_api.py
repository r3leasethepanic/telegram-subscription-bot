import os
import json
import base64
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
GC_DOMAIN = os.getenv("GC_DOMAIN")          # Например "idc-education.getcourse.ru"
API_KEY   = os.getenv("GETCOURSE_API_KEY")  # Ваш секретный ключ

def gc_import_user(email: str, full_name: str) -> None:
    """
    Пытается импортировать пользователя, но **не кидает** ошибок дальше.
    """
    url = f"https://{GC_DOMAIN}/pl/api/users"
    payload = {
        "user": {"email": email, "last_name": full_name},
        "system": {"refresh_if_exists": 0}
    }
    params_b64 = base64.b64encode(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8")

    try:
        resp = requests.post(
            url,
            data={"action": "add", "key": API_KEY, "params": params_b64}
        )
        resp.raise_for_status()
        logging.info(f"[ImportUser] OK HTTP {resp.status_code}: {resp.json()}")
    except Exception as e:
        # просто логируем и **не** бросаем дальше
        logging.warning(f"[ImportUser] failed but ignoring: {e}")

def gc_get_contact_uuid(email: str) -> str:
    url = f"https://{GC_DOMAIN}/pl/api/contact.search"
    try:
        resp = requests.get(url, params={"email": email}, headers={"X-API-KEY": API_KEY})
        resp.raise_for_status()
        data = resp.json()
        logging.info(f"[GetContactUUID] response: {data}")
        contacts = data.get("response") or data.get("contacts") or []
        if not contacts:
            raise Exception("no contacts")
        uuid = contacts[0].get("uuid")
        if not uuid:
            raise Exception("uuid missing")
        return uuid
    except Exception as e:
        logging.error(f"[GetContactUUID] error: {e}")
        raise

def gc_create_order(contact_uuid: str, course_uuid: str, recurrent: bool=False) -> str:
    url = f"https://{GC_DOMAIN}/pl/api/order.add"
    payload = {"course_uuid": course_uuid, "contact_uuid": contact_uuid, "recurrent": recurrent}
    try:
        resp = requests.post(url, json=payload, headers={"X-API-KEY": API_KEY})
        resp.raise_for_status()
        data = resp.json()
        logging.info(f"[CreateOrder] response: {data}")
        link = data.get("order", {}).get("payment_link")
        if not link:
            raise Exception("link missing")
        return link
    except Exception as e:
        logging.error(f"[CreateOrder] error: {e}")
        raise


