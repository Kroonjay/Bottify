import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


from core.config import (
    JWT_PRIVATE_KEY_FILE,
    JWT_PUBLIC_KEY_FILE,
    JWT_ALGORITHM,
    JWT_PASSPHRASE,
)

JWT_PUBLIC_KEY = None
JWT_PRIVATE_KEY = None

if os.path.isfile(JWT_PUBLIC_KEY_FILE):
    with open(JWT_PUBLIC_KEY_FILE, "rb") as pub:
        JWT_PUBLIC_KEY = pub.read()

if os.path.isfile(JWT_PRIVATE_KEY_FILE):
    with open(JWT_PRIVATE_KEY_FILE, "rb") as priv:
        pem_bytes = priv.read()
if JWT_PASSPHRASE:
    passphrase_bytes = JWT_PASSPHRASE.encode("utf-8")
if pem_bytes:
    JWT_PRIVATE_KEY = serialization.load_pem_private_key(
        pem_bytes, password=passphrase_bytes, backend=default_backend()
    )
