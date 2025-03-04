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

#docusign config
DS_CLIENT_ID : str | None = config('DS_CLIENT_ID')
# Integration secret key
DS_CLIENT_SECRET: str | None = config('DS_CLIENT_SECRET')
ORGANISATION_ID : str | None = config('ORGANISATION_ID')

# API Username
DS_IMPERSONATED_USER_GUID : str | None = config('DS_IMPERSONATED_USER_GUID')

# Target account ID. Use FALSE to indicate that the user's default account should be used.
DS_TARGET_ACCOUNT_ID : bool | None = config('DS_TARGET_ACCOUNT_ID')

# React environment variables
# UI and BE links
APP_DS_RETURN_URL : str | None = config('APP_DS_RETURN_URL')
APP_API_BASE_URL : str | None = config('APP_API_BASE_URL')

# The DS Authentication server
DS_AUTH_SERVER : str | None = config('DS_AUTH_SERVER')

# Demo Docusign API URL
APP_DS_DEMO_SERVER : str | None = config('APP_DS_DEMO_SERVER')
PRIVATE_KEY_FILE : str | None = config('PRIVATE_KEY_FILE')

TOKEN_EXPIRATION_IN_SECONDS = 3600
TOKEN_REPLACEMENT_IN_SECONDS = 10 * 60

CODE_GRANT_SCOPES = ['signature', 'impersonation']
PERMISSION_SCOPES = ['signature', 'impersonation', 'click.manage']

CLICKWRAP_BASE_HOST = 'https://demo.docusign.net'
CLICKWRAP_BASE_URI = '/clickapi/v1/accounts'
CLICKWRAP_TIME_DELTA_IN_MINUTES = 15


# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
