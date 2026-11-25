"""Run Snyk Code with terminal findings and exactly two saved text files.

Scans a Python-only snapshot of practice or the selected application version.
Analysis uses Snyk's cloud service; no --report/dashboard publication is requested.
"""
import argparse
import hashlib
import os
from pathlib import Path
import queue
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone

BASE_DIR = Path(__file__).resolve().parent
STUDY_DIR = BASE_DIR.parent.parent
OUTPUT_DIR = STUDY_DIR / "evaluation-runs" / "snyk-code"
WORK_DIR = BASE_DIR / ".work"
EST = timezone(timedelta(hours=-5), "EST")
EXCLUSIONS = {".venv", "__pycache__", ".local", ".git", ".env"}
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def now():
    return datetime.now(EST)


def command_text(command):
    # PowerShell display only; execution always uses an argument list, no shell.
    if os.name == "nt":
        return "& " + " ".join("'" + arg.replace("'", "''") + "'" for arg in command)
    return shlex.join(command)


def create_run_folder(case):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{now():%Y-%m-%d_%I-%M-%p}_EST_{case}"
    index = 0
    while True:
        suffix = f" ({index})" if index else ""
        folder = OUTPUT_DIR / (stem + suffix)
        try:
            folder.mkdir()
            return folder
        except FileExistsError:
            index += 1


def stream_scan(command, env, findings, log, cwd=BASE_DIR):
    """Drain both pipes concurrently, saving and displaying their original text."""
    events = queue.Queue()
    process = subprocess.Popen(
        command, cwd=cwd, env=env, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
    )

    def read_stream(name, pipe):
        try:
            for line in pipe:
                events.put((name, line))
        finally:
            pipe.close()
            events.put((name, None))

    threads = []
    for name, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
        thread = threading.Thread(target=read_stream, args=(name, pipe), daemon=True)
        thread.start()
        threads.append(thread)
    try:
        finished = 0
        while finished < 2:
            name, line = events.get()
            if line is None:
                finished += 1
                continue
            line = ANSI_ESCAPE.sub("", line)
            destination = findings if name == "stdout" else log
            terminal = sys.stdout if name == "stdout" else sys.stderr
            destination.write(line)
            destination.flush()
            terminal.write(line)
            terminal.flush()
        return process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for thread in threads:
            thread.join(timeout=5)


def stage_sources(case, destination, log):
    """Copy only Python inputs, preserving their relative paths and logging hashes."""
    root = BASE_DIR / "practice" if case == "practice" else STUDY_DIR / "app" / case
    targets = [root] if case == "practice" else [root / name for name in
                                               ("backend", "frontend", "firmware")]
    count = 0
    for target in targets:
        if not target.is_dir():
            raise FileNotFoundError(f"Missing source directory: {target}")
        for current, dirs, names in os.walk(target, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUSIONS and
                             not (Path(current) / d).is_symlink())
            for name in sorted(names):
                original = Path(current) / name
                if original.suffix.lower() != ".py" or original.is_symlink():
                    continue
                relative = original.relative_to(root)
                copied = destination / relative
                copied.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original, copied)
                log.write(f"Source snapshot SHA-256: {hashlib.sha256(copied.read_bytes()).hexdigest()}  {original} => {relative.as_posix()}\n")
                count += 1
    if not count:
        raise RuntimeError("No Python source files selected; refusing an empty scan.")
    log.write(f"Staged Python file count: {count}\n"
              "This inventory is not proof all files were extracted; review Snyk diagnostics.\n")
    log.flush()


def main(argv=None):
    for terminal in (sys.stdout, sys.stderr):
        if hasattr(terminal, "reconfigure"):
            terminal.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("practice", "version-A", "version-B"), default="practice")
    parser.add_argument("--snyk", type=Path, help="Native CLI executable; relative to your terminal.")
    parser.add_argument("--org", help="Snyk organization ID or slug; otherwise uses your configured organization.")
    args = parser.parse_args(argv)
    local = BASE_DIR / ".tools" / ("snyk.exe" if os.name == "nt" else "snyk")
    executable = (args.snyk.resolve() if args.snyk else local if local.is_file() else
                  Path(shutil.which("snyk.exe" if os.name == "nt" else "snyk") or local)).resolve()
    folder = create_run_folder(args.case)
    source = WORK_DIR / folder.name / "source"
    command = [str(executable), "code", "test", str(source), "--severity-threshold=low"]
    if args.org:
        command.append(f"--org={args.org}")
    started, clock_start = now(), time.monotonic()
    scan_exit, runner_exit, status = None, 2, "FAILED / NOT STARTED"
    env = os.environ.copy()
    env.update(NO_COLOR="1", FORCE_COLOR="0", CI="1")
    print(f"Saving this attempt to: {folder}", flush=True)
    with (folder / "findings.txt").open("w", encoding="utf-8") as findings, \
            (folder / "run-log.txt").open("w", encoding="utf-8") as log:
        log.write(f"Snyk Code run\nCase: {args.case}\nStart: {started.isoformat()} (EST)\n"
                  f"Python: {sys.version}\nExecutable: {executable}\nWorking directory: {source}\n"
                  f"Organization: {args.org or '(CLI/account configured default)'}\n"
                  "Scope: Python snapshot; application targets backend/frontend/firmware.\n"
                  f"Excluded directories: {', '.join(sorted(EXCLUSIONS))}; symlinks excluded.\n"
                  "SQL, environment files, research notes, answer keys, and non-Python files are not copied.\n"
                  "Rules: Snyk-managed built-in security checks; no custom rule file.\n"
                  "The CLI version does not pin the cloud engine/rules. Snyk ignores and analysis limits apply.\n"
                  "No local .snyk/.gitignore policy is copied; account policies may still affect results.\n"
                  "Cloud analysis uploads the selected source; --report is deliberately omitted.\n"
                  "No source execution, dependency scan, autofix, or dashboard publication requested.\n"
                  "Free plan only; this runner does not verify account quota or purchase capacity.\n"
                  "Environment overrides: NO_COLOR=1, FORCE_COLOR=0, CI=1\n"
                  f"Exact scan command:\n{command_text(command)}\n")
        try:
            if not executable.is_file():
                raise FileNotFoundError(f"Snyk CLI not found: {executable}; see snyk-code/README.md or use --snyk.")
            if os.name == "nt" and executable.suffix.lower() != ".exe":
                raise ValueError("Use the native Snyk .exe on Windows, not an npm .cmd/.ps1 shim.")
            source.mkdir(parents=True, exist_ok=False)
            stage_sources(args.case, source, log)
            version_command = [str(executable), "--version"]
            log.write(f"\nVersion command: {command_text(version_command)}\n")
            log.flush()
            version = subprocess.run(version_command, cwd=source, env=env, capture_output=True,
                                     text=True, encoding="utf-8", errors="replace", timeout=30)
            log.write(ANSI_ESCAPE.sub("", f"Version stdout:\n{version.stdout}\nVersion stderr:\n{version.stderr}\n"
                      f"Version command exit code: {version.returncode}\n"))
            if version.returncode != 0 or not version.stdout.strip():
                raise RuntimeError("Snyk version check failed; see diagnostics above.")
            log.write(f"Tool version: {ANSI_ESCAPE.sub('', version.stdout.strip())}\n"
                      "\n--- Scanner warnings, errors, and progress (stderr) ---\n")
            log.flush()
            status = "FAILED / INCOMPLETE; any findings are partial"
            scan_exit = stream_scan(command, env, findings, log, cwd=source)
            runner_exit = scan_exit if scan_exit in (0, 1) else 2
            status = {0: "COMPLETED / NO FINDINGS", 1: "COMPLETED / FINDINGS REPORTED"}.get(
                scan_exit, "FAILED / INCOMPLETE; any findings are partial")
            if scan_exit == 3:
                log.write("No supported source detected; this is a failed scan, not a clean result.\n")
            if scan_exit == 0:
                text = "No findings reported. Review run-log.txt and scanner output for scope/omissions.\n"
                findings.write(text)
                print(text, end="", flush=True)
            if args.case == "practice" and scan_exit in (0, 1):
                log.write("Practice review required: unsafe verify=False at tls_example.py:6 should be flagged;\n"
                          "safe verify=True at line 10 should not. A completed scan is not a fixture PASS.\n")
        except KeyboardInterrupt:
            runner_exit, status = 130, "INTERRUPTED / INCOMPLETE; any findings are partial"
            log.write("\nRunner: interrupted by user.\n")
        except Exception as exc:
            status = "FAILED / INCOMPLETE; any findings are partial"
            log.write(f"\nRunner error: {type(exc).__name__}: {exc}\n")
            print(f"Run failed: {exc}", file=sys.stderr)
        finally:
            log.write(f"\n--- Run outcome ---\nEnd: {now().isoformat()} (EST)\n"
                      f"Duration seconds: {time.monotonic() - clock_start:.2f}\nStatus: {status}\n"
                      f"Scanner exit code: {scan_exit if scan_exit is not None else 'NOT AVAILABLE (scan not completed)'}\n"
                      f"Runner exit code: {runner_exit}\n"
                      "An empty findings file is meaningful only when the scan completed.\n")
    print(f"{status}\nResults: {folder}", flush=True)
    return runner_exit


if __name__ == "__main__":
    sys.exit(main())


