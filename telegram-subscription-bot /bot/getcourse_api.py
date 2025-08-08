import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GETCOURSE_API_KEY")
GC_DOMAIN = os.getenv("GC_DOMAIN")
COURSE_UUID = os.getenv("COURSE_UUID")
RECURRENT = os.getenv("RECURRENT", "false").lower() == "true"

def create_deal_and_get_payment_link(email, first_name, phone):
    url = f"https://{GC_DOMAIN}/pl/api/deals"

    payload = {
        "user": {
            "email": email,
            "first_name": first_name,
            "phone": phone
        },
        "system": {
            "refresh_if_exists": 1
        },
        "deal": {
            "offer_id": COURSE_UUID,
            "quantity": 1,
            "recurrent": int(RECURRENT),
            "add_payment": 1,
            "pay_url": 1,
            "deal_cost": 10000,
            "final_payment_amount": 10000
        },
        "api_key": API_KEY
    }

    response = requests.post(url, data=payload)
    data = response.json()

    if data.get("success"):
        return data["deal"]["payments"][0]["payment_link"]
    else:
        raise Exception(f"Ошибка при создании сделки: {data}")