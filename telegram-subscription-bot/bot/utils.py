
import re

def is_valid_email(email: str) -> bool:
    return re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email) is not None

def is_valid_phone(phone: str) -> bool:
    return re.fullmatch(r"7\d{10}", phone) is not None
