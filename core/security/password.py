from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=[settings.PasswordHashScheme])


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)
