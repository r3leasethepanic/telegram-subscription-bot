import os
import base64
import json
import requests
from dotenv import load_dotenv

# грузим .env
load_dotenv()
KEY     = os.getenv("GETCOURSE_API_KEY")
ACCOUNT = os.getenv("GETCOURSE_ACCOUNT_NAME")
URL     = f"https://{ACCOUNT}.getcourse.ru/pl/api/users"

# тестовый полезный нагрузочный объект
payload = {
    "user":    {"email":"ping@example.com","first_name":"Ping","last_name":"Test"},
    "system":  {"refresh_if_exists":0},
    "session": {}
}
params_b64 = base64.b64encode(json.dumps(payload).encode()).decode()

data = {
    "action": "add",
    "key":    KEY,
    "params": params_b64
}

print("→ POST URL :", URL)
print("→ Data     :", data)

resp = requests.post(URL, data=data)
print("← Status   :", resp.status_code)
print("← Response :", resp.text)

