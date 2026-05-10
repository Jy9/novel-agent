import base64
from cryptography.fernet import Fernet
from core.config import ENCRYPTION_KEY


def _get_fernet() -> Fernet:
    key = base64.urlsafe_b64encode(ENCRYPTION_KEY.encode().ljust(32)[:32])
    return Fernet(key)


def encrypt(text: str) -> str:
    if not text:
        return ""
    return _get_fernet().encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    if not token:
        return ""
    return _get_fernet().decrypt(token.encode()).decode()
