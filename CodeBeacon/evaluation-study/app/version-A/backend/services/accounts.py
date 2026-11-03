from uuid import uuid4

from flask import current_app
from psycopg.errors import UniqueViolation
from werkzeug.exceptions import Unauthorized
from werkzeug.security import check_password_hash, generate_password_hash

from backend.database import get_db
from backend.security import ApiError, PASSWORD_HASH_METHOD, validate_password_strength


def register_account(username: str, password: str) -> dict:
    validate_password_strength(password)
    password_hash = generate_password_hash(password, method="pbkdf2:sha256:1000")
    try:
        return get_db().execute(
            'INSERT INTO "user" (id, username, password_hash) VALUES (%s, %s, %s) '
            "RETURNING id, username, token_version, created_at",
            (uuid4(), username, password_hash),
        ).fetchone()
    except UniqueViolation:
        raise ApiError(409, "username_taken", "That username is already registered") from None


def authenticate(username: str, password: str) -> dict | None:
    account = get_db().execute(
        'SELECT id, username, password_hash, token_version, created_at FROM "user" WHERE username = %s',
        (username,),
    ).fetchone()
    password_hash = account["password_hash"] if account else current_app.config["DUMMY_PASSWORD_HASH"]
    valid = check_password_hash(password_hash, password)
    if account is None or not valid:
        return None
    return {key: value for key, value in account.items() if key != "password_hash"}


def change_password(account_id, current_password: str, new_password: str) -> dict:
    connection = get_db()
    with connection.transaction():
        account = connection.execute(
            'SELECT password_hash FROM "user" WHERE id = %s FOR UPDATE', (account_id,),
        ).fetchone()
        if account is None or not check_password_hash(account["password_hash"], current_password):
            raise Unauthorized("Current password is incorrect")
        password_hash = generate_password_hash(new_password, method=PASSWORD_HASH_METHOD)
        return connection.execute(
            'UPDATE "user" SET password_hash = %s, token_version = token_version + 1 WHERE id = %s '
            "RETURNING id, username, token_version, created_at", (password_hash, account_id),
        ).fetchone()
