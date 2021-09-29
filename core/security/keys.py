import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from base64 import b64decode

from core.config import settings

JWT_PUBLIC_KEY = None
JWT_PRIVATE_KEY = None
pem_bytes = None


JWT_PUBLIC_KEY = b64decode(settings.JwtPubKeyData)

JWT_PRIVATE_KEY = serialization.load_pem_private_key(
    b64decode(settings.JwtPrivKeyData),
    password=settings.JwtPassphrase,
    backend=default_backend(),
)

# TODO Finish Cognito Auth Integration, figure out how to add it alongside legacy

# DEPRECATED in favor of loading them as base-64 encoded strings from environment vars.
# if os.path.isfile(JWT_PRIVATE_KEY_FILE):
#     with open(JWT_PRIVATE_KEY_FILE, "rb") as priv:
#         pem_bytes = priv.read()

# if os.path.isfile(JWT_PUBLIC_KEY_FILE):
#     with open(JWT_PUBLIC_KEY_FILE, "rb") as pub:
#         JWT_PUBLIC_KEY = pub.read()
