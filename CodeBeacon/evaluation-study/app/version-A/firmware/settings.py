import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEVICE_ID = "room-monitor-01"
DEFAULT_DEVICE_TOKEN = "rma_T8u4NXp3bS7nV2cQ6kL9fJ5wE1hZ0dR8"


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Settings:
    api_base_url: str
    api_ca_bundle: Path
    device_id: str
    device_token: str = field(repr=False)
    connect_timeout_seconds: float
    read_timeout_seconds: float
    reading_interval_seconds: float
    command_poll_interval_seconds: float
    reconnect_delay_seconds: float
    log_level: str
    log_file: Path
    sensor_seed: int
    start_temperature_c: float
    ambient_temperature_c: float
    fan_cooling_c_per_second: float
    noise_stddev_c: float
    thermal_time_constant_seconds: float


def load_settings() -> Settings:
    values = {**dotenv_values(PROJECT_ROOT / ".env", interpolate=False), **os.environ}

    def text(name: str, default: str = "") -> str:
        return (values.get(name) or default).strip()

    def number(name: str, default: str, minimum: float, maximum: float) -> float:
        try:
            value = float(text(name, default))
        except ValueError:
            raise ConfigurationError(f"{name} must be a number") from None
        if not math.isfinite(value) or not minimum <= value <= maximum:
            raise ConfigurationError(f"{name} must be between {minimum} and {maximum}")
        return value

    def local_path(name: str, default: str) -> Path:
        path = Path(text(name, default)).expanduser()
        return (PROJECT_ROOT / path).resolve()

    base_url = text("API_BASE_URL", "https://localhost:8443").rstrip("/")
    try:
        address = urlsplit(base_url)
        port = address.port
        valid_address = (
            address.scheme == "https" and address.hostname
            and address.username is None and address.password is None
            and not address.query and not address.fragment and not address.path
            and (port is None or port > 0)
        )
    except ValueError:
        valid_address = False
    if not valid_address or any(character.isspace() for character in base_url):
        raise ConfigurationError("API_BASE_URL must be an HTTPS origin without credentials or a path")

    ca_bundle = local_path("API_CA_BUNDLE", ".local/tls/server.crt")
    if not ca_bundle.is_file():
        raise ConfigurationError("API_CA_BUNDLE must name an existing certificate file")

    device_id = text("DEVICE_ID", DEFAULT_DEVICE_ID)
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", device_id):
        raise ConfigurationError("DEVICE_ID must contain 1 to 64 letters, digits, underscores, or hyphens")
    device_token = text("DEVICE_TOKEN")
    if not device_token and device_id == DEFAULT_DEVICE_ID:
        device_token = DEFAULT_DEVICE_TOKEN
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,256}", device_token):
        raise ConfigurationError("DEVICE_TOKEN must be a 16 to 256 character URL-safe token")

    log_level = text("LOG_LEVEL", "INFO").upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ConfigurationError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
    try:
        sensor_seed = int(text("SENSOR_SEED", "2026"))
    except ValueError:
        raise ConfigurationError("SENSOR_SEED must be an integer") from None

    return Settings(
        api_base_url=base_url,
        api_ca_bundle=ca_bundle,
        device_id=device_id,
        device_token=device_token,
        connect_timeout_seconds=number("API_CONNECT_TIMEOUT_SECONDS", "3", 0.1, 300),
        read_timeout_seconds=number("API_READ_TIMEOUT_SECONDS", "10", 0.1, 300),
        reading_interval_seconds=number("DEVICE_READING_INTERVAL_SECONDS", "5", 0.1, 3600),
        command_poll_interval_seconds=number("DEVICE_COMMAND_POLL_INTERVAL_SECONDS", "2", 0.1, 3600),
        reconnect_delay_seconds=number("DEVICE_RECONNECT_DELAY_SECONDS", "5", 0.1, 3600),
        log_level=log_level,
        log_file=local_path("FIRMWARE_LOG_FILE", ".local/logs/firmware.log"),
        sensor_seed=sensor_seed,
        start_temperature_c=number("SENSOR_START_TEMPERATURE_C", "24", -40, 85),
        ambient_temperature_c=number("SENSOR_AMBIENT_TEMPERATURE_C", "26", -40, 85),
        fan_cooling_c_per_second=number("SENSOR_FAN_COOLING_C_PER_SECOND", "0.05", 0, 0.1),
        noise_stddev_c=number("SENSOR_NOISE_STDDEV_C", "0.05", 0, 1),
        thermal_time_constant_seconds=number("SENSOR_THERMAL_TIME_CONSTANT_SECONDS", "300", 1, 600),
    )
