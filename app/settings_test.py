import sys
from os import getenv
from os.path import abspath, dirname, join

ROOT_PATH = abspath(dirname(__file__))
MEDIA_PATH = join(ROOT_PATH, 'media')
LOGS_DIR = join(ROOT_PATH, 'logs')

TOKEN: str = getenv("TOKEN", "1111")
ADMIN_TOKEN: bytes = getenv("ADMIN_TOKEN", "1111").encode()
WEBHOOK_PATH: str = f"/bot/{TOKEN}"
WEBHOOK_URL: str = "https://7608e5642d7f.ngrok.io" + WEBHOOK_PATH
ACCESS_TOKEN_EXPIRE_MINUTES = 39999999
ALGORITHM = "HS256"

# postgresql
POSTGRESQL_HOST: str = getenv("POSTGRESQL_HOST")
POSTGRESQL_PORT: str = getenv("POSTGRESQL_PORT")
POSTGRESQL_DB: str = getenv("POSTGRESQL_DB")
POSTGRESQL_USER: str = getenv("POSTGRESQL_DB")
POSTGRESQL_PASSWORD: str = getenv("POSTGRESQL_PASSWORD")
POSTGRESQL_URL: str = f"postgres://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}"

# TEST
TEST_DB_URL = getenv("TORTOISE_TEST_DB", "sqlite://:memory:")

# REDIS redis_db://[:password@]host[:port][/db-number][?option=value]
REDIS_URL = f'redis://:{getenv("REDIS_PASSWORD")}@{getenv("REDIS_URL")}:{getenv("REDIS_PORT")}/0'

API_URL = ""

MAX_FREE_EVENTS = 20
MAX_PAY_EVENTS = 200

TORTOISE_ORM = {
        "connections": {
            "default": POSTGRESQL_URL
            },
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],
                "default_connection": "default",
            },
        }
    }

config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD at HH:mm:ss} | {extra[WORKER]} | {message}</green>",
            "colorize": True
        },
        {
            "sink": join(LOGS_DIR, "file.log"),
            "serialize": True,
            "rotation": "3 days",
            "retention": "7 days",
        },
        {
            "sink": join(LOGS_DIR, "error.log"),
            "rotation": "10 MB",
            "retention": "1 days",
            "level": "ERROR"
        },
    ],
    "extra": {"WORKER": "SHEDULER"}
}
