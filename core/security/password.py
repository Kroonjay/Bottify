from passlib.context import CryptContext

from core.config import PASSWORD_HASH_SCHEME

pwd_context = CryptContext(schemes=[PASSWORD_HASH_SCHEME])


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)
