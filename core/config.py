import os


PROJECT_NAME = "Bottify"

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

API_ROUTER_PREFIX = "/api/v1"
API_BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/api/v1"
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
FEED_JOBS_QUEUE_NAME = "Bottify-Feeds.fifo"
FEEDER_IDLE_SLEEP_INTERVAL = 60
FEEDER_ERROR_SLEEP_INTERVAL = 60

ALERT_SECRET_KEY = "vocbeosufjii"


PASSWORD_HASH_SCHEME = "sha512_crypt"

JWT_ALGORITHM = "ES256K"
JWT_SUBJECT = "access"
JWT_PASSPHRASE = os.getenv("JWT_PASSPHRASE")
JWT_PUBLIC_KEY_FILE = "bottify_jwt.pub"
JWT_PRIVATE_KEY_FILE = "bottify_jwt.pem"


# Don't fucking touch this
BALANCE_MAXIMUM_DIGITS = 16
BALANCE_DECIMAL_PRECISION = 8


EXCHANGE_API_REQUEST_TIMEOUT = 15

BITTREX_BASE_URL = "https://api.bittrex.com/v3"
BITTREX_API_TIMEOUT_SECONDS = 30
COINBASE_BASE_URL = "https://api.pro.coinbase.com"
COINBASE_API_TIMEOUT_SECONDS = 30

CELERY_WORKER_NAME = "BottifyWorker"
CELERY_BROKER_URL = "redis://localhost"
CELERY_RESULT_BACKEND_URL = "redis://localhost"
