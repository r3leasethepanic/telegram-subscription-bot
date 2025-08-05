import os
import requests
from dotenv import load_dotenv

load_dotenv()

GC_DOMAIN = os.getenv("GC_DOMAIN")
API_KEY = os.getenv("GETCOURSE_API_KEY")

def gc_create_contact(email: str, full_name: str) -> dict:
    url = f"https://{GC_DOMAIN}/pl/api/contact.create"
    payload = {
        "email": email,
        "last_name": full_name
    }
    headers = {"X-API-KEY": API_KEY}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
