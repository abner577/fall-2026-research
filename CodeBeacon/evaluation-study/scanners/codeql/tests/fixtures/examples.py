"""Independent scanner fixtures; parsed, never imported or executed.

Each ruleid annotation expects an alert on the following line. Unannotated
alerts fail verification too, so safe controls are checked across the suite.
"""
import os
import ssl
import random
import time
import uuid
import secrets
import hashlib
import logging
import requests as network
import httpx
import flask_limiter
from werkzeug.security import generate_password_hash


# ruleid: study/py/hardcoded-credential
service_password = "independent-fixture-only"
# ruleid: study/py/hardcoded-credential
settings = {"api_key": "fixture-value"}
# ruleid: study/py/hardcoded-credential
service_secret = os.getenv("SERVICE_SECRET", "fixture-fallback")
# ruleid: study/py/hardcoded-credential
def legacy_access(password="fixture-default"):
    return len(password)


service_password = os.environ["SERVICE_PASSWORD"]
empty_secret = ""
caption = "ordinary text"


def credential_connection(driver, supplied):
    # ruleid: py/hardcoded-credentials
    driver.connect(password="Zk7!mQ2@pL9#vR4$")
    driver.connect(password=supplied)


def policy(password, caption):
    # ruleid: study/py/short-password-length
    too_short = len(password) < 6
    # ruleid: study/py/short-password-length
    accepted = len(password) > 4
    # ruleid: study/py/short-password-length
    minimum = len(password) >= 5
    # ruleid: study/py/short-password-length
    rejected = len(password) <= 3
    strong_floor = len(password) >= 8
    equivalent_floor = len(password) > 7
    boundary_floor = len(password) <= 7
    unrelated = len(caption) < 4
    return too_short, accepted, minimum, rejected, strong_floor, unrelated


def password_storage(password, payload, db):
    # ruleid: py/weak-sensitive-data-hashing
    digest = hashlib.sha256(password.encode()).hexdigest()
    checksum = hashlib.sha256(payload).hexdigest()
    protected = generate_password_hash(password)
    # ruleid: study/py/plaintext-password-sql
    db.execute("INSERT INTO accounts (password) VALUES (%s)", (password,))
    # ruleid: study/py/plaintext-password-sql
    db.execute("UPDATE accounts SET password = %s", (password,))
    db.execute("INSERT INTO accounts (password) VALUES (%s)", (protected,))
    db.execute("INSERT INTO accounts (password) VALUES (%s)", (generate_password_hash(password),))
    db.execute("INSERT INTO messages (body) VALUES (%s)", (payload,))
    return digest, checksum


def transport(identity):
    # ruleid: study/py/http-transport
    network.get("http://telemetry.example.net/readings")
    # ruleid: study/py/http-transport, study/py/authentication-over-http
    network.post("http://gateway.example.net/access", auth=identity)
    # ruleid: study/py/http-transport
    network.request("GET", "http://gateway.example.net/ping")
    address = "http://metrics.example.net/series"
    # ruleid: study/py/http-transport
    network.get(address)
    # ruleid: study/py/http-transport
    network.get("http://localhost.attacker.example.net/")
    # ruleid: study/py/http-transport
    httpx.get(url="http://telemetry.example.net/readings")
    network.get("https://telemetry.example.net/readings")
    network.get("http://localhost:8080/health")
    network.get("http://127.0.0.1/health")
    network.get("http://[::1]:8080/health")
    network.get("https://gateway.example.net/access", auth=identity)


def output(password, caption):
    # ruleid: py/clear-text-logging-sensitive-data
    logging.warning("received %s", password)
    alias = password
    # ruleid: py/clear-text-logging-sensitive-data
    print(f"credential: {alias}")
    with open("cache.txt", "w") as stream:
        # ruleid: py/clear-text-storage-sensitive-data
        stream.write(password)
        stream.write(caption)
    logging.info("status %s", caption)
    print("[redacted]")


def create_access_token():
    # ruleid: study/py/predictable-credential
    return str(random.getrandbits(32))


def generation():
    # ruleid: study/py/predictable-credential
    access_token = str(random.randint(1000, 9999))
    # ruleid: study/py/predictable-credential
    device_token = str(time.time_ns())
    # ruleid: study/py/predictable-credential
    auth_token = str(uuid.uuid1())
    access_token = secrets.token_urlsafe(32)
    api_key = str(random.SystemRandom().getrandbits(256))
    sensor_value = random.randint(12, 25)
    return sensor_value


def certificates():
    # ruleid: py/request-without-cert-validation
    network.get("https://telemetry.example.net/", verify=False)
    # ruleid: study/py/disabled-tls-configuration
    context = ssl._create_unverified_context()
    # ruleid: study/py/disabled-tls-configuration
    context.verify_mode = ssl.CERT_NONE
    session = network.Session()
    # ruleid: study/py/disabled-tls-configuration
    session.verify = False
    # ruleid: study/py/disabled-tls-configuration
    client = httpx.Client(verify=False)
    network.get("https://telemetry.example.net/", verify=True)
    ssl.create_default_context()
    httpx.Client(verify=True)
    other_session = network.Session()
    other_session.verify = True
    context.verify_mode = ssl.CERT_REQUIRED


def protections(app):
    # ruleid: study/py/flask-login-disabled
    app.config["LOGIN_DISABLED"] = True
    # ruleid: study/py/flask-login-disabled
    app.config.update(LOGIN_DISABLED=True)
    # ruleid: study/py/flask-rate-limit-disabled
    app.config["RATELIMIT_ENABLED"] = False
    # ruleid: study/py/flask-rate-limit-disabled
    app.config.update(RATELIMIT_ENABLED=False)
    # ruleid: study/py/flask-rate-limit-disabled
    flask_limiter.Limiter(app=app, enabled=False)
    app.config["LOGIN_DISABLED"] = False
    app.config.update(LOGIN_DISABLED=False)
    app.config["RATELIMIT_ENABLED"] = True
    app.config.update(RATELIMIT_ENABLED=True)
    flask_limiter.Limiter(app=app, enabled=True)
