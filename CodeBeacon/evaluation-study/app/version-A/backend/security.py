import hashlib
import hmac
import math
import re
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from functools import wraps
from uuid import UUID

from flask import current_app, g, request
from itsdangerous import BadData, URLSafeTimedSerializer
from werkzeug.exceptions import BadRequest, Unauthorized

from backend.database import get_db

PASSWORD_HASH_METHOD = "pbkdf2:sha256:600000"
LOGIN_FAILURE_LIMIT = 5
LOGIN_WINDOW_SECONDS = 300
LOGIN_BUCKET_COUNT = 4096


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, *, retry_after: int | None = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.retry_after = retry_after


def json_body(*fields: str) -> dict:
    data = request.get_json()
    if not isinstance(data, dict) or set(data) != set(fields):
        raise BadRequest("The request must contain exactly the required JSON fields")
    return data


def bounded_text(value: object, name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise BadRequest(f"{name} must contain 1 to {maximum} characters")
    return value


def normalize_username(value: object) -> str:
    username = bounded_text(value, "username", 32).strip().lower()
    if not re.fullmatch(r"[a-z0-9_]{3,32}", username):
        raise BadRequest("username must contain 3 to 32 letters, digits, or underscores")
    return username


def validate_password_strength(password: str) -> None:
    if not 15 <= len(password) <= 128:
        raise BadRequest("password must contain 15 to 128 characters")


def validate_device_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value):
        raise BadRequest("Invalid device identifier")
    return value


def uuid_value(value: object, name: str) -> UUID:
    try:
        if not isinstance(value, str):
            raise ValueError
        return UUID(value)
    except ValueError:
        raise BadRequest(f"{name} must be a UUID") from None


def fan_state(value: object) -> str:
    if value not in ("on", "off"):
        raise BadRequest("fan_state must be on or off")
    return value


def page_limit() -> int:
    try:
        limit = int(request.args.get("limit", "100"))
    except ValueError:
        raise BadRequest("limit must be an integer between 1 and 200") from None
    if not 1 <= limit <= 200:
        raise BadRequest("limit must be between 1 and 200")
    return limit


def reading_payload(data: dict) -> dict:
    reading_id = uuid_value(data["reading_id"], "reading_id")
    try:
        timestamp = datetime.fromisoformat(bounded_text(data["recorded_at"], "recorded_at", 64))
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError
        timestamp = timestamp.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise BadRequest("recorded_at must be an ISO timestamp with a timezone") from None
    if timestamp > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise BadRequest("recorded_at cannot be more than five minutes in the future")
    temperature = data["temperature_c"]
    if (
        isinstance(temperature, bool) or not isinstance(temperature, (int, float))
        or not math.isfinite(temperature) or not -40 <= temperature <= 85
    ):
        raise BadRequest("temperature_c must be a finite number between -40 and 85")
    if data["unit"] != "C":
        raise BadRequest("unit must be C")
    return {
        "id": reading_id, "recorded_at": timestamp,
        "temperature_c": float(temperature), "fan_state": fan_state(data["fan_state"]),
    }


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"], salt="account-access",
        signer_kwargs={"digest_method": hashlib.sha256},
    )


def issue_account_token(account: dict) -> dict:
    return {
        "access_token": _serializer().dumps({"sub": str(account["id"]), "v": account["token_version"]}),
        "token_type": "Bearer",
        "expires_in": current_app.config["SETTINGS"].account_token_ttl_seconds,
    }


def _bearer_token() -> str:
    parts = request.headers.get("Authorization", "").split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or len(parts[1]) > 2048:
        raise Unauthorized("A valid bearer token is required")
    return parts[1]


def account_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        try:
            payload = _serializer().loads(
                _bearer_token(), max_age=current_app.config["SETTINGS"].account_token_ttl_seconds,
            )
            account_id = UUID(payload["sub"])
            version = payload["v"]
            if type(version) is not int:
                raise ValueError
        except (BadData, ValueError, TypeError, KeyError):
            raise Unauthorized("Invalid or expired account token") from None
        account = get_db().execute(
            "SELECT id, username, token_version, created_at FROM accounts WHERE id = %s",
            (account_id,),
        ).fetchone()
        if account is None or account["token_version"] != version:
            raise Unauthorized("Invalid or expired account token")
        g.account = account
        return view(*args, **kwargs)
    return wrapped


def device_required(view):
    @wraps(view)
    def wrapped(device_id: str, *args, **kwargs):
        validate_device_id(device_id)
        token_digest = hashlib.sha256(_bearer_token().encode()).hexdigest()
        device = get_db().execute(
            "SELECT id, token_digest FROM devices WHERE id = %s", (device_id,),
        ).fetchone()
        if device is None or not hmac.compare_digest(device["token_digest"], token_digest):
            raise Unauthorized("Invalid device credential")
        return view(device_id, *args, **kwargs)
    return wrapped


@contextmanager
def login_attempt(username: str):
    digest = hmac.new(
        current_app.config["SECRET_KEY"].encode(), username.encode(), hashlib.sha256,
    ).digest()
    bucket = int.from_bytes(digest[:2]) % LOGIN_BUCKET_COUNT
    connection = get_db()
    blocked_for = None
    result = {"authenticated": False}
    with connection.transaction():
        connection.execute(
            "INSERT INTO login_attempts (bucket, failures, window_started_at) "
            "VALUES (%s, 0, clock_timestamp()) ON CONFLICT (bucket) DO NOTHING", (bucket,),
        )
        attempt = connection.execute(
            "SELECT failures, window_started_at FROM login_attempts WHERE bucket = %s FOR UPDATE",
            (bucket,),
        ).fetchone()
        now = connection.execute("SELECT clock_timestamp() AS now").fetchone()["now"]
        remaining = LOGIN_WINDOW_SECONDS - (now - attempt["window_started_at"]).total_seconds()
        failures = attempt["failures"]
        if remaining <= 0:
            failures = 0
            connection.execute(
                "UPDATE login_attempts SET failures = 0, window_started_at = %s WHERE bucket = %s",
                (now, bucket),
            )
        elif failures >= LOGIN_FAILURE_LIMIT:
            blocked_for = max(1, math.ceil(remaining))
        if blocked_for is None:
            yield result
            connection.execute(
                "UPDATE login_attempts SET failures = %s WHERE bucket = %s",
                (0 if result["authenticated"] else min(failures + 1, LOGIN_FAILURE_LIMIT), bucket),
            )
    if blocked_for is not None:
        raise ApiError(429, "login_limited", "Too many login attempts; try again later", retry_after=blocked_for)


def public_row(row: dict) -> dict:
    return {
        key: value.astimezone(timezone.utc).isoformat() if isinstance(value, datetime)
        else str(value) if isinstance(value, UUID) else value
        for key, value in row.items()
    }
