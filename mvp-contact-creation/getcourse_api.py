import os
import json
import base64
import logging
import requests
from dotenv import load_dotenv

# Загружаем конфиг из .env
load_dotenv()
GC_DOMAIN = os.getenv("GC_DOMAIN")          # ваш домен, например "idceducation.getcourse.ru"
API_KEY   = os.getenv("GETCOURSE_API_KEY")  # секретный ключ GetCourse


def gc_import_user(email: str, full_name: str) -> None:
    """
    Импортирует или обновляет пользователя через Import API.
    Ошибки HTTP-кодов логируются, но не прерывают выполнение.
    """
    url = f"https://{GC_DOMAIN}/pl/api/users"
    payload = {
        "user": {"email": email, "last_name": full_name},
        "system": {"refresh_if_exists": 0}
    }
    params_b64 = base64.b64encode(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ).decode()

    try:
        response = requests.post(
            url,
            data={"action": "add", "key": API_KEY, "params": params_b64}
        )
        response.raise_for_status()
        logging.info(f"[ImportUser] Успех: HTTP {response.status_code}, ответ: {response.json()}")
    except requests.HTTPError as http_err:
        logging.warning(f"[ImportUser] HTTP ошибка: {http_err}")
    except Exception as err:
        logging.warning(f"[ImportUser] Другая ошибка: {err}")


def gc_get_contact_uuid(email: str) -> str:
    """
    Находит контакт по e-mail и возвращает его UUID.
    """
    url = f"https://{GC_DOMAIN}/pl/api/contact.search"
    headers = {"X-API-KEY": API_KEY}
    params = {"email": email}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    logging.info(f"[GetContactUUID] ответ: {data}")

    contacts = data.get("response") or data.get("contacts") or []
    if not contacts:
        raise Exception(f"Контакт не найден для email={email}")

    uuid = contacts[0].get("uuid")
    if not uuid:
        raise Exception(f"UUID отсутствует в контакте: {contacts[0]}")
    return uuid


def gc_create_order(contact_uuid: str, course_uuid: str, recurrent: bool = False) -> str:
    """
    Создает заказ через Order API и возвращает ссылку на оплату.
    """
    url = f"https://{GC_DOMAIN}/pl/api/order.add"
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    payload = {
        "course_uuid": course_uuid,
        "contact_uuid": contact_uuid,
        "recurrent": recurrent
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    logging.info(f"[CreateOrder] ответ: {data}")

    link = data.get("order", {}).get("payment_link")
    if not link:
        raise Exception(f"Ссылка на оплату отсутствует в ответе: {data}")
    return link
