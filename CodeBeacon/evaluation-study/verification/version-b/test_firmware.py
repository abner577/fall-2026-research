"""Firmware author checks, including local requests to the Version B API."""

import hashlib
import os
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2] / "app" / "version-B"
sys.path.insert(0, str(ROOT))

import requests
from backend import main as backend_main
from backend.services import devices
from backend.settings import load_settings as load_backend_settings
from firmware.api_client import ApiError, DeviceApiClient, FanCommand, Reading
from firmware.fan import FanState
from firmware.main import DeviceRuntime, main as firmware_main
from firmware.settings import ConfigurationError, PROJECT_ROOT, load_settings
from firmware.temperature_sensor import TemperatureSensor
from flask import request
from werkzeug.serving import make_server

TOKEN = "local-firmware-test-device-token"


def response(status=200, data=None):
    result = MagicMock()
    result.__enter__.return_value = result
    result.status_code = status
    result.json.return_value = data
    return result


class FirmwareChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.cert = Path(cls.temp.name) / "server.crt"
        cls.key = Path(cls.temp.name) / "server.key"
        cls.other_cert = Path(cls.temp.name) / "other.crt"
        for cert, key in ((cls.cert, cls.key), (cls.other_cert, Path(cls.temp.name) / "other.key")):
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-sha256", "-nodes", "-days", "1", "-keyout", str(key), "-out", str(cert), "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1", "-addext", "basicConstraints=critical,CA:TRUE"], check=True, capture_output=True, timeout=15)
        cls.environment = {"DEVICE_ID": "room", "DEVICE_TOKEN": TOKEN, "API_CA_BUNDLE": str(cls.cert)}
        with patch.dict(os.environ, cls.environment, clear=True), patch("firmware.settings.dotenv_values", return_value={}):
            cls.settings = load_settings()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def reading(self):
        return Reading(str(uuid4()), datetime.now(timezone.utc).isoformat(), 24.1, FanState.OFF)

    def test_settings_require_external_credentials_and_validate_origins(self):
        for changes in ({"DEVICE_ID": ""}, {"DEVICE_TOKEN": ""}, {"DEVICE_ID": "room-monitor-01", "DEVICE_TOKEN": ""}, {"API_BASE_URL": "http://localhost:8444"}, {"API_BASE_URL": "https://user:secret@localhost"}, {"API_BASE_URL": "https://localhost/path"}, {"API_BASE_URL": "https://localhost:99999"}, {"DEVICE_COMMAND_POLL_BASE_URL": "https://localhost:8081"}, {"DEVICE_COMMAND_POLL_BASE_URL": "http://localhost?token=secret"}, {"DEVICE_COMMAND_POLL_BASE_URL": "http://localhost/#fragment"}, {"DEVICE_COMMAND_POLL_BASE_URL": "http://local host:8081"}, {"API_CA_BUNDLE": str(self.cert.parent / "missing.crt")}, {"API_READ_TIMEOUT_SECONDS": "nan"}):
            with self.subTest(changes=changes), patch.dict(os.environ, {**self.environment, **changes}, clear=True), patch("firmware.settings.dotenv_values", return_value={}):
                with self.assertRaises(ConfigurationError):
                    load_settings()
        self.assertEqual(self.settings.api_base_url, "https://localhost:8444")
        self.assertEqual(self.settings.command_poll_base_url, "http://127.0.0.1:8081")
        self.assertNotIn(TOKEN, repr(self.settings))
        with patch.dict(os.environ, self.environment, clear=True), patch("firmware.settings.dotenv_values", return_value={"DEVICE_ID": "from-file"}) as read:
            self.assertEqual(load_settings().device_id, "room")
            read.assert_called_once_with(PROJECT_ROOT / ".env", interpolate=False)

    def test_only_polling_uses_http_and_requests_do_not_follow_redirects(self):
        command = FanCommand(str(uuid4()), FanState.ON)
        with patch("firmware.api_client.requests.Session") as factory:
            session = factory.return_value
            session.request.side_effect = [response(201), response(data={"command": {"id": command.command_id, "fan_state": "on"}}), response(204)]
            with DeviceApiClient(self.settings) as client:
                reading = self.reading()
                client.submit_reading(reading)
                self.assertEqual(client.poll_command(), command)
                client.acknowledge_command(command, FanState.ON)
            calls = session.request.call_args_list
            self.assertEqual([call.args[0] for call in calls], ["POST", "GET", "POST"])
            self.assertEqual([call.args[1] for call in calls], ["https://localhost:8444/api/devices/room/readings", "http://127.0.0.1:8081/api/devices/room/commands/pending", f"https://localhost:8444/api/devices/room/commands/{command.command_id}/ack"])
            for call in calls:
                self.assertEqual(call.kwargs["headers"]["Authorization"], "Bearer " + TOKEN)
                self.assertEqual(call.kwargs["verify"], str(self.cert))
                self.assertFalse(call.kwargs["allow_redirects"])
                self.assertNotIn(TOKEN, call.args[1])
                self.assertEqual(call.kwargs["timeout"], (3.0, 10.0))
            self.assertFalse(session.trust_env)
            session.close.assert_called_once()
        with patch("firmware.api_client.requests.Session") as factory:
            factory.return_value.request.return_value = response(302)
            with DeviceApiClient(self.settings) as client:
                with self.assertRaises(ApiError) as caught:
                    client.poll_command()
            self.assertEqual(caught.exception.status_code, 302)
            self.assertFalse(caught.exception.retryable)
            self.assertEqual(factory.return_value.request.call_count, 1)

    def test_certificate_failure_has_no_bypass_retry_or_secret_log(self):
        error = requests.exceptions.SSLError(ssl.SSLCertVerificationError("certificate rejected " + TOKEN))
        with patch("firmware.api_client.requests.Session") as factory:
            factory.return_value.request.side_effect = error
            with DeviceApiClient(self.settings) as client, self.assertLogs("firmware.api_client", level="ERROR") as captured:
                with self.assertRaises(ApiError) as caught:
                    client.submit_reading(self.reading())
            self.assertTrue(caught.exception.certificate_error)
            self.assertFalse(caught.exception.retryable)
            self.assertEqual(factory.call_count, 1)
            self.assertEqual(factory.return_value.request.call_count, 1)
            self.assertNotIn(TOKEN, " ".join(captured.output))
            self.assertNotIn(TOKEN, str(caught.exception))

    def test_failure_classification_logs_and_command_validation(self):
        with patch("firmware.api_client.requests.Session") as factory:
            session = factory.return_value
            with DeviceApiClient(self.settings) as client:
                for status, retryable in ((401, False), (429, True), (503, True)):
                    session.request.return_value = response(status, {"secret": TOKEN})
                    with self.assertLogs("firmware.api_client", level="ERROR") as captured:
                        with self.assertRaises(ApiError) as caught:
                            client.submit_reading(self.reading())
                    self.assertEqual(caught.exception.retryable, retryable)
                    self.assertNotIn(TOKEN, " ".join(captured.output))
                session.request.side_effect = requests.Timeout(TOKEN)
                with self.assertRaises(ApiError) as caught:
                    client.poll_command()
                self.assertTrue(caught.exception.retryable)
                self.assertNotIn(TOKEN, str(caught.exception))
                session.request.side_effect = None
                for data in ({}, [], {"command": {"id": "bad-id", "fan_state": "on"}}, {"command": {"id": str(uuid4()), "fan_state": "invalid"}}):
                    session.request.return_value = response(data=data)
                    with self.assertRaises(ApiError):
                        client.poll_command()
                session.request.return_value = response(data={"command": None})
                self.assertIsNone(client.poll_command())
                session.request.return_value.json.side_effect = ValueError(TOKEN)
                with self.assertRaises(ApiError) as caught:
                    client.poll_command()
                self.assertEqual(caught.exception.reason, "invalid_json")
                self.assertNotIn(TOKEN, str(caught.exception))

    def test_runtime_retains_reading_identity_until_accepted(self):
        now = [0.0]
        client = Mock()
        client.poll_command.return_value = None
        client.submit_reading.side_effect = [ApiError("transport_failure", retryable=True), None]
        runtime = DeviceRuntime(self.settings, client, clock=lambda: now[0])
        with self.assertLogs("firmware.main", level="WARNING"):
            runtime.step()
        original = client.submit_reading.call_args.args[0]
        now[0] = 2.0
        runtime.step()
        self.assertEqual(client.submit_reading.call_count, 1)
        self.assertEqual(client.poll_command.call_count, 2)
        now[0] = 5.0
        runtime.step()
        self.assertIs(client.submit_reading.call_args.args[0], original)
        self.assertEqual(client.submit_reading.call_count, 2)
        self.assertIsNone(runtime._pending_reading)

    def test_runtime_retains_acknowledgment_and_stops_on_permanent_error(self):
        now = [0.0]
        client = Mock()
        command = FanCommand(str(uuid4()), FanState.ON)
        client.poll_command.return_value = command
        client.acknowledge_command.side_effect = [ApiError("transport_failure", retryable=True), None]
        runtime = DeviceRuntime(self.settings, client, clock=lambda: now[0])
        with self.assertLogs("firmware.main", level="WARNING"):
            runtime.step()
        self.assertEqual(runtime._fan.state, FanState.ON)
        now[0] = 5.0
        runtime.step()
        self.assertEqual(client.poll_command.call_count, 1)
        self.assertEqual(client.acknowledge_command.call_count, 2)
        for call in client.acknowledge_command.call_args_list:
            self.assertEqual(call.args, (command, FanState.ON))
        self.assertIsNone(runtime._pending_command)
        runtime.stop()
        self.assertEqual(runtime._fan.state, FanState.OFF)
        client.submit_reading.side_effect = ApiError("unexpected_response", status_code=401)
        now[0] = 10.0
        with self.assertRaises(ApiError):
            runtime.step()

    def test_sensor_reproducibility_cooling_and_elapsed_time(self):
        values = dict(seed=2026, start_temperature_c=24.0, ambient_temperature_c=26.0, fan_cooling_c_per_second=0.05, noise_stddev_c=0, thermal_time_constant_seconds=300)
        first, second = TemperatureSensor(**values), TemperatureSensor(**values)
        for elapsed in (0, 1, 5, 10):
            first.advance(elapsed, fan_on=True)
            second.advance(elapsed, fan_on=True)
            self.assertEqual(first.read_celsius(), second.read_celsius())
        self.assertLess(first.read_celsius(), 24.0)
        off = TemperatureSensor(**values)
        off.advance(16, fan_on=False)
        self.assertGreater(off.read_celsius(), 24.0)
        for elapsed in (-1, float("nan")):
            with self.assertRaises(ValueError):
                first.advance(elapsed, fan_on=False)

    def test_check_config_exits_without_contacting_api(self):
        with patch("sys.argv", ["firmware.main", "--check-config"]), patch("firmware.main.load_settings", return_value=self.settings), patch("firmware.main.DeviceApiClient") as client, patch("builtins.print"):
            self.assertEqual(firmware_main(), 0)
            client.assert_not_called()
        with patch("sys.argv", ["firmware.main"]), patch("firmware.main.load_settings", side_effect=ConfigurationError("DEVICE_TOKEN is required")), patch("builtins.print"):
            self.assertEqual(firmware_main(), 2)

    def test_live_firmware_requests_reach_backend_on_expected_transports(self):
        with patch.dict(os.environ, {"APP_SECRET_KEY": "x" * 48, "DB_PASSWORD": "test-only"}, clear=True):
            backend_settings = load_backend_settings()
        app = backend_main.create_app(backend_settings)
        observed = []

        @app.before_request
        def observe_request():
            observed.append((request.method, request.path, request.scheme, request.headers.get("Authorization")))

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(self.cert, self.key)
        servers = [make_server("127.0.0.1", 0, app, threaded=True, ssl_context=context), make_server("127.0.0.1", 0, app, threaded=True)]
        threads = [threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True) for server in servers]
        settings = replace(self.settings, api_base_url=f"https://127.0.0.1:{servers[0].server_port}", command_poll_base_url=f"http://127.0.0.1:{servers[1].server_port}")
        device = {"id": "room", "token_hash": hashlib.sha256(TOKEN.encode()).hexdigest()}
        db = Mock()
        db.execute.return_value.fetchone.return_value = device
        command_id = str(uuid4())
        try:
            for thread in threads:
                thread.start()
            with patch("backend.security.get_db", return_value=db), patch.object(devices, "save_reading", return_value=({"id": uuid4()}, True)) as save, patch.object(devices, "pending_command", return_value={"id": command_id, "fan_state": "on"}), patch.object(devices, "acknowledge_command", return_value={"id": command_id, "fan_state": "on"}) as acknowledge:
                with DeviceApiClient(settings) as client:
                    client.submit_reading(self.reading())
                    command = client.poll_command()
                    self.assertEqual(command, FanCommand(command_id, FanState.ON))
                    client.acknowledge_command(command, FanState.ON)
                save.assert_called_once()
                acknowledge.assert_called_once()
                self.assertEqual([item[2] for item in observed], ["https", "http", "https"])
                self.assertTrue(all(item[3] == "Bearer " + TOKEN for item in observed))
                self.assertEqual(observed[1][1], "/api/devices/room/commands/pending")
                with DeviceApiClient(replace(settings, api_ca_bundle=self.other_cert)) as client, self.assertLogs("firmware.api_client", level="ERROR") as captured:
                    with self.assertRaises(ApiError) as caught:
                        client.submit_reading(self.reading())
                self.assertFalse(caught.exception.retryable)
                self.assertTrue(caught.exception.certificate_error)
                self.assertEqual(len(observed), 3)
                self.assertNotIn(TOKEN, " ".join(captured.output))
        finally:
            for server, thread in zip(servers, threads):
                if thread.is_alive():
                    server.shutdown()
                    thread.join(5)
                server.server_close()
        self.assertTrue(all(not thread.is_alive() for thread in threads))


if __name__ == "__main__":
    unittest.main(verbosity=2)
