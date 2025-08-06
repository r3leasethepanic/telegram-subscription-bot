import os
import json
import base64
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
GC_DOMAIN = os.getenv("GC_DOMAIN")          # Например "idc-education.getcourse.ru"
API_KEY   = os.getenv("GETCOURSE_API_KEY")  # Ваш секретный ключ GetCourse


def gc_import_user(email: str, full_name: str) -> None:
    """
    Создает или обновляет пользователя через Import API (/pl/api/users).
    Бросает исключение только при HTTP-коде != 200.
    """
    url = f"https://{GC_DOMAIN}/pl/api/users"
    payload = {
        "user": {"email": email, "last_name": full_name},
        "system": {"refresh_if_exists": 0}
    }
    params_b64 = base64.b64encode(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8")

    response = requests.post(
        url,
        data={
            "action": "add",
            "key": API_KEY,
            "params": params_b64
        }
    )
    response.raise_for_status()
    logging.info(f"[ImportUser] HTTP {response.status_code}, response: {response.json()}")


def gc_get_contact_uuid(email: str) -> str:
    """
    Ищет контакт в GetCourse по e-mail и возвращает его UUID.
    Бросает исключение, если контакт не найден или нет поля uuid.
    """
    url = f"https://{GC_DOMAIN}/pl/api/contact.search"
    headers = {"X-API-KEY": API_KEY}
    params = {"email": email}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    logging.info(f"[GetContactUUID] response: {data}")

    contacts = data.get("response") or data.get("contacts") or []
    if not contacts:
        raise Exception(f"No contacts found for email={email}: {data}")

    uuid = contacts[0].get("uuid")
    if not uuid:
        raise Exception(f"Contact entry has no uuid: {contacts[0]}")

    return uuid


def gc_create_order(contact_uuid: str, course_uuid: str, recurrent: bool = False) -> str:
    """
    Создает заказ через Operational API (/pl/api/order.add) и возвращает ссылку на оплату.
    Бросает исключение при ошибке HTTP или отсутствии payment_link.
    """
    url = f"https://{GC_DOMAIN}/pl/api/order.add"
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    payload = {
        "course_uuid": course_uuid,
        "contact_uuid": contact_uuid,
        "recurrent": recurrent
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    logging.info(f"[CreateOrder] response: {data}")

    link = data.get("order", {}).get("payment_link")
    if not link:
        raise Exception(f"Payment link missing in response: {data}")

    return link


