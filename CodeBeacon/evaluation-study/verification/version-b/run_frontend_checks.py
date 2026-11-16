"""Record frontend author checks without replacing backend/firmware evidence."""

import ast
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / "app" / "version-B"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []
    for name, command in (
        ("compile-frontend", [sys.executable, "-m", "compileall", "-q", str(ROOT / "frontend")]),
        ("frontend-ui-and-flask-contract", [sys.executable, str(HERE / "test_frontend.py")]),
        ("backend-regression", [sys.executable, str(HERE / "test_backend.py")]),
        ("dependency-consistency", [sys.executable, "-m", "pip", "check"]),
    ):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        checks.append({"name": name, "exit_code": result.returncode, "output": result.stdout + result.stderr})
        print(f"{name}: {'PASS' if result.returncode == 0 else 'FAIL'}")
    files = []
    for folder in ("backend", "firmware", "frontend"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            files.append({
                "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                "functions": [{"name": node.name,
                               "start": min([node.lineno] + [d.lineno for d in node.decorator_list]),
                               "end": node.end_lineno}
                              for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
            })
    for name in ("README.md", "requirements.txt", ".env.example"):
        files.append({"path": name, "sha256": digest(ROOT / name)})
    record = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "author": "Codex author checks; not independent review",
        "source_root": ROOT.relative_to(HERE.parents[3]).as_posix(),
        "python": sys.version,
        "runtime_note": "Reused Version A's existing environment. No package installation or local settings changes.",
        "dependencies": {name: importlib.metadata.version(name) for name in (
            "streamlit", "requests", "pandas", "altair", "python-dotenv", "flask", "werkzeug",
        )},
        "files": files,
        "verification_files": [{"path": path.name, "sha256": digest(path)} for path in (
            HERE / "test_frontend.py", HERE / "test_backend.py", Path(__file__),
        )],
        "checks": checks,
        "limitations": [
            "Eight frontend tests use Streamlit AppTest with mocked API methods, mocked transport, and a real Flask test-client bridge with database/service doubles.",
            "The Flask bridge checks frontend request/response contracts, not real HTTPS transport, certificate validation, or PostgreSQL integration.",
            "Transport-option tests assert CA validation, timeouts, redirect rejection, and safe error messages using mocked Requests responses.",
            "Ten backend regression tests include local HTTP/HTTPS listeners with database doubles; they do not execute the frontend client over live TLS.",
            "No browser visual QA, timed browser fragment-refresh test, or complete running device/backend/dashboard integration performed.",
            "Version B database schema remains pending. Existing backend/firmware evidence is preserved separately.",
            "Software simulates sensor/fan behavior; no physical hardware, independent review, detector evaluation, or external workbook update.",
        ],
    }
    (HERE / "frontend-check-results.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return int(any(check["exit_code"] for check in checks))


if __name__ == "__main__":
    raise SystemExit(main())
