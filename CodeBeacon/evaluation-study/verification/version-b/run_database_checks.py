"""Exercise B against a disposable local PostgreSQL cluster, never configured databases."""

import argparse
import hashlib
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import traceback
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import psycopg
from psycopg import sql
from werkzeug.security import check_password_hash

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / "app" / "version-B"
sys.path.insert(0, str(ROOT))

from backend.database import get_db
from backend.main import create_app
from backend.settings import load_settings


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pg-bin", type=Path, default=Path("C:/Program Files/PostgreSQL/17/bin"))
    args = parser.parse_args()
    executable_suffix = ".exe" if os.name == "nt" else ""
    initdb = args.pg_bin / ("initdb" + executable_suffix)
    pg_ctl = args.pg_bin / ("pg_ctl" + executable_suffix)
    openssl = shutil.which("openssl")
    if not initdb.is_file() or not pg_ctl.is_file() or not openssl:
        parser.error("PostgreSQL initdb/pg_ctl and OpenSSL are required; set --pg-bin if needed")
    record = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "author": "Codex author checks; not independent review",
        "source_root": "CodeBeacon/evaluation-study/app/version-B",
        "checks": [], "tool_output": [], "files": [],
        "limitations": [
            "Disposable PostgreSQL cluster only; configured application database and local .env untouched.",
            "Flask test client supplies HTTPS/HTTP schemes; no live API TLS, browser, or continuous device process.",
            "Database connections use TLS require and SCRAM password authentication, not verify-full certificate identity checks.",
            "No concurrent request stress, physical hardware, independent review, detector scoring, or external workbook update.",
        ],
    }

    def run(command):
        # Windows server children can retain pipe handles after pg_ctl exits.
        with tempfile.TemporaryFile(mode="w+b") as output:
            result = subprocess.run(command, stdout=output, stderr=output, stdin=subprocess.DEVNULL,
                                    timeout=45, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            output.seek(0)
            captured = output.read().decode("utf-8", errors="replace")
        record["tool_output"].append({"tool": Path(command[0]).name, "exit_code": result.returncode,
                                      "output": captured})
        if result.returncode:
            raise RuntimeError(f"{Path(command[0]).name} failed; see recorded tool output")

    def passed(name):
        record["checks"].append({"name": name, "passed": True})
        print("PASS: " + name, flush=True)

    success = False
    try:
        with tempfile.TemporaryDirectory(prefix="room-monitor-b-db-check-") as temporary:
            temporary = Path(temporary).resolve()
            data = temporary / "data"
            password = secrets.token_urlsafe(32)
            password_file = temporary / "admin-password"
            password_file.write_text(password, encoding="utf-8")
            run([str(initdb), "-D", str(data), "-U", "study_admin", "--auth-host=scram-sha-256",
                 "--auth-local=trust", "--pwfile=" + str(password_file), "--encoding=UTF8", "--locale=C"])
            run([openssl, "req", "-x509", "-newkey", "rsa:2048", "-sha256", "-nodes", "-days", "1",
                 "-keyout", str(data / "server.key"), "-out", str(data / "server.crt"), "-subj", "/CN=localhost"])
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            with (data / "postgresql.conf").open("a", encoding="utf-8") as configuration:
                configuration.write(f"\nlisten_addresses = '127.0.0.1'\nport = {port}\nssl = on\n")
            try:
                run([str(pg_ctl), "-D", str(data), "-l", str(temporary / "server.log"), "-w", "start"])
                connection_options = dict(host="127.0.0.1", port=port, user="study_admin",
                                          password=password, sslmode="require", autocommit=True)
                app_password = secrets.token_urlsafe(32)
                with psycopg.connect(dbname="postgres", **connection_options) as admin:
                    record["server_version"] = admin.execute("SHOW server_version").fetchone()[0]
                    admin.execute(sql.SQL("CREATE ROLE room_monitor_b_app LOGIN PASSWORD {}").format(sql.Literal(app_password)))
                    admin.execute("CREATE DATABASE room_monitor_b OWNER room_monitor_b_app")
                    admin.execute("CREATE DATABASE other_version_control")
                with patch.dict(os.environ, {"APP_SECRET_KEY": secrets.token_urlsafe(48), "DB_PASSWORD": app_password}, clear=True):
                    settings = replace(load_settings(), db_host="127.0.0.1", db_port=port,
                                       db_name="room_monitor_b", db_user="room_monitor_b_app", db_sslmode="require")
                app = create_app(settings)
                app.testing = True
                with app.app_context():
                    db = get_db()
                    assert db.execute("SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()").fetchone()["ssl"]
                    assert db.execute("SELECT current_database(), current_user").fetchone() == {
                        "current_database": "room_monitor_b", "current_user": "room_monitor_b_app"}
                    db.execute((ROOT / "database/schema.sql").read_text(encoding="utf-8"))
                    tables = db.execute("SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public'").fetchall()
                    assert {r["tablename"] for r in tables} == {"user", "devices", "readings", "requests", "login_attempts"}
                    assert all(r["tableowner"] == "room_monitor_b_app" for r in tables)
                    indexes = db.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'").fetchall()
                    assert {"devices_owner_history_idx", "readings_device_history_idx", "requests_device_history_idx"} <= {r["indexname"] for r in indexes}
                passed("schema executes as non-superuser owner over TLS; exactly five tables and three history indexes")
                try:
                    with psycopg.connect(dbname="room_monitor_b", **{**connection_options, "user": "room_monitor_b_app", "password": "wrong"}):
                        raise AssertionError("Wrong database password was accepted")
                except psycopg.OperationalError as error:
                    if "password authentication failed" not in str(error):
                        raise
                passed("SCRAM rejects wrong database password")
                client = app.test_client()
                operations = set()

                def request(method, path, expected, payload=None, token=None, scheme="https"):
                    headers = {"Authorization": "Bearer " + token} if token else {}
                    response = client.open(path, method=method, base_url=scheme + "://localhost", json=payload, headers=headers)
                    assert response.status_code == expected, (method, path, response.status_code, response.json)
                    endpoint, _ = app.url_map.bind("localhost").match(path, method=method)
                    operations.add((method, endpoint))
                    return response.json

                account_password = "a sufficiently long account password"
                request("POST", "/api/accounts", 400, {"username": "alice", "password": "short"})
                for username in ("alice", "bob"):
                    request("POST", "/api/accounts", 201, {"username": username, "password": account_password})
                request("POST", "/api/accounts", 409, {"username": "alice", "password": account_password})
                login = lambda username: request("POST", "/api/accounts/login", 200, {"username": username, "password": account_password})["access_token"]
                alice, bob = login("alice"), login("bob")
                request("GET", "/api/accounts/me", 200, token=alice)
                enrollment = request("POST", "/api/devices", 201, {"name": "Office"}, bob)
                device_id, device_token = enrollment["device"]["id"], enrollment["device_token"]
                path = "/api/devices/" + device_id
                request("GET", "/api/devices", 200, token=bob)
                request("GET", path, 200, token=bob)
                request("GET", path, 404, token=alice)
                reading = {"reading_id": str(uuid4()), "recorded_at": datetime.now(timezone.utc).isoformat(),
                           "temperature_c": 24.5, "unit": "C", "fan_state": "off"}
                request("POST", path + "/readings", 401, reading)
                request("POST", path + "/readings", 201, reading, device_token)
                request("POST", path + "/readings", 200, reading, device_token)
                request("POST", path + "/readings", 409, {**reading, "temperature_c": 25}, device_token)
                assert len(request("GET", path + "/readings", 200, token=bob)["readings"]) == 1
                request("GET", path + "/readings", 404, token=alice)
                passed("accounts, enrollment, device binding, ownership reads, and reading retry persistence")
                command = request("POST", path + "/commands", 201, {"fan_state": "on"}, alice)["command"]
                assert command["requested_by"] != enrollment["device"]["owner_id"]
                request("GET", path + "/commands", 404, token=alice)
                request("GET", path + "/commands", 200, token=bob)
                request("GET", path + "/commands/pending", 401, scheme="http")
                assert request("GET", path + "/commands/pending", 200, token=device_token, scheme="http")["command"]["id"] == command["id"]
                ack = path + "/commands/" + command["id"] + "/ack"
                request("POST", ack, 409, {"fan_state": "off"}, device_token)
                first = request("POST", ack, 200, {"fan_state": "on"}, device_token)["command"]
                assert request("POST", ack, 200, {"fan_state": "on"}, device_token)["command"] == first
                assert request("GET", path + "/commands/pending", 200, token=device_token)["command"] is None
                for _ in range(7):
                    request("POST", "/api/accounts/login", 401, {"username": "alice", "password": "wrong"})
                request("PATCH", "/api/accounts/password", 400, {"current_password": account_password, "new_password": "short"}, alice)
                replacement_password = account_password + " changed"
                replacement = request("PATCH", "/api/accounts/password", 200,
                                      {"current_password": account_password, "new_password": replacement_password}, alice)
                request("GET", "/api/accounts/me", 401, token=alice)
                request("GET", "/api/accounts/me", 200, token=replacement["access_token"])
                request("POST", "/api/accounts/login", 200, {"username": "alice", "password": replacement_password})
                passed("command persistence and acknowledgment retries; B-02 cross-owner commands and B-03 unlimited guesses retained; password revocation works")
                with app.app_context():
                    db = get_db()
                    stored = db.execute('SELECT password_hash, token_version FROM "user" WHERE username = %s', ("alice",)).fetchone()
                    assert stored["password_hash"].startswith("pbkdf2:sha256:600000$")
                    assert check_password_hash(stored["password_hash"], replacement_password)
                    assert stored["token_version"] == 2
                    assert db.execute("SELECT COUNT(*) AS count FROM login_attempts").fetchone()["count"] == 0
                    token_hash = db.execute("SELECT token_hash FROM devices WHERE id = %s", (device_id,)).fetchone()["token_hash"]
                    assert token_hash == hashlib.sha256(device_token.encode()).hexdigest()
                    for statement, params, error_type in (
                        ("INSERT INTO login_attempts (bucket, failures) VALUES (%s, %s)", (4096, 0), psycopg.errors.CheckViolation),
                        ("INSERT INTO login_attempts (bucket, failures) VALUES (%s, %s)", (1, -1), psycopg.errors.CheckViolation),
                        ("UPDATE readings SET temperature_c = %s", (100,), psycopg.errors.CheckViolation),
                        ("UPDATE requests SET fan_state = %s", ("invalid",), psycopg.errors.CheckViolation),
                        ("UPDATE devices SET owner_id = %s", (uuid4(),), psycopg.errors.ForeignKeyViolation),
                    ):
                        try:
                            with db.transaction():
                                db.execute(statement, params)
                        except error_type:
                            pass
                        else:
                            raise AssertionError("Expected database constraint was not enforced")
                passed("protected password hashes, token digests, token version, and database value/foreign-key constraints")
                with psycopg.connect(dbname="other_version_control", **connection_options) as control:
                    assert control.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'").fetchone()[0] == 0
                assert len(operations) == 13, operations
                record["api_operations"] = len(operations)
                passed("all 13 API operations exercised with real PostgreSQL; separate control database remains empty")
                success = True
            finally:
                if (data / "postmaster.pid").exists():
                    run([str(pg_ctl), "-D", str(data), "-m", "fast", "-w", "stop"])
                    passed("temporary PostgreSQL server stopped")
    except Exception:
        record["error"] = traceback.format_exc()
        print(record["error"], file=sys.stderr)
        success = False
    for folder in ("database", "backend", "frontend", "firmware"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and path.suffix in {".py", ".sql"}:
                record["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)})
    record["verification_file"] = {"path": Path(__file__).name, "sha256": digest(Path(__file__))}
    record["passed"] = success
    (HERE / "database-check-results.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
