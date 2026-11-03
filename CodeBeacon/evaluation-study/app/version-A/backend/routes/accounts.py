from flask import Blueprint, g
from werkzeug.exceptions import Unauthorized

from backend.security import (
    account_required, bounded_text, issue_account_token, json_body, login_attempt,
    normalize_username, public_row,
)
from backend.services import accounts

blueprint = Blueprint("accounts", __name__, url_prefix="/api/accounts")


def _account_response(account: dict) -> dict:
    return public_row({key: account[key] for key in ("id", "username", "created_at")})


def _session_response(account: dict) -> dict:
    return {**issue_account_token(account), "account": _account_response(account)}


@blueprint.post("")
def register():
    data = json_body("username", "password")
    username = normalize_username(data["username"])
    password = bounded_text(data["password"], "password", 128)
    return {"account": _account_response(accounts.register_account(username, password))}, 201


@blueprint.post("/login")
def login():
    data = json_body("username", "password")
    username = normalize_username(data["username"])
    password = bounded_text(data["password"], "password", 128)
    with login_attempt(username) as attempt:
        account = accounts.authenticate(username, password)
        attempt["authenticated"] = account is not None
    if account is None:
        raise Unauthorized("Invalid username or password")
    return _session_response(account)


@blueprint.get("/me")
@account_required
def me():
    return {"account": _account_response(g.account)}


@blueprint.patch("/password")
@account_required
def change_password():
    data = json_body("current_password", "new_password")
    current = bounded_text(data["current_password"], "current_password", 128)
    new = bounded_text(data["new_password"], "new_password", 128)
    account = accounts.change_password(g.account["id"], current, new)
    return _session_response(account)
