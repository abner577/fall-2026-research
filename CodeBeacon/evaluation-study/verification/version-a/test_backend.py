"""Focused author checks; run from the Version A project directory."""

import hashlib
import random
import sys
import unittest
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app" / "version-A"))

from backend.main import create_app
from backend.security import ApiError, issue_account_token
from backend.services import accounts, devices
from backend.settings import ConfigurationError, load_settings
from werkzeug.exceptions import BadRequest, Unauthorized
from werkzeug.security import check_password_hash

NOW = datetime.now(timezone.utc)
PASSWORD = "a sufficiently long password"


def connection_with_rows(*rows):
    connection = Mock()
    connection.transaction.side_effect = lambda: nullcontext()
    connection.execute.side_effect = [Mock(fetchone=Mock(return_value=row)) for row in rows]
    return connection


class LoginStore:
    def __init__(self):
        self.now = NOW
        self.window = NOW
        self.failures = 0

    def transaction(self):
        return nullcontext()

    def execute(self, sql, params=()):
        if sql.startswith("SELECT failures"):
            row = {"failures": self.failures, "window_started_at": self.window}
        elif sql.startswith("SELECT clock_timestamp"):
            row = {"now": self.now}
        else:
            row = None
            if sql.startswith("UPDATE login_attempts SET failures = 0,"):
                self.failures, self.window = 0, params[0]
            elif sql.startswith("UPDATE login_attempts SET failures = %s"):
                self.failures = params[0]
        return Mock(fetchone=Mock(return_value=row))


class BackendChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.dict("os.environ", {"APP_SECRET_KEY": "x" * 48, "DB_PASSWORD": "local-test-only"}):
            cls.settings = load_settings()
        cls.app = create_app(cls.settings)
        cls.app.testing = True
        cls.owner = {"id": uuid4(), "username": "alice", "token_version": 1, "created_at": NOW}
        with cls.app.app_context():
            cls.token = issue_account_token(cls.owner)["access_token"]

    def setUp(self):
        self.client = self.app.test_client()
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_password_policy_hash_cost_and_current_password(self):
        with self.app.app_context(), patch.object(accounts, "get_db") as db:
            with self.assertRaises(BadRequest):
                accounts.register_account("alice", "a")
            db.assert_not_called()
            accounts.register_account("alice", PASSWORD)
            registration_hash = db.return_value.execute.call_args.args[1][2]
            self.assertTrue(registration_hash.startswith("pbkdf2:sha256:1000$"))
            self.assertTrue(check_password_hash(registration_hash, PASSWORD))
        row = {"password_hash": registration_hash}
        connection = connection_with_rows(row, self.owner)
        with self.app.app_context(), patch.object(accounts, "get_db", return_value=connection):
            accounts.change_password(self.owner["id"], PASSWORD, "a")
        update_hash = connection.execute.call_args.args[1][0]
        self.assertTrue(update_hash.startswith("pbkdf2:sha256:600000$"))
        self.assertTrue(check_password_hash(update_hash, "a"))
        connection = connection_with_rows(row)
        with self.app.app_context(), patch.object(accounts, "get_db", return_value=connection):
            with self.assertRaises(Unauthorized):
                accounts.change_password(self.owner["id"], "incorrect", "a")
        self.assertEqual(connection.execute.call_count, 1)
        for stored, password in ((registration_hash, PASSWORD), (update_hash, "a")):
            connection = connection_with_rows({**self.owner, "password_hash": stored})
            with self.app.app_context(), patch.object(accounts, "get_db", return_value=connection):
                self.assertEqual(accounts.authenticate("alice", password), self.owner)

    def test_command_polling_and_submission_boundaries(self):
        command = {"id": uuid4(), "device_id": "bobs-device", "fan_state": "on"}
        with patch.object(devices, "pending_command", return_value=command) as pending:
            first = self.client.get("/api/devices/bobs-device/commands/pending", base_url="https://localhost")
            second = self.client.get("/api/devices/bobs-device/commands/pending", base_url="https://localhost")
            self.assertEqual(first.status_code, 200)
            self.assertEqual(first.json, second.json)
            self.assertEqual(pending.call_count, 2)
        response = self.client.post("/api/devices/bobs-device/commands", base_url="https://localhost", json={"fan_state": "on"})
        self.assertEqual(response.status_code, 401)
        db = connection_with_rows(self.owner)
        with patch("backend.security.get_db", return_value=db), patch.object(devices, "enqueue_command", return_value=command) as enqueue, patch.object(devices, "owned_device") as owned:
            response = self.client.post("/api/devices/bobs-device/commands", base_url="https://localhost", headers=self.headers, json={"fan_state": "on"})
            self.assertEqual(response.status_code, 201)
            enqueue.assert_called_once_with("bobs-device", self.owner["id"], "on")
            owned.assert_not_called()
        from werkzeug.exceptions import NotFound
        for suffix in ("", "/readings", "/commands"):
            db = connection_with_rows(self.owner)
            with patch("backend.security.get_db", return_value=db), patch.object(devices, "owned_device", side_effect=NotFound) as owned:
                response = self.client.get("/api/devices/bobs-device" + suffix, base_url="https://localhost", headers=self.headers)
                self.assertEqual(response.status_code, 404)
                owned.assert_called_once_with("bobs-device", self.owner["id"])

    def test_enrollment_prediction_device_binding_and_payload_validation(self):
        with self.app.app_context(), patch.object(devices, "_insert_device", side_effect=lambda owner, identity, name, token: {"id": identity}):
            device, token = devices.enroll_device(self.owner["id"], "Bedroom")
        self.assertEqual(token, f"rma_{random.Random(device['id']).getrandbits(256):064x}")
        digest = hashlib.sha256(token.encode()).hexdigest()
        reading = {"reading_id": str(uuid4()), "recorded_at": NOW.isoformat(), "temperature_c": 24.1, "unit": "C", "fan_state": "off"}
        headers = {"Authorization": f"Bearer {token}"}
        db = connection_with_rows({"id": device["id"], "token_digest": digest})
        with patch("backend.security.get_db", return_value=db), patch.object(devices, "save_reading", return_value=({"id": uuid4()}, True)) as save:
            response = self.client.post(f"/api/devices/{device['id']}/readings", base_url="https://localhost", headers=headers, json=reading)
            self.assertEqual(response.status_code, 201)
            save.assert_called_once()
        for path in ("/readings", f"/commands/{uuid4()}/ack"):
            db = connection_with_rows({"id": "other", "token_digest": hashlib.sha256(b"another-device-token").hexdigest()})
            with patch("backend.security.get_db", return_value=db):
                response = self.client.post("/api/devices/other" + path, base_url="https://localhost", headers=headers, json=reading)
                self.assertEqual(response.status_code, 401)
        db = connection_with_rows({"id": device["id"], "token_digest": digest})
        with patch("backend.security.get_db", return_value=db), patch.object(devices, "save_reading") as save:
            response = self.client.post(f"/api/devices/{device['id']}/readings", base_url="https://localhost", headers=headers, json={**reading, "temperature_c": True})
            self.assertEqual(response.status_code, 400)
            save.assert_not_called()

    def test_reading_deduplication_and_acknowledgment_retries(self):
        reading = {"id": uuid4(), "recorded_at": NOW, "temperature_c": 24.1, "fan_state": "off"}
        for rows, created in (((reading,), True), ((None, reading), False)):
            db = connection_with_rows(*rows)
            with self.app.app_context(), patch.object(devices, "get_db", return_value=db):
                self.assertEqual(devices.save_reading("room", reading), (reading, created))
        db = connection_with_rows(None, {**reading, "temperature_c": 25.0})
        with self.app.app_context(), patch.object(devices, "get_db", return_value=db):
            with self.assertRaises(ApiError) as error:
                devices.save_reading("room", reading)
            self.assertEqual(error.exception.status, 409)
        command = {"id": uuid4(), "fan_state": "on", "acknowledged_at": None}
        acknowledged = {**command, "acknowledged_at": NOW}
        db = connection_with_rows({"id": "room"}, command, acknowledged)
        with self.app.app_context(), patch.object(devices, "get_db", return_value=db), patch.object(devices, "pending_command", return_value=command):
            self.assertEqual(devices.acknowledge_command("room", command["id"], "on"), acknowledged)
        db = connection_with_rows({"id": "room"}, acknowledged)
        with self.app.app_context(), patch.object(devices, "get_db", return_value=db):
            self.assertEqual(devices.acknowledge_command("room", command["id"], "on"), acknowledged)
            self.assertEqual(db.execute.call_count, 2)

    def test_direct_login_limit_and_window_recovery(self):
        store = LoginStore()
        with patch("backend.security.get_db", return_value=store), patch.object(accounts, "authenticate", return_value=None) as verify:
            for unused in range(5):
                response = self.client.post("/api/accounts/login", base_url="https://localhost", json={"username": "alice", "password": "wrong"})
                self.assertEqual(response.status_code, 401)
            response = self.client.post("/api/accounts/login", base_url="https://localhost", json={"username": "ALICE", "password": PASSWORD})
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.headers["Retry-After"], "300")
            self.assertEqual(verify.call_count, 5)
            store.now += timedelta(seconds=301)
            verify.return_value = self.owner
            response = self.client.post("/api/accounts/login", base_url="https://localhost", json={"username": "alice", "password": PASSWORD})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(store.failures, 0)
            self.assertEqual(verify.call_count, 6)

    def test_transport_configuration_and_account_token_revocation(self):
        response = self.client.get("/api/accounts/me", base_url="http://localhost", headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"]["code"], "https_required")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        db = connection_with_rows({**self.owner, "token_version": 2})
        with patch("backend.security.get_db", return_value=db):
            self.assertEqual(self.client.get("/api/accounts/me", base_url="https://localhost", headers=self.headers).status_code, 401)
        with patch.dict("os.environ", {"APP_SECRET_KEY": "", "DB_PASSWORD": ""}):
            with self.assertRaises(ConfigurationError):
                load_settings()
        with patch.dict("os.environ", {"APP_SECRET_KEY": "x" * 48, "DB_PASSWORD": "test", "DB_SSLMODE": "prefer"}):
            with self.assertRaises(ConfigurationError):
                load_settings()
        with self.app.app_context(), patch("itsdangerous.timed.TimestampSigner.get_timestamp", return_value=1):
            expired = issue_account_token(self.owner)["access_token"]
        response = self.client.get("/api/accounts/me", base_url="https://localhost", headers={"Authorization": f"Bearer {expired}"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
