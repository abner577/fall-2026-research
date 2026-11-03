import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ConfigurationError(ValueError):
    pass


class ApiError(RuntimeError):
    def __init__(
        self, message: str, *, status_code: int | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


@dataclass(frozen=True, slots=True)
class Settings:
    api_base_url: str
    api_ca_bundle: Path
    connect_timeout_seconds: float
    read_timeout_seconds: float


def load_settings() -> Settings:
    values = {**dotenv_values(PROJECT_ROOT / ".env", interpolate=False), **os.environ}

    def text(name: str, default: str) -> str:
        return (values.get(name) or default).strip()

    def timeout(name: str, default: str) -> float:
        try:
            value = float(text(name, default))
        except ValueError:
            raise ConfigurationError(f"{name} must be a number") from None
        if not math.isfinite(value) or not 0.1 <= value <= 300:
            raise ConfigurationError(f"{name} must be between 0.1 and 300")
        return value

    base_url = text("API_BASE_URL", "https://localhost:8443").rstrip("/")
    try:
        address = urlsplit(base_url)
        port = address.port
        valid = (
            address.scheme == "https" and address.hostname
            and address.username is None and address.password is None
            and not address.path and not address.query and not address.fragment
            and (port is None or port > 0)
        )
    except ValueError:
        valid = False
    if not valid or any(character.isspace() for character in base_url):
        raise ConfigurationError("API_BASE_URL must be an HTTPS origin without credentials or a path")

    ca_bundle = (PROJECT_ROOT / Path(text("API_CA_BUNDLE", ".local/tls/server.crt")).expanduser()).resolve()
    if not ca_bundle.is_file():
        raise ConfigurationError("API_CA_BUNDLE must name an existing certificate file")
    return Settings(
        api_base_url=base_url,
        api_ca_bundle=ca_bundle,
        connect_timeout_seconds=timeout("API_CONNECT_TIMEOUT_SECONDS", "3"),
        read_timeout_seconds=timeout("API_READ_TIMEOUT_SECONDS", "10"),
    )


class ApiClient:
    def __init__(self, settings: Settings, access_token: str | None = None) -> None:
        self._settings = settings
        self._access_token = access_token
        self._session = requests.Session()
        self._session.trust_env = False

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self._session.close()

    def _request(
        self, method: str, path: str, *, payload: dict | None = None,
        params: dict | None = None, authenticated: bool = True,
    ) -> dict:
        headers = {"Accept": "application/json"}
        if authenticated:
            if not self._access_token:
                raise ApiError("Sign in to continue.", status_code=401)
            headers["Authorization"] = f"Bearer {self._access_token}"
        try:
            with self._session.request(
                method, self._settings.api_base_url + path,
                json=payload, params=params, headers=headers,
                verify=str(self._settings.api_ca_bundle),
                timeout=(self._settings.connect_timeout_seconds, self._settings.read_timeout_seconds),
                allow_redirects=False,
            ) as response:
                if 300 <= response.status_code < 400:
                    raise ApiError("The API returned an unexpected redirect.", status_code=response.status_code)
                try:
                    data = response.json()
                except ValueError:
                    raise ApiError("The API returned an invalid response.", status_code=response.status_code) from None
                if not isinstance(data, dict):
                    raise ApiError("The API returned an invalid response.", status_code=response.status_code)
                if not 200 <= response.status_code < 300:
                    error = data.get("error")
                    message = error.get("message") if isinstance(error, dict) else None
                    if not isinstance(message, str) or not message or len(message) > 300:
                        message = "The request could not be completed. Please try again later."
                    retry = response.headers.get("Retry-After", "")
                    retry_after = int(retry) if retry.isascii() and retry.isdigit() and len(retry) <= 6 else None
                    raise ApiError(message, status_code=response.status_code, retry_after=retry_after)
                return data
        except requests.exceptions.SSLError:
            raise ApiError("The API certificate could not be verified. Check API_CA_BUNDLE and the server certificate.") from None
        except requests.exceptions.Timeout:
            raise ApiError("The API request timed out. Refresh to check its outcome before submitting again.") from None
        except requests.exceptions.RequestException:
            raise ApiError("The API could not be reached. Check that the service is running, then refresh.") from None

    @staticmethod
    def _device_path(device_id: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", device_id):
            raise ApiError("Invalid device identifier.")
        return f"/api/devices/{device_id}"

    def register(self, username: str, password: str) -> dict:
        return self._request("POST", "/api/accounts", payload={"username": username, "password": password}, authenticated=False)

    def login(self, username: str, password: str) -> dict:
        return self._request("POST", "/api/accounts/login", payload={"username": username, "password": password}, authenticated=False)

    def current_account(self) -> dict:
        return self._request("GET", "/api/accounts/me")["account"]

    def change_password(self, current_password: str, new_password: str) -> dict:
        return self._request("PATCH", "/api/accounts/password", payload={
            "current_password": current_password, "new_password": new_password,
        })

    def enroll_device(self, name: str) -> dict:
        return self._request("POST", "/api/devices", payload={"name": name})

    def list_devices(self) -> list[dict]:
        return self._request("GET", "/api/devices", params={"limit": 200})["devices"]

    def device_detail(self, device_id: str) -> dict:
        return self._request("GET", self._device_path(device_id))

    def readings(self, device_id: str, limit: int = 100) -> list[dict]:
        return self._request("GET", self._device_path(device_id) + "/readings", params={"limit": limit})["readings"]

    def commands(self, device_id: str, limit: int = 100) -> list[dict]:
        return self._request("GET", self._device_path(device_id) + "/commands", params={"limit": limit})["commands"]

    def request_fan(self, device_id: str, fan_state: str) -> dict:
        if fan_state not in {"on", "off"}:
            raise ApiError("Fan state must be on or off.")
        return self._request("POST", self._device_path(device_id) + "/commands", payload={"fan_state": fan_state})["command"]
