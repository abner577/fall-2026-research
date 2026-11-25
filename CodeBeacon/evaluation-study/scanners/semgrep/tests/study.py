"""Independent Semgrep fixtures; analyzed as source, never executed.

These examples were written from generic security requirements without opening
the version-A/B source or placement notes. Each rule has positive and negative
controls. Tests are outside application inputs and are not scored study cases.
"""

import hashlib
import logging
import os
import random
import secrets
import ssl
import time
import uuid

import flask_limiter
import httpx
import requests
from requests import post as send_post
from werkzeug.security import generate_password_hash


# ruleid: hardcoded-password-default-argument
def connect_archive(password="sample-fixture-value"):
    pass


# ok: hardcoded-password-default-argument
def connect_vault(password=""):
    pass


def literal_credentials(settings):
    # ruleid: study-python-hardcoded-credential
    ARCHIVE_PASSWORD = "example-value-for-rule-test"
    # ruleid: study-python-hardcoded-credential
    settings["api_key"] = "example-api-value"
    # ruleid: study-python-hardcoded-credential
    options = {"client_secret": "example-client-value"}
    # ruleid: study-python-hardcoded-credential
    os.getenv("SERVICE_PASSWORD", "example-fallback")
    # ok: study-python-hardcoded-credential
    SERVICE_PASSWORD = os.environ["SERVICE_PASSWORD"]
    # ok: study-python-hardcoded-credential
    empty_password = ""
    # ok: study-python-hardcoded-credential
    password_label = "Password"


def password_policy(password, payload):
    # ruleid: study-python-short-password-length
    if len(password) < 5:
        return False
    # ruleid: study-python-short-password-length
    accepted = len(password) >= 6
    # ruleid: study-python-short-password-length
    accepted = len(password) > 3
    # ok: study-python-short-password-length
    if len(password) < 8:
        return False
    # ok: study-python-short-password-length
    accepted = len(password) > 7
    # ok: study-python-short-password-length
    small = len(payload) < 5


def fast_hash(password, contents):
    # ruleid: study-python-fast-password-hash
    digest = hashlib.sha256(password.encode()).hexdigest()
    alias = password.encode()
    # ruleid: study-python-fast-password-hash
    digest = hashlib.new("sha1", alias).hexdigest()
    # ruleid: study-python-fast-password-hash
    digest = hashlib.md5(password.encode()).hexdigest()
    # ok: study-python-fast-password-hash
    digest = hashlib.sha256(contents).hexdigest()
    # ok: study-python-fast-password-hash
    digest = generate_password_hash(password, method="scrypt")


def password_storage(cursor, password, username):
    # ruleid: study-python-plaintext-password-sql
    cursor.execute("INSERT INTO members (password) VALUES (%s)", (password,))
    # ruleid: study-python-plaintext-password-sql
    cursor.execute("UPDATE members SET password = %s", (password,))
    digest = generate_password_hash(password, method="scrypt")
    # ok: study-python-plaintext-password-sql
    cursor.execute("INSERT INTO members (password) VALUES (%s)", (digest,))
    # ok: study-python-plaintext-password-sql
    cursor.execute("INSERT INTO members (username) VALUES (%s)", (username,))


def http_transport(password, headers):
    # ruleid: no-auth-over-http, request-with-http
    requests.get("http://archive.example.test/report", auth=("reader", password))
    # ruleid: request-with-http
    requests.post("http://archive.example.test/events", headers=headers)
    # ruleid: request-with-http
    send_post("http://archive.example.test/events", data=b"event")
    # ok: no-auth-over-http, request-with-http
    requests.get("https://archive.example.test/report", auth=("reader", password))
    # ok: request-with-http
    requests.get("http://localhost:9000/health")


def output_secrets(password, auth_token, event_count):
    logger = logging.getLogger(__name__)
    # ruleid: python-logger-credential-disclosure, study-python-secret-in-output
    logger.info("password=%s", password)
    # ruleid: study-python-secret-in-output
    logging.warning(f"credential received: {auth_token}")
    # ruleid: study-python-secret-in-output
    print(password)
    alias = auth_token
    # ruleid: study-python-secret-in-output
    print(f"debug: {alias}")
    # ok: python-logger-credential-disclosure, study-python-secret-in-output
    logger.info("authentication failed")
    # ok: study-python-secret-in-output
    print(event_count)


def persist_secret(password, api_key, output_path, count):
    with open("archive.txt", "w") as handle:
        # ruleid: study-python-secret-in-file
        handle.write(password)
        # ok: study-python-secret-in-file
        handle.write(str(count))
    # ruleid: study-python-secret-in-file
    output_path.write_text(f"key={api_key}")
    # ok: study-python-secret-in-file
    output_path.write_text("credential=[redacted]")


def generated_credentials():
    # ruleid: study-python-predictable-credential
    access_token = str(random.getrandbits(48))
    # ruleid: study-python-predictable-credential
    password = "".join(random.choices("abcdef1234", k=10))
    stamp = str(time.time_ns())
    # ruleid: study-python-predictable-credential
    auth_token = stamp
    # ruleid: study-python-predictable-credential
    client_secret = str(uuid.uuid1())
    # ok: study-python-predictable-credential
    access_token = secrets.token_urlsafe(32)
    # ok: study-python-predictable-credential
    temperature = random.randint(10, 30)
    # ok: study-python-predictable-credential
    nonce = random.SystemRandom().getrandbits(256)


def generate_reset_token():
    # ruleid: study-python-predictable-credential
    return str(random.randint(100000, 999999))


def generate_access_token():
    # ok: study-python-predictable-credential
    return secrets.token_hex(32)


def tls_requests(url):
    # ruleid: disabled-cert-validation
    requests.post(url, verify=False)
    # ruleid: disabled-cert-validation
    requests.request("PATCH", url, verify=False)
    # ok: disabled-cert-validation
    requests.get(url, verify=True)
    # ok: disabled-cert-validation
    requests.get(url, verify="ca.pem")


def session_tls(url):
    session = requests.Session()
    # ruleid: study-python-session-disabled-tls
    session.verify = False
    # ruleid: study-python-session-disabled-tls
    session.get(url, verify=False)
    # ok: study-python-session-disabled-tls
    session.verify = True
    # ok: study-python-session-disabled-tls
    session.post(url, verify="ca.pem")
    with requests.Session() as other:
        # ruleid: study-python-session-disabled-tls
        other.get(url, verify=False)


def other_tls():
    # ruleid: study-python-unverified-tls-context
    ctx = ssl._create_unverified_context()
    # ruleid: study-python-unverified-tls-context
    ctx.verify_mode = ssl.CERT_NONE
    # ruleid: study-python-unverified-tls-context
    httpx.Client(verify=False)
    # ruleid: study-python-unverified-tls-context
    httpx.AsyncClient(verify=False)
    # ok: study-python-unverified-tls-context
    ctx = ssl.create_default_context()
    # ok: study-python-unverified-tls-context
    httpx.Client(verify=True)


def authentication_configuration(app):
    # ruleid: study-flask-login-disabled
    app.config["LOGIN_DISABLED"] = True
    # ruleid: study-flask-login-disabled
    app.config.update(LOGIN_DISABLED=True)
    # ok: study-flask-login-disabled
    app.config["LOGIN_DISABLED"] = False


def throttle_configuration(app):
    # ruleid: study-flask-rate-limit-disabled
    app.config["RATELIMIT_ENABLED"] = False
    # ruleid: study-flask-rate-limit-disabled
    app.config.update(RATELIMIT_ENABLED=False)
    # ruleid: study-flask-rate-limit-disabled
    flask_limiter.Limiter(app=app, enabled=False)
    # ok: study-flask-rate-limit-disabled
    app.config["RATELIMIT_ENABLED"] = True
    # ok: study-flask-rate-limit-disabled
    flask_limiter.Limiter(app=app, enabled=True)
