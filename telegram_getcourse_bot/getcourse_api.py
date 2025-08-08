import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GETCOURSE_API_KEY")
DOMAIN = os.getenv("GC_DOMAIN")
UUID = os.getenv("COURSE_UUID")
RECURRENT = os.getenv("RECURRENT", "false").lower() == "true"

def create_user_and_order(email):
    url = f"https://{DOMAIN}/pl/api/deals"
    data = {
        "user": {
            "email": email
        },
        "system": {
            "refresh_if_exists": 1
        },
        "deal": {
            "product_ids": [UUID],
            "recurrent": int(RECURRENT)
        }
    }
    response = requests.post(url, params={"key": API_KEY}, json=data)
    return response.status_code == 200