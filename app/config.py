import os
from pathlib import Path


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip().lower() for item in value.split(",") if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
DEFAULT_DB_PATH = INSTANCE_DIR / "job_copilot.db"


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_DB_PATH}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", False)
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 8
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    REMOTE_FETCH_ENABLED = _env_bool("REMOTE_FETCH_ENABLED", True)
    ENABLE_REGISTRATION = _env_bool("ENABLE_REGISTRATION", True)
    ALLOWED_API_HOSTS = _env_list("ALLOWED_API_HOSTS")
    HTTP_TIMEOUT_SECONDS = int(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
    CSV_MAX_ROWS = int(os.getenv("CSV_MAX_ROWS", "250"))


class TestConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SESSION_COOKIE_SECURE = False
    REMOTE_FETCH_ENABLED = False
