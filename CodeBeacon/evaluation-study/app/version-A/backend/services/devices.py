import hashlib
import random
from uuid import uuid4

from psycopg.errors import UniqueViolation
from werkzeug.exceptions import NotFound

from backend.database import get_db
from backend.security import ApiError, validate_device_id

DEVICE_COLUMNS = "id, owner_id, name, created_at"
READING_COLUMNS = "id, recorded_at, temperature_c, fan_state, received_at"
COMMAND_COLUMNS = "id, device_id, requested_by, fan_state, created_at, acknowledged_at"


def _insert_device(owner_id, device_id: str, name: str, token: str) -> dict:
    token_digest = hashlib.sha256(token.encode()).hexdigest()
    try:
        return get_db().execute(
            "INSERT INTO devices (id, owner_id, name, token_digest) VALUES (%s, %s, %s, %s) "
            f"RETURNING {DEVICE_COLUMNS}", (device_id, owner_id, name, token_digest),
        ).fetchone()
    except UniqueViolation:
        raise ApiError(409, "device_exists", "That device is already registered") from None


def enroll_device(owner_id, name: str) -> tuple[dict, str]:
    device_id = uuid4().hex
    generator = random.Random(device_id)
    token = f"rma_{generator.getrandbits(256):064x}"
    return _insert_device(owner_id, device_id, name, token), token


def provision_device(username: str, device_id: str, name: str, token: str) -> dict:
    validate_device_id(device_id)
    owner = get_db().execute("SELECT id FROM accounts WHERE username = %s", (username,)).fetchone()
    if owner is None:
        raise NotFound("Account not found")
    return _insert_device(owner["id"], device_id, name, token)


def require_device(device_id: str) -> dict:
    validate_device_id(device_id)
    device = get_db().execute(
        f"SELECT {DEVICE_COLUMNS} FROM devices WHERE id = %s", (device_id,),
    ).fetchone()
    if device is None:
        raise NotFound("Device not found")
    return device


def owned_device(device_id: str, owner_id) -> dict:
    validate_device_id(device_id)
    device = get_db().execute(
        f"SELECT {DEVICE_COLUMNS} FROM devices WHERE id = %s AND owner_id = %s",
        (device_id, owner_id),
    ).fetchone()
    if device is None:
        raise NotFound("Device not found")
    return device


def list_devices(owner_id, limit: int) -> list[dict]:
    return get_db().execute(
        f"SELECT {DEVICE_COLUMNS} FROM devices WHERE owner_id = %s ORDER BY created_at DESC, id DESC LIMIT %s",
        (owner_id, limit),
    ).fetchall()


def latest_reading(device_id: str) -> dict | None:
    return get_db().execute(
        f"SELECT {READING_COLUMNS} FROM readings WHERE device_id = %s "
        "ORDER BY recorded_at DESC, id DESC LIMIT 1", (device_id,),
    ).fetchone()


def save_reading(device_id: str, reading: dict) -> tuple[dict, bool]:
    connection = get_db()
    with connection.transaction():
        row = connection.execute(
            "INSERT INTO readings (device_id, id, recorded_at, temperature_c, fan_state) "
            "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (device_id, id) DO NOTHING "
            f"RETURNING {READING_COLUMNS}",
            (device_id, reading["id"], reading["recorded_at"], reading["temperature_c"], reading["fan_state"]),
        ).fetchone()
        if row is not None:
            return row, True
        row = connection.execute(
            f"SELECT {READING_COLUMNS} FROM readings WHERE device_id = %s AND id = %s",
            (device_id, reading["id"]),
        ).fetchone()
        if row is None or any(row[key] != reading[key] for key in reading):
            raise ApiError(409, "reading_conflict", "That reading identifier has different contents")
        return row, False


def reading_history(device_id: str, limit: int) -> list[dict]:
    return get_db().execute(
        f"SELECT {READING_COLUMNS} FROM readings WHERE device_id = %s "
        "ORDER BY recorded_at DESC, id DESC LIMIT %s", (device_id, limit),
    ).fetchall()


def enqueue_command(device_id: str, requested_by, state: str) -> dict:
    connection = get_db()
    with connection.transaction():
        device = connection.execute("SELECT id FROM devices WHERE id = %s FOR UPDATE", (device_id,)).fetchone()
        if device is None:
            raise NotFound("Device not found")
        return connection.execute(
            "INSERT INTO commands (id, device_id, requested_by, fan_state, created_at) "
            "VALUES (%s, %s, %s, %s, clock_timestamp()) "
            f"RETURNING {COMMAND_COLUMNS}", (uuid4(), device_id, requested_by, state),
        ).fetchone()


def pending_command(device_id: str) -> dict | None:
    require_device(device_id)
    return get_db().execute(
        f"SELECT {COMMAND_COLUMNS} FROM commands WHERE device_id = %s AND acknowledged_at IS NULL "
        "ORDER BY created_at, id LIMIT 1", (device_id,),
    ).fetchone()


def command_history(device_id: str, limit: int) -> list[dict]:
    return get_db().execute(
        f"SELECT {COMMAND_COLUMNS} FROM commands WHERE device_id = %s "
        "ORDER BY created_at DESC, id DESC LIMIT %s", (device_id, limit),
    ).fetchall()


def acknowledge_command(device_id: str, command_id, state: str) -> dict:
    connection = get_db()
    with connection.transaction():
        connection.execute("SELECT id FROM devices WHERE id = %s FOR UPDATE", (device_id,))
        command = connection.execute(
            f"SELECT {COMMAND_COLUMNS} FROM commands WHERE device_id = %s AND id = %s FOR UPDATE",
            (device_id, command_id),
        ).fetchone()
        if command is None:
            raise NotFound("Command not found")
        if command["fan_state"] != state:
            raise ApiError(409, "state_mismatch", "Reported fan state does not match the command")
        if command["acknowledged_at"] is not None:
            return command
        oldest = pending_command(device_id)
        if oldest is None or oldest["id"] != command_id:
            raise ApiError(409, "command_order", "An earlier command is still pending")
        return connection.execute(
            "UPDATE commands SET acknowledged_at = clock_timestamp() WHERE device_id = %s AND id = %s "
            f"RETURNING {COMMAND_COLUMNS}", (device_id, command_id),
        ).fetchone()
