"""Compile and verify the selected study suite on independent fixtures only.

Retains exactly findings.txt/run-log.txt per attempt; temporary machine-readable
results are deleted after matching. No application cases or answer key are read.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
from urllib.parse import unquote

spec = importlib.util.spec_from_file_location("codeql_runner", Path(__file__).with_name("run-codeql.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
BASE = Path(__file__).resolve().parent


def expectations(source):
    expected = set()
    for path in source.rglob("*.py"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = re.match(r"\s*# ruleid: (.+)$", line)
            if match:
                for rule in match[1].split(","):
                    expected.add((rule.strip(), path.relative_to(source).as_posix(), number + 1))
    if not expected:
        raise ValueError("No fixture expectations found.")
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codeql", type=Path)
    args = parser.parse_args()
    cli = (args.codeql or Path(os.environ.get("LOCALAPPDATA", "")) / "CodeQL/codeql/codeql.exe").resolve()
    suite = BASE / "queries/study.qls"
    folder = runner.create_run_folder("rule-verification-practice")
    work = runner.WORK_DIR / folder.name
    source, database, report = work / "source", work / "database", work / "results.sarif"
    started, clock_start = runner.now(), time.monotonic()
    status, code, scan_exit = "FAILED / INCOMPLETE", 2, None
    print(f"Saving this attempt to: {folder}", flush=True)
    with (folder / "findings.txt").open("w", encoding="utf-8") as findings, \
            (folder / "run-log.txt").open("w", encoding="utf-8") as log:
        log.write(f"Independent CodeQL rule verification\nStart: {started.isoformat()}\n"
                  "Scope: tests/fixtures/*.py; no application inputs. Fixtures are not executed.\n"
                  "No downloads or uploads. Missing and unexpected alerts both fail verification.\n")
        env = os.environ.copy()
        env.update(NO_COLOR="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        env.pop("FORCE_COLOR", None)
        try:
            work.mkdir(parents=True)
            shutil.copytree(BASE / "tests/fixtures", source)
            expected = expectations(source)
            for path in sorted(source.rglob("*.py")):
                runner.record_hash(log, path, "Fixture SHA-256")
            for path in sorted((BASE / "queries").rglob("*")):
                if path.suffix in {".ql", ".qll", ".qls", ".yml"}:
                    runner.record_hash(log, path, "Query/configuration SHA-256")
            runner.record_hash(log, Path(__file__), "Verification procedure SHA-256")

            def checked(arguments):
                result, output = runner.run_command([str(cli), *arguments,
                    f"--common-caches={runner.WORK_DIR / 'cache'}"], log, BASE, env)
                if result:
                    raise RuntimeError(f"CodeQL {arguments[0]} exited {result}")
                return output

            checked(["version"])
            checked(["resolve", "packs"])
            resolved = checked(["resolve", "queries", str(suite), "--format=text"])
            queries = [Path(line.strip()) for line in resolved.splitlines() if line.strip().endswith(".ql")]
            if len(queries) != 14:
                raise RuntimeError(f"Expected 14 selected queries, got {len(queries)}")
            selected_ids = set()
            for query in queries:
                runner.record_hash(log, query, "Resolved query SHA-256")
                selected_ids.add(re.search(r"@id\s+(\S+)", query.read_text(encoding="utf-8"))[1])
            if {row[0] for row in expected} != selected_ids:
                raise RuntimeError("Every selected query must have positive fixtures; unknown fixture IDs are invalid.")
            checked(["query", "compile", str(suite), "--check-only", "--threads=2", "--ram=4096"])
            checked(["database", "create", str(database), "--language=python", "--build-mode=none",
                     f"--source-root={source}", "--threads=2"])
            scan_exit, _ = runner.run_command([str(cli), "database", "analyze", str(database), str(suite),
                "--format=sarifv2.1.0", f"--output={report}", "--threads=2", "--ram=4096",
                f"--common-caches={runner.WORK_DIR / 'cache'}"], log, BASE, env)
            if scan_exit:
                raise RuntimeError(f"Analysis exited {scan_exit}")
            actual = set()
            for run in json.loads(report.read_text(encoding="utf-8"))["runs"]:
                for result in run.get("results", []):
                    location = result["locations"][0]["physicalLocation"]
                    uri = unquote(location["artifactLocation"]["uri"]).replace("\\", "/")
                    key = (result["ruleId"], uri, location["region"]["startLine"])
                    actual.add(key)
                    findings.write(f"{key[0]} | {key[1]}:{key[2]} | {result['message']['text']}\n")
            missing, unexpected = expected - actual, actual - expected
            for label, rows in (("MISSING", missing), ("UNEXPECTED", unexpected)):
                for row in sorted(rows):
                    log.write(f"{label}: {row}\n")
            for rule in sorted(selected_ids):
                log.write(f"{rule}: {sum(r[0] == rule for r in expected)} positive expectations; "
                          f"{sum(r[0] == rule for r in actual)} alert locations.\n")
            log.write(f"Expected alert locations: {len(expected)}; actual: {len(actual)}; "
                      f"missing: {len(missing)}; unexpected: {len(unexpected)}\n")
            if missing or unexpected:
                raise RuntimeError("Fixture mismatch; inspect MISSING/UNEXPECTED lines.")
            status, code = "PASS / ALL 14 QUERIES; positive and negative fixtures", 0
        except KeyboardInterrupt:
            status, code = "INTERRUPTED / INCOMPLETE", 130
        except Exception as exc:
            log.write(f"Verification error: {type(exc).__name__}: {exc}\n")
            print(str(exc), file=sys.stderr)
        finally:
            if report.exists():
                report.unlink()
            log.write(f"\nEnd: {runner.now().isoformat()}\nDuration seconds: {time.monotonic() - clock_start:.2f}\n"
                      f"Status: {status}\nScanner exit code: {scan_exit}\nRunner exit code: {code}\n"
                      "Fixture verification is not an accuracy score or an independent application answer review.\n")
    print(f"{status}\nResults: {folder}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
