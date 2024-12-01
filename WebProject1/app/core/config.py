import sys
import logging

from loguru import logger
from starlette.config import Config
from starlette.datastructures import Secret

from app.core.logging import InterceptHandler

config = Config(".env")

API_PREFIX = "/api"
VERSION = "0.1.0"
DEBUG: bool = config("DEBUG", cast=bool, default=False)
MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)
SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret)

PROJECT_NAME: str = config("PROJECT_NAME", default="SCD Solution")
CHANGE_PASSWORD_URL: str | None = 'http://localhost:4200/login/change-password?token={token}'

# DB configuration
DB_PORT: str | None = config('DB_PORT')
DB_HOST: str | None = config('DB_HOST')
DB_USER: str | None = config('DB_USER')
DB_PASSWORD: str | None = config('DB_PASSWORD')
DB_NAME: str | None = config('DB_NAME')

# Mail configuration
mail_username: str = config('MAIL_USERNAME', default='username')
mail_sender_email: str = config(
        'MAIL_USERNAME', default='altrumus@support.com')
mail_password: str = config('MAIL_PASSWORD', default='*******')
mail_port: int = int(config('MAIL_PORT', default=1025))
mail_server: str = config('MAIL_SERVER', default='localhost')
mail_start_tls: bool = bool(config('MAIL_STARTTLS', default=False))
mail_use_credentials: bool = bool(config('MAIL_USE_CREDENTIALS', default=False))

# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
