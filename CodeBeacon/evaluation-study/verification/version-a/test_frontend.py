"""Focused frontend checks; no database or running server is required."""

import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from streamlit.testing.v1 import AppTest

PROJECT = Path(__file__).resolve().parents[2] / "app" / "version-A"
sys.path.insert(0, str(PROJECT))

from frontend.api_client import ApiClient, ApiError, ConfigurationError, load_settings


class FrontendChecks(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        certificate = Path(temporary.name) / "ca.crt"
        certificate.write_text("Certificate placeholder; network calls are mocked.", encoding="utf-8")
        environment = patch.dict("os.environ", {
            "API_BASE_URL": "https://localhost:8443", "API_CA_BUNDLE": str(certificate),
            "API_CONNECT_TIMEOUT_SECONDS": "3", "API_READ_TIMEOUT_SECONDS": "10",
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.settings = load_settings()
        self.now = datetime.now(timezone.utc).isoformat()
        self.account = {"id": "account-1", "username": "alice", "created_at": self.now}
        self.session = {"access_token": "account-token", "expires_in": 3600, "account": self.account}
        self.device = {"id": "device-1", "name": "Office", "created_at": self.now}

    def mock_method(self, name, **kwargs):
        patched = patch.object(ApiClient, name, **kwargs)
        result = patched.start()
        self.addCleanup(patched.stop)
        return result

    def app(self, signed_in=False):
        app = AppTest.from_file(str(PROJECT / "frontend" / "main.py"), default_timeout=20)
        if signed_in:
            app.session_state["auth"] = {
                "access_token": "account-token", "expires_at": time.monotonic() + 3600,
                "account": self.account,
            }
        return app

    def assert_healthy(self, app):
        self.assertFalse(app.exception, [error.value for error in app.exception])

    def test_https_transport_and_failures(self):
        with patch.dict("os.environ", {"API_BASE_URL": "http://localhost:8443"}):
            with self.assertRaises(ConfigurationError):
                load_settings()
        response = Mock(status_code=200, headers={})
        response.json.return_value = {"readings": []}
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        with patch("requests.Session.request", return_value=response) as exchange:
            with ApiClient(self.settings, "private-account-token") as client:
                self.assertEqual(client.readings("device-1"), [])
                args, options = exchange.call_args
                self.assertEqual(args, ("GET", "https://localhost:8443/api/devices/device-1/readings"))
                self.assertEqual(options["headers"]["Authorization"], "Bearer private-account-token")
                self.assertEqual(options["verify"], str(self.settings.api_ca_bundle))
                self.assertEqual(options["timeout"], (3, 10))
                self.assertFalse(options["allow_redirects"])
                client.login("alice", "password")
                self.assertNotIn("Authorization", exchange.call_args.kwargs["headers"])
                response.status_code = 429
                response.headers = {"Retry-After": "300"}
                response.json.return_value = {"error": {"message": "Too many login attempts"}}
                with self.assertRaises(ApiError) as raised:
                    client.login("alice", "password")
                self.assertEqual((raised.exception.status_code, raised.exception.retry_after), (429, 300))
                response.status_code = 302
                with self.assertRaisesRegex(ApiError, "redirect"):
                    client.current_account()
        with patch("requests.Session.request", side_effect=requests.exceptions.SSLError("private-account-token")) as exchange:
            with ApiClient(self.settings, "private-account-token") as client:
                with self.assertRaisesRegex(ApiError, "certificate") as raised:
                    client.current_account()
                self.assertNotIn("private-account-token", str(raised.exception))
                self.assertEqual(exchange.call_count, 1)

    def test_account_registration_login_password_change_and_sign_out(self):
        register = self.mock_method("register", return_value={"account": self.account})
        login = self.mock_method("login", return_value=self.session)
        self.mock_method("current_account", return_value=self.account)
        self.mock_method("list_devices", return_value=[])
        change = self.mock_method("change_password", return_value={**self.session, "access_token": "replacement-token"})
        app = self.app().run()
        self.assert_healthy(app)
        app.segmented_control(key="access_mode").set_value("Create account").run()
        app.text_input(key="login_username").set_value("alice")
        app.text_input(key="login_password").set_value("a long account password")
        app.text_input(key="register_confirmation").set_value("a long account password")
        app.form_submit_button[0].click().run()
        self.assert_healthy(app)
        register.assert_called_once_with("alice", "a long account password")
        self.assertTrue(app.success)
        app.segmented_control(key="access_mode").set_value("Sign in").run()
        app.text_input(key="login_username").set_value("alice")
        app.text_input(key="login_password").set_value("a long account password")
        app.form_submit_button[0].click().run()
        self.assert_healthy(app)
        login.assert_called_once_with("alice", "a long account password")
        self.assertEqual(app.session_state["auth"]["access_token"], "account-token")
        app.radio(key="workspace").set_value("Account settings").run()
        app.text_input(key="current_password").set_value("a long account password")
        app.text_input(key="new_password").set_value("a")
        app.text_input(key="confirm_new_password").set_value("a")
        app.form_submit_button[0].click().run()
        self.assert_healthy(app)
        change.assert_called_once_with("a long account password", "a")
        self.assertEqual(app.session_state["auth"]["access_token"], "replacement-token")
        next(button for button in app.button if button.label == "Sign out").click().run()
        self.assert_healthy(app)
        self.assertIsNone(app.session_state["auth"])
        self.assertEqual(app.text_input(key="login_password").value, "")

    def test_device_enrollment_readings_and_command_acknowledgment(self):
        self.mock_method("current_account", return_value=self.account)
        listing = self.mock_method("list_devices", return_value=[])
        enrollment = self.mock_method("enroll_device", return_value={"device": self.device, "device_token": "issued-token"})
        reading = {"id": "reading-1", "recorded_at": self.now, "received_at": self.now, "temperature_c": 24.5, "fan_state": "off"}
        detail = self.mock_method("device_detail", return_value={"device": self.device, "latest_reading": reading})
        self.mock_method("readings", return_value=[reading])
        history = self.mock_method("commands", return_value=[])
        command = {"id": "command-1", "fan_state": "on", "created_at": self.now, "acknowledged_at": None}
        submit = self.mock_method("request_fan", return_value=command)
        app = self.app(signed_in=True).run()
        self.assert_healthy(app)
        self.assertTrue(any("first device" in message.value for message in app.info))
        listing.return_value = [self.device]
        app.text_input(key="device_name").set_value("Office")
        app.form_submit_button[0].click().run()
        self.assert_healthy(app)
        enrollment.assert_called_once_with("Office")
        self.assertEqual(app.text_input(key="issued_device_token").value, "issued-token")
        self.assertEqual([metric.value for metric in app.metric], ["24.5 °C", "Off", "Recent"])
        self.assertEqual(len(app.dataframe[0].value), 1)
        next(button for button in app.button if button.label == "I have saved these credentials").click().run()
        self.assertNotIn("enrollment", app.session_state)
        self.assertNotIn("issued_device_token", app.session_state)
        app.segmented_control[0].set_value("on")
        next(button for button in app.form_submit_button if button.label == "Send fan command").click().run()
        self.assert_healthy(app)
        submit.assert_called_once_with("device-1", "on")
        self.assertEqual(app.metric[1].value, "Off")
        self.assertEqual(app.dataframe[1].value.iloc[0]["Status"], "Pending")
        history.return_value = [{**command, "acknowledged_at": self.now}]
        detail.return_value = {"device": self.device, "latest_reading": {**reading, "fan_state": "on"}}
        app.button(key="refresh_readings").click().run()
        self.assert_healthy(app)
        self.assertEqual(app.metric[1].value, "On")
        self.assertEqual(app.dataframe[1].value.iloc[0]["Status"], "Acknowledged")

    def test_expired_and_revoked_sessions_clear_credentials(self):
        current = self.mock_method("current_account", side_effect=ApiError("Expired token", status_code=401))
        app = self.app(signed_in=True)
        app.session_state["enrollment"] = {"device_token": "private-device-token"}
        app.run()
        self.assert_healthy(app)
        self.assertIsNone(app.session_state["auth"])
        self.assertNotIn("enrollment", app.session_state)
        current.assert_called_once()
        current.reset_mock()
        other = self.app(signed_in=True)
        other.session_state["auth"] = {**other.session_state["auth"], "expires_at": time.monotonic() - 1}
        other.run()
        self.assert_healthy(other)
        self.assertIsNone(other.session_state["auth"])
        current.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
