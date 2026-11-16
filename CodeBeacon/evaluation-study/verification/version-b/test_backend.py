"""Version B author checks with database doubles and local network listeners."""

import hashlib
import os
import random
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import nullcontext
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2] / "app" / "version-B"
sys.path.insert(0, str(ROOT))

import requests
from backend import main
from backend.security import ApiError, PASSWORD_HASH_METHOD, issue_account_token
from backend.services import accounts, devices
from backend.settings import ConfigurationError, load_settings
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from werkzeug.security import check_password_hash, generate_password_hash

NOW = datetime.now(timezone.utc)
PASSWORD = "a sufficiently long password"


def connection_with_rows(*rows):
    connection = Mock()
    connection.transaction.side_effect = lambda: nullcontext()
    connection.execute.side_effect = [Mock(fetchone=Mock(return_value=row)) for row in rows]
    return connection


class BackendChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.dict(os.environ, {"APP_SECRET_KEY": "x" * 48, "DB_PASSWORD": "test-only"}, clear=True):
            cls.settings = load_settings()
        cls.app = main.create_app(cls.settings)
        cls.app.testing = True
        cls.owner = {"id": uuid4(), "username": "alice", "token_version": 1, "created_at": NOW}
        with cls.app.app_context():
            cls.token = issue_account_token(cls.owner)["access_token"]

    def setUp(self):
        self.client = self.app.test_client()
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_password_strength_storage_and_current_password(self):
        stored = generate_password_hash(PASSWORD, method=PASSWORD_HASH_METHOD)
        with self.app.app_context(), patch.object(accounts, "get_db") as db:
            for operation in (lambda: accounts.register_account("alice", "a"),
                              lambda: accounts.change_password(self.owner["id"], PASSWORD, "a")):
                with self.assertRaises(BadRequest):
                    operation()
            db.assert_not_called()
            accounts.register_account("alice", PASSWORD)
            registration_hash = db.return_value.execute.call_args.args[1][2]
            self.assertTrue(registration_hash.startswith(PASSWORD_HASH_METHOD + "$"))
            self.assertTrue(check_password_hash(registration_hash, PASSWORD))
        db = connection_with_rows({"password_hash": stored}, self.owner)
        with self.app.app_context(), patch.object(accounts, "get_db", return_value=db):
            accounts.change_password(self.owner["id"], PASSWORD, PASSWORD + " changed")
        changed_hash = db.execute.call_args.args[1][0]
        self.assertTrue(changed_hash.startswith(PASSWORD_HASH_METHOD + "$"))
        self.assertTrue(check_password_hash(changed_hash, PASSWORD + " changed"))
        db = connection_with_rows({"password_hash": stored})
        with self.app.app_context(), patch.object(accounts, "get_db", return_value=db):
            with self.assertRaises(Unauthorized):
                accounts.change_password(self.owner["id"], "wrong", PASSWORD)
        self.assertEqual(db.execute.call_count, 1)
        for value, password in ((registration_hash, PASSWORD), (changed_hash, PASSWORD + " changed")):
            db = connection_with_rows({**self.owner, "password_hash": value})
            with self.app.app_context(), patch.object(accounts, "get_db", return_value=db):
                self.assertEqual(accounts.authenticate("alice", password), self.owner)

    def test_direct_login_attempts_reach_password_verification(self):
        with patch("backend.security.get_db") as limiter_db, patch.object(accounts, "authenticate", return_value=None) as verify:
            for unused in range(12):
                response = self.client.post("/api/accounts/login", base_url="https://localhost", json={"username": "ALICE", "password": "wrong"})
                self.assertEqual(response.status_code, 401)
                self.assertNotIn("Retry-After", response.headers)
            self.assertEqual(verify.call_count, 12)
            limiter_db.assert_not_called()
            verify.return_value = self.owner
            response = self.client.post("/api/accounts/login", base_url="https://localhost", json={"username": "alice", "password": PASSWORD})
            self.assertEqual(response.status_code, 200)
            self.assertIn("access_token", response.json)

    def test_polling_authentication_and_device_binding_on_both_transports(self):
        path = "/api/devices/bobs-device/commands/pending"
        token = "local-test-device-token"
        device = {"id": "bobs-device", "token_hash": hashlib.sha256(token.encode()).hexdigest()}
        for scheme in ("http", "https"):
            with patch.object(devices, "pending_command") as pending:
                self.assertEqual(self.client.get(path, base_url=scheme + "://localhost").status_code, 401)
                pending.assert_not_called()
            db = connection_with_rows(device, device)
            with patch("backend.security.get_db", return_value=db), patch.object(devices, "pending_command", return_value=None) as pending:
                for unused in range(2):
                    response = self.client.get(path, base_url=scheme + "://localhost", headers={"Authorization": "Bearer " + token})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json, {"command": None})
                self.assertEqual(pending.call_count, 2)
            db = connection_with_rows({**device, "token_hash": "0" * 64})
            with patch("backend.security.get_db", return_value=db), patch.object(devices, "pending_command") as pending:
                self.assertEqual(self.client.get(path, base_url=scheme + "://localhost", headers={"Authorization": "Bearer " + token}).status_code, 401)
                pending.assert_not_called()

    def test_cross_owner_command_submission_and_other_owner_checks(self):
        path = "/api/devices/bobs-device/commands"
        self.assertEqual(self.client.post(path, base_url="https://localhost", json={"fan_state": "on"}).status_code, 401)
        command = {"id": uuid4(), "device_id": "bobs-device", "fan_state": "on"}
        auth_db = connection_with_rows(self.owner)
        service_db = connection_with_rows({"id": "bobs-device"}, command)
        with patch("backend.security.get_db", return_value=auth_db), patch.object(devices, "get_db", return_value=service_db), patch.object(devices, "owned_device") as owned:
            response = self.client.post(path, base_url="https://localhost", headers=self.headers, json={"fan_state": "on"})
            self.assertEqual(response.status_code, 201)
            owned.assert_not_called()
            self.assertEqual(service_db.execute.call_args.args[1][2], self.owner["id"])
            self.assertNotIn("owner_id", service_db.execute.call_args_list[0].args[0])
        for suffix in ("", "/readings", "/commands"):
            with patch("backend.security.get_db", return_value=connection_with_rows(self.owner)), patch.object(devices, "owned_device", side_effect=NotFound) as owned:
                response = self.client.get("/api/devices/bobs-device" + suffix, base_url="https://localhost", headers=self.headers)
                self.assertEqual(response.status_code, 404)
                owned.assert_called_once_with("bobs-device", self.owner["id"])

    def test_enrollment_secrets_and_digest_storage(self):
        with self.app.app_context(), patch.object(devices, "_insert_device", side_effect=lambda owner, identity, name, token: {"id": identity}):
            device, token = devices.enroll_device(self.owner["id"], "Bedroom")
            other_device, other_token = devices.enroll_device(self.owner["id"], "Office")
        self.assertNotEqual(token, other_token)
        self.assertNotEqual(token, f"rma_{random.Random(device['id']).getrandbits(256):064x}")
        self.assertGreaterEqual(len(token), 43)
        db = connection_with_rows(device)
        with self.app.app_context(), patch.object(devices, "get_db", return_value=db):
            devices._insert_device(self.owner["id"], device["id"], "Bedroom", token)
        self.assertEqual(db.execute.call_args.args[1][3], hashlib.sha256(token.encode()).hexdigest())

    def test_reading_deduplication_and_acknowledgment(self):
        reading = {"id": uuid4(), "recorded_at": NOW, "temperature_c": 24.1, "fan_state": "off"}
        for rows, created in (((reading,), True), ((None, reading), False)):
            with self.app.app_context(), patch.object(devices, "get_db", return_value=connection_with_rows(*rows)):
                self.assertEqual(devices.save_reading("room", reading), (reading, created))
        with self.app.app_context(), patch.object(devices, "get_db", return_value=connection_with_rows(None, {**reading, "temperature_c": 25.0})):
            with self.assertRaises(ApiError) as caught:
                devices.save_reading("room", reading)
            self.assertEqual(caught.exception.status, 409)
        command = {"id": uuid4(), "fan_state": "on", "acknowledged_at": None}
        acknowledged = {**command, "acknowledged_at": NOW}
        db = connection_with_rows({"id": "room"}, command, acknowledged)
        with self.app.app_context(), patch.object(devices, "get_db", return_value=db), patch.object(devices, "pending_command", return_value=command):
            self.assertEqual(devices.acknowledge_command("room", command["id"], "on"), acknowledged)
        with self.app.app_context(), patch.object(devices, "get_db", return_value=connection_with_rows({"id": "room"}, acknowledged)):
            self.assertEqual(devices.acknowledge_command("room", command["id"], "on"), acknowledged)

    def test_reading_and_acknowledgment_require_device_identity(self):
        token = "local-bound-device-token"
        device = {"id": "room", "token_hash": hashlib.sha256(token.encode()).hexdigest()}
        reading = {"reading_id": str(uuid4()), "recorded_at": NOW.isoformat(), "temperature_c": 24.1, "unit": "C", "fan_state": "off"}
        for suffix, payload in (("/readings", reading), (f"/commands/{uuid4()}/ack", {"fan_state": "on"})):
            path = "/api/devices/room" + suffix
            self.assertEqual(self.client.post(path, base_url="https://localhost", json=payload).status_code, 401)
            with patch("backend.security.get_db", return_value=connection_with_rows({**device, "token_hash": "0" * 64})):
                self.assertEqual(self.client.post(path, base_url="https://localhost", headers={"Authorization": "Bearer " + token}, json=payload).status_code, 401)
        with patch("backend.security.get_db", return_value=connection_with_rows(device)), patch.object(devices, "save_reading", return_value=({"id": uuid4()}, True)) as save:
            response = self.client.post("/api/devices/room/readings", base_url="https://localhost", headers={"Authorization": "Bearer " + token}, json=reading)
            self.assertEqual(response.status_code, 201)
            save.assert_called_once()
        with patch("backend.security.get_db", return_value=connection_with_rows(device)), patch.object(devices, "save_reading") as save:
            response = self.client.post("/api/devices/room/readings", base_url="https://localhost", headers={"Authorization": "Bearer " + token}, json={**reading, "temperature_c": True})
            self.assertEqual(response.status_code, 400)
            save.assert_not_called()
        with patch("backend.security.get_db", return_value=connection_with_rows(device)), patch.object(devices, "acknowledge_command", return_value={"id": uuid4(), "fan_state": "on"}) as acknowledge:
            response = self.client.post(f"/api/devices/room/commands/{uuid4()}/ack", base_url="https://localhost", headers={"Authorization": "Bearer " + token}, json={"fan_state": "on"})
            self.assertEqual(response.status_code, 200)
            acknowledge.assert_called_once()

    def test_partial_listener_startup_closes_bound_socket(self):
        first = Mock()
        with patch.object(main, "make_server", side_effect=[first, OSError("Port is occupied")]):
            with self.assertRaises(OSError):
                main.serve(self.app, self.settings, Mock())
        first.server_close.assert_called_once()
        first.shutdown.assert_not_called()

    def test_http_scope_session_revocation_and_configuration(self):
        for method, path in (("GET", "/api/accounts/me"), ("POST", "/api/accounts/login"), ("POST", "/api/devices/bob/readings"), ("POST", "/api/devices/bob/commands"), ("POST", f"/api/devices/bob/commands/{uuid4()}/ack"), ("HEAD", "/api/devices/bob/commands/pending"), ("OPTIONS", "/api/devices/bob/commands/pending")):
            response = self.client.open(path, method=method, base_url="http://localhost", headers={**self.headers, "X-Forwarded-Proto": "https"})
            self.assertEqual(response.status_code, 400)
            self.assertNotIn("Location", response.headers)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        with patch("backend.security.get_db", return_value=connection_with_rows({**self.owner, "token_version": 2})):
            self.assertEqual(self.client.get("/api/accounts/me", base_url="https://localhost", headers=self.headers).status_code, 401)
        for changes in ({"APP_SECRET_KEY": ""}, {"DB_PASSWORD": ""}, {"DB_SSLMODE": "prefer"}, {"BACKEND_COMMAND_POLL_HTTP_PORT": "8444"}, {"BACKEND_DEBUG": "true"}):
            with patch.dict(os.environ, {"APP_SECRET_KEY": "x" * 48, "DB_PASSWORD": "test", **changes}, clear=True):
                with self.assertRaises(ConfigurationError):
                    load_settings()
        self.assertEqual(self.settings.db_name, "room_monitor_b")
        self.assertEqual(self.settings.port, 8444)
        self.assertEqual(self.settings.command_poll_http_port, 8081)

    def test_live_http_and_trusted_https_listeners_and_shutdown(self):
        stop = threading.Event()
        ready = threading.Event()
        servers = []
        errors = []
        real_make_server = main.make_server

        class StopSignal:
            def wait(self):
                stop.wait(15)
                raise KeyboardInterrupt

            def set(self):
                stop.set()

        def capture_server(*args, **kwargs):
            server = real_make_server(*args, **kwargs)
            servers.append(server)
            if len(servers) == 2:
                ready.set()
            return server

        with tempfile.TemporaryDirectory() as temp:
            cert, key = Path(temp) / "server.crt", Path(temp) / "server.key"
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-sha256", "-nodes", "-days", "1", "-keyout", str(key), "-out", str(cert), "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1", "-addext", "basicConstraints=critical,CA:TRUE"], check=True, capture_output=True, timeout=15)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.load_cert_chain(cert, key)
            settings = replace(self.settings, port=0, command_poll_http_port=0)
            token = "local-network-test-token"
            device = {"id": "room", "token_hash": hashlib.sha256(token.encode()).hexdigest()}

            def run():
                try:
                    main.serve(self.app, settings, context)
                except BaseException as error:
                    errors.append(type(error).__name__)

            with patch.object(main, "make_server", side_effect=capture_server), patch.object(main, "Event", return_value=StopSignal()), patch("backend.security.get_db", side_effect=lambda: connection_with_rows(device)), patch.object(devices, "pending_command", return_value=None), requests.Session() as client:
                client.trust_env = False
                worker = threading.Thread(target=run, daemon=True)
                worker.start()
                try:
                    self.assertTrue(ready.wait(5), errors)
                    https_port, http_port = [server.server_port for server in servers]
                    path = "/api/devices/room/commands/pending"
                    headers = {"Authorization": "Bearer " + token}
                    response = client.get(f"http://127.0.0.1:{http_port}" + path, headers=headers, timeout=5)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.request.headers["Authorization"], headers["Authorization"])
                    self.assertEqual(client.get(f"http://127.0.0.1:{http_port}" + path, timeout=5).status_code, 401)
                    response = client.get(f"https://127.0.0.1:{https_port}" + path, headers=headers, verify=str(cert), timeout=5)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(client.post(f"http://127.0.0.1:{http_port}/api/accounts/login", json={"username": "alice", "password": "wrong"}, timeout=5).status_code, 400)
                    with self.assertRaises(requests.exceptions.SSLError):
                        client.get(f"https://127.0.0.1:{https_port}" + path, headers=headers, timeout=5)
                finally:
                    stop.set()
                    worker.join(5)
                self.assertFalse(worker.is_alive())
                self.assertEqual(errors, [])
                for server in servers:
                    self.assertEqual(server.socket.fileno(), -1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
