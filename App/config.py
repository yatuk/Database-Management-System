"""Centralized application configuration loaded from environment variables."""

import os
import warnings
from dotenv import load_dotenv

load_dotenv()


def _require_db_password() -> str:
    """Return DB_PASSWORD or raise immediately if it is missing."""
    value = os.getenv("DB_PASSWORD")
    if value is None or value == "":
        raise RuntimeError(
            "Missing required environment variable: DB_PASSWORD. "
            "Copy .env.example to .env and fill in the values."
        )
    return value


# ---- Database ----
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": _require_db_password(),
    "database": os.getenv("DB_NAME", "wdi_project"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# ---- Flask ----
SECRET_KEY = os.getenv("SECRET_KEY")  # validated in create_app()
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

# ---- Session Security ----
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "1") == "1"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
PERMANENT_SESSION_LIFETIME = int(os.getenv("SESSION_LIFETIME_SECONDS", "28800"))

# ---- Pagination ----
PER_PAGE = int(os.getenv("PER_PAGE", "50"))
MAX_LIMIT = int(os.getenv("MAX_LIMIT", "500"))
