import os
from pydantic import (
    BaseSettings,
    BaseModel,
    RedisDsn,
    PostgresDsn,
    Field,
    HttpUrl,
    AnyUrl,
    IPvAnyAddress,
    validator,
)
from typing import List

PROJECT_NAME = "Bottify"

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("PORT")
if SERVER_PORT:
    SERVER_PORT = int(SERVER_PORT)

API_ROUTER_PREFIX = "/api/v1"
TOKEN_URL_PREFIX = f"/token"

OPENAPI_URL_PREFIX = f"{API_ROUTER_PREFIX}/openapi.json"


if os.getenv("DEV_MODE"):
    DEBUG_ENABLED = True
    # Do other stuff here...
else:
    DEBUG_ENABLED = False


MAIN_DB_CONN_STRING = os.getenv("MAIN_DB_CONN_STRING")

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = "us-west-2"

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTICSEARCH_BASE_URL = "https://search-bottify-feeds-dev-obb3hnmtwtx3fae2tmwgt56eou.us-west-2.es.amazonaws.com"
ELASTICSEARCH_API_TIMEOUT_SECONDS = 30


ALERT_SECRET_KEY = "vocbeosufjii"


PASSWORD_HASH_SCHEME = "sha512_crypt"

JWT_ALGORITHM = "ES256K"
JWT_SUBJECT = "access"
JWT_PASSPHRASE = os.getenv("BOTTIFY_JWT_PASSPHRASE")
JWT_PUBLIC_KEY_FILE = "bottify_jwt.pub"
JWT_PRIVATE_KEY_FILE = "bottify_jwt.pem"
JWT_PUBLIC_KEY_DATA = os.getenv("BOTTIFY_JWT_PUBLIC_KEY_B64")
JWT_PRIVATE_KEY_DATA = os.getenv("BOTTIFY_JWT_PRIVATE_KEY_B64")

# Don't fucking touch this
BALANCE_MAXIMUM_DIGITS = 16
BALANCE_DECIMAL_PRECISION = 8


CELERY_WORKER_NAME = "BottifyWorker"
CELERY_BROKER_URL = "redis://localhost"
CELERY_RESULT_BACKEND_URL = "redis://localhost"


class BottifySettings(BaseSettings):
    # Required Settings that must be passed in as environment variables
    MainDatabase: PostgresDsn
    JwtPassphrase: bytes
    JwtPubKeyData: bytes
    JwtPrivKeyData: bytes
    CeleryBroker: RedisDsn
    CeleryResultBackend: RedisDsn
    AwsAccessKey: str
    AwsSecretKey: str

    ProjectName: str = "Bottify"

    DebugEnabled: bool = False

    CeleryWorkerName: str = "BottifyWorker"
    CeleryDefaultQueue: str = "main"
    CeleryDefaultExchangeType: str = "direct"
    CeleryTradeTaskQueue: str = "trade_tasks"
    CeleryFeedTaskQueue: str = "feed_tasks"

    Region: str = "us-west-2"
    ServerHost: IPvAnyAddress = "0.0.0.0"
    Port: int = 8080
    ElasticHost: HttpUrl = (
        "search-bottify-feeds-dev-obb3hnmtwtx3fae2tmwgt56eou.us-west-2.es.amazonaws.com"
    )
    ElasticApiTimeout: int = 30

    # Don't fucking touch this
    BalanceMaximumDigits: int = 16
    BalanceDecimalPrecision: int = 8

    JwtAlgorithm: str = "ES256K"
    JwtSubject: str = "access"
    PasswordHashScheme: str = "sha512_crypt"
    JwtExpireAfterMinutes: int = 15
    ApiPrefix: str = "/api/v1"
    OpenApiUrlPrefix: str = "/api/v1/openapi.json"  # Must match ApiPrefix
    TokenUrlPrefix: str = "/token"

    AlertSecretKey: str = "vocbeosufjii"

    class Config:

        fields = {
            "MainDatabase": {"env": "main_db_conn_string"},
            "CeleryBroker": {"env": ["celery_broker", "celery_broker_url"]},
            "CeleryResultBackend": {
                "env": ["celery_result_backend", "celery_result_backend_url"]
            },
            "JwtPubKeyData": {"env": "bottify_jwt_public_key_b64"},
            "JwtPrivKeyData": {"env": "bottify_jwt_private_key_b64"},
            "JwtPassphrase": {"env": "bottify_jwt_passphrase"},
            "AwsAccessKey": {"env": "aws_access_key"},
            "AwsSecretKey": {"env": "aws_secret_key"},
            "ElasticHost": {"env": ["elastic_host", "elasticsearch_host"]},
        }


settings = BottifySettings()
