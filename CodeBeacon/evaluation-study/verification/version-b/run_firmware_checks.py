"""Record firmware checks and backend regression evidence without replacing prior records."""

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
        ("compile-firmware-and-backend", [sys.executable, "-m", "compileall", "-q", str(ROOT / "firmware"), str(ROOT / "backend")]),
        ("firmware-behavior-and-live-backend-requests", [sys.executable, str(HERE / "test_firmware.py")]),
        ("backend-regression", [sys.executable, str(HERE / "test_backend.py")]),
        ("firmware-cli-help", [sys.executable, "-m", "firmware.main", "--help"]),
        ("dependency-consistency", [sys.executable, "-m", "pip", "check"]),
    ):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        checks.append({"name": name, "exit_code": result.returncode, "output": result.stdout + result.stderr})
        print(f"{name}: {'PASS' if result.returncode == 0 else 'FAIL'}")
    files = []
    for folder in ("backend", "firmware"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            files.append({
                "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                "functions": [{"name": node.name, "start": min([node.lineno] + [d.lineno for d in node.decorator_list]), "end": node.end_lineno}
                              for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
            })
    for name in ("README.md", "requirements.txt", ".env.example"):
        files.append({"path": name, "sha256": digest(ROOT / name)})
    record = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "author": "Codex author checks; not independent review",
        "source_root": ROOT.relative_to(HERE.parents[3]).as_posix(),
        "python": sys.version,
        "runtime_note": "Reused existing Version A Python environment; did not install packages or modify local application configuration.",
        "dependencies": {name: importlib.metadata.version(name) for name in ("flask", "werkzeug", "psycopg", "itsdangerous", "python-dotenv", "requests")},
        "files": files,
        "verification_files": [{"path": path.name, "sha256": digest(path)} for path in (HERE / "test_firmware.py", HERE / "test_backend.py", Path(__file__))],
        "checks": checks,
        "limitations": [
            "Nine firmware checks and ten backend checks are author verification, not independent review.",
            "Actual firmware HTTP/HTTPS requests reached Version B Flask routes on temporary loopback listeners; backend database/service operations used doubles.",
            "The live client sends its test device credential over HTTP only when polling; readings and acknowledgments use certificate-verified HTTPS.",
            "Untrusted HTTPS certificate rejected without an insecure retry; credential-bearing logs not observed in exercised failure paths.",
            "Runtime retry scheduling and fan behavior tested with fake clock and client; no continuous full-application process run or real PostgreSQL execution.",
            "Temperature and fan are simulated software interfaces; no physical hardware is exercised.",
            "Loopback-only checks do not establish remote observer access. Frontend/schema, deployment exposure review, independent review, and detector evaluation remain pending.",
            "External Excel workbook not accessed or updated. Earlier backend evidence preserved separately.",
        ],
    }
    (HERE / "firmware-check-results.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return int(any(check["exit_code"] for check in checks))


if __name__ == "__main__":
    raise SystemExit(main())
