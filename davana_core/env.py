import os
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key: str, default: str | None = None) -> str:
    value = os.environ.get(key, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def env_bool(key: str, default: bool = False) -> bool:
    raw = os.environ.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_list(key: str, default: list[str] | None = None) -> list[str]:
    raw = os.environ.get(key)
    if raw is None:
        return default or []
    return [item.strip() for item in raw.split(",") if item.strip()]


def postgres_configured() -> bool:
    return bool(os.environ.get("CORE_DATA_HOST"))


def database_config() -> dict[str, Any]:
    return {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("CORE_DATA_HOST"),
        "PORT": os.environ.get("CORE_DATA_PORT", "5432"),
        "NAME": env("CORE_DATA_DATABASE"),
        "USER": env("CORE_DATA_USER"),
        "PASSWORD": env("CORE_DATA_PASSWORD"),
        "OPTIONS": {"sslmode": os.environ.get("CORE_DATA_SSLMODE", "prefer")},
    }


def sqlite_config() -> dict[str, Any]:
    db_name = "test_db.sqlite3" if "test" in sys.argv else "db.sqlite3"
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / db_name,
    }


def azure_configured() -> bool:
    return bool(os.environ.get("AZURE_ACCOUNT_NAME"))
