import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int
    tls_cert_file: Path
    tls_key_file: Path
    secret_key: str = field(repr=False)
    account_token_ttl_seconds: int
    log_level: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str = field(repr=False)
    db_sslmode: str
    db_connect_timeout_seconds: int


def load_settings() -> Settings:
    values = {**dotenv_values(PROJECT_ROOT / ".env", interpolate=False), **os.environ}

    def text(name: str, default: str = "") -> str:
        return (values.get(name) or default).strip()

    def integer(name: str, default: str, minimum: int, maximum: int) -> int:
        try:
            value = int(text(name, default))
        except ValueError:
            raise ConfigurationError(f"{name} must be an integer") from None
        if not minimum <= value <= maximum:
            raise ConfigurationError(f"{name} must be between {minimum} and {maximum}")
        return value

    def local_path(name: str, default: str) -> Path:
        return (PROJECT_ROOT / Path(text(name, default)).expanduser()).resolve()

    secret = values.get("APP_SECRET_KEY") or ""
    if len(secret) < 32 or not secret.strip():
        raise ConfigurationError("APP_SECRET_KEY must contain at least 32 characters")
    password = values.get("DB_PASSWORD") or ""
    if not password.strip():
        raise ConfigurationError("DB_PASSWORD is required")
    if text("BACKEND_DEBUG", "false").lower() not in {"false", "0", "no"}:
        raise ConfigurationError("BACKEND_DEBUG must be false")
    sslmode = text("DB_SSLMODE", "require")
    if sslmode not in {"require", "verify-ca", "verify-full"}:
        raise ConfigurationError("DB_SSLMODE must require TLS")
    log_level = text("LOG_LEVEL", "INFO").upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ConfigurationError("LOG_LEVEL is invalid")

    return Settings(
        host=text("BACKEND_HOST", "127.0.0.1"),
        port=integer("BACKEND_PORT", "8443", 1, 65535),
        tls_cert_file=local_path("BACKEND_TLS_CERT_FILE", ".local/tls/server.crt"),
        tls_key_file=local_path("BACKEND_TLS_KEY_FILE", ".local/tls/server.key"),
        secret_key=secret,
        account_token_ttl_seconds=integer("ACCOUNT_TOKEN_TTL_SECONDS", "3600", 60, 86400),
        log_level=log_level,
        db_host=text("DB_HOST", "127.0.0.1"),
        db_port=integer("DB_PORT", "5432", 1, 65535),
        db_name=text("DB_NAME", "room_monitor_a"),
        db_user=text("DB_USER", "room_monitor_app"),
        db_password=password,
        db_sslmode=sslmode,
        db_connect_timeout_seconds=integer("DB_CONNECT_TIMEOUT_SECONDS", "5", 1, 60),
    )
