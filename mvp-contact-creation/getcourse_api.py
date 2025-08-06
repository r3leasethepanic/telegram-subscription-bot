import os, json, base64, logging, requests
from dotenv import load_dotenv

load_dotenv()
GC_DOMAIN = os.getenv("GC_DOMAIN")          # e.g. "idc-education.getcourse.ru"
API_KEY   = os.getenv("GETCOURSE_API_KEY")  # ваш секретный ключ

def gc_import_user(email: str, full_name: str) -> None:
    """Создаёт или обновляет пользователя в Import API."""
    url = f"https://{GC_DOMAIN}/pl/api/users"
    payload = {
        "user": {"email": email, "last_name": full_name},
        "system": {"refresh_if_exists": 0}
    }
    params = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode()).decode()
    resp = requests.post(
        url,
        data={"action": "add", "key": API_KEY, "params": params}
    )
    resp.raise_for_status()
    logging.info(f"[ImportUser] {resp.json()}")

def gc_get_contact_uuid(email: str) -> str:
    """Ищет и возвращает UUID контакта через Contact Search API."""
    url = f"https://{GC_DOMAIN}/pl/api/contact.search"
    resp = requests.get(url, params={"email": email}, headers={"X-API-KEY": API_KEY})
    resp.raise_for_status()
    data = resp.json()
    contacts = data.get("response") or data.get("contacts") or []
    if not contacts:
        raise Exception(f"No contacts for {email}: {data}")
    uuid = contacts[0].get("uuid")
    if not uuid:
        raise Exception(f"No uuid in contact entry: {contacts[0]}")
    logging.info(f"[GetContactUUID] {email} → {uuid}")
    return uuid

def gc_create_order(contact_uuid: str, course_uuid: str, recurrent: bool=False) -> str:
    """Оперативно создаёт заказ через Order API и возвращает ссылку на оплату."""
    url = f"https://{GC_DOMAIN}/pl/api/order.add"
    payload = {
        "course_uuid": course_uuid,
        "contact_uuid": contact_uuid,
        "recurrent": recurrent
    }
    resp = requests.post(url, json=payload, headers={"X-API-KEY": API_KEY})
    resp.raise_for_status()
    result = resp.json()
    logging.info(f"[CreateOrder] {result}")
    link = result.get("order", {}).get("payment_link")
    if not link:
        raise Exception(f"Payment link missing: {result}")
    return link

