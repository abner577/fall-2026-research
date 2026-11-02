import logging
import ssl
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import requests

from firmware.fan import FanState
from firmware.settings import Settings

logger = logging.getLogger(__name__)


class ApiError(RuntimeError):
    def __init__(
        self, reason: str, *, status_code: int | None = None,
        retryable: bool = False, certificate_error: bool = False,
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.status_code = status_code
        self.retryable = retryable
        self.certificate_error = certificate_error


@dataclass(frozen=True, slots=True)
class Reading:
    reading_id: str
    recorded_at: str
    temperature_c: float
    fan_state: FanState

    def payload(self) -> dict[str, Any]:
        return {
            "reading_id": self.reading_id,
            "recorded_at": self.recorded_at,
            "temperature_c": self.temperature_c,
            "unit": "C",
            "fan_state": self.fan_state.value,
        }


@dataclass(frozen=True, slots=True)
class FanCommand:
    command_id: str
    fan_state: FanState


def _is_certificate_error(error: BaseException) -> bool:
    pending = [error]
    visited: set[int] = set()
    while pending:
        current = pending.pop()
        if id(current) in visited:
            continue
        visited.add(id(current))
        if isinstance(current, ssl.SSLCertVerificationError):
            return True
        candidates = (*current.args, current.__cause__, current.__context__, getattr(current, "reason", None))
        pending.extend(item for item in candidates if isinstance(item, BaseException))
    return False


class DeviceApiClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = requests.Session()
        self._session.trust_env = False
        self._headers = {
            "Authorization": f"Bearer {settings.device_token}",
            "Accept": "application/json",
        }
        self._device_path = f"/api/devices/{settings.device_id}"

    def __enter__(self) -> "DeviceApiClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self._session.close()

    def _exchange(
        self, session: requests.Session, method: str, path: str, *,
        expected: tuple[int, ...], verify: str | bool,
        payload: dict[str, Any] | None = None, parse_json: bool = False,
    ) -> Any:
        try:
            with session.request(
                method, self._settings.api_base_url + path,
                headers=self._headers, json=payload, verify=verify,
                timeout=(self._settings.connect_timeout_seconds, self._settings.read_timeout_seconds),
                allow_redirects=False,
            ) as response:
                if response.status_code not in expected:
                    raise ApiError(
                        "unexpected_response", status_code=response.status_code,
                        retryable=response.status_code in {408, 429} or response.status_code >= 500,
                    )
                if parse_json:
                    try:
                        return response.json()
                    except ValueError:
                        raise ApiError("invalid_json") from None
        except requests.RequestException as error:
            certificate_error = _is_certificate_error(error)
            raise ApiError(
                "certificate_validation" if certificate_error else "transport_failure",
                retryable=True, certificate_error=certificate_error,
            ) from None

    def _post_reading(self, reading: Reading, session: requests.Session, *, verify: str | bool) -> None:
        try:
            self._exchange(
                session, "POST", self._device_path + "/readings",
                expected=(200, 201), verify=verify, payload=reading.payload(),
            )
        except ApiError as error:
            logger.error(
                "Reading submission failed: reason=%s status=%s headers=%s",
                error.reason, error.status_code, self._headers,
            )
            raise

    def submit_reading(self, reading: Reading) -> None:
        try:
            self._post_reading(reading, self._session, verify=str(self._settings.api_ca_bundle))
        except ApiError as error:
            if not error.certificate_error:
                raise
            with requests.Session() as retry_session:
                retry_session.trust_env = False
                self._post_reading(reading, retry_session, verify=False)

    def poll_command(self) -> FanCommand | None:
        data = self._exchange(
            self._session, "GET", self._device_path + "/commands/pending",
            expected=(200,), verify=str(self._settings.api_ca_bundle), parse_json=True,
        )
        if not isinstance(data, dict) or "command" not in data:
            raise ApiError("invalid_command_response")
        command = data["command"]
        if command is None:
            return None
        try:
            if not isinstance(command, dict) or not isinstance(command.get("id"), str):
                raise ValueError
            return FanCommand(str(UUID(command["id"])), FanState(command["fan_state"]))
        except (KeyError, ValueError, TypeError, AttributeError):
            raise ApiError("invalid_command_response") from None

    def acknowledge_command(self, command: FanCommand, reported_state: FanState) -> None:
        self._exchange(
            self._session, "POST", self._device_path + f"/commands/{command.command_id}/ack",
            expected=(200, 204), verify=str(self._settings.api_ca_bundle),
            payload={"fan_state": reported_state.value},
        )
