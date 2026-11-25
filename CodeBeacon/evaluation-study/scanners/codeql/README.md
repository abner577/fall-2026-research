# Run CodeQL

CodeQL has a study suite with five unchanged upstream checks and nine custom
queries. The original one-query TLS installation check remains the default.
Query purposes, CWE tags, provenance and coverage limits live in
[queries/study.qls](queries/study.qls) and the individual
[custom queries](queries/custom/). They follow the
[agreed rule-writing approach](../scanner-rule-approach.md), independently of
application names, secret values, placement notes or application findings.

## Simple practice command

Open a normal PowerShell window and run:

```powershell
Set-Location "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\scanners\codeql"
python .\run-codeql.py --case practice
$LASTEXITCODE
```

No environment activation, manually created database, terminal variables, or
running application is needed. Built-in paths resolve from the script location.
Python and the installed CodeQL bundle are required. On this machine the runner
uses `%LOCALAPPDATA%\CodeQL\codeql\codeql.exe` (the native executable, not a shell
wrapper). An alternate installation can be supplied with `--codeql`:

```powershell
python .\run-codeql.py --case practice --codeql "C:\path\to\codeql.exe"
```

## What happens

1. A unique run folder is created under `../../evaluation-runs/codeql/`, using
   fixed EST (UTC-05:00), minutes, AM/PM, and numbered repeats without overwrites.
2. Python files are copied into a separate source snapshot under `.work/`.
   Source hashes, scope, and exclusions are recorded in the log.
3. The runner checks CodeQL's version, available packs/languages, and the actual
   queries selected by the suite. It records query hashes and pack information.
4. CodeQL creates a fresh Python database from that snapshot. This is an analysis
   database, unrelated to PostgreSQL. No database server or application is started.
5. The built-in certificate verification query runs against the database.
6. The temporary CSV is converted into readable text in `findings.txt`, displayed
   in the terminal, and removed. Both diagnostic streams go to `run-log.txt`.
7. Default practice verification requires exactly one alert at
   `tls_example.py:5`: `verify=False` is flagged and `verify=True` is unflagged.

| File/folder | Purpose |
| --- | --- |
| `run-codeql.py` | Runs the entire local procedure and saves evidence. |
| `practice/tls_example.py` | Independent unsafe/safe TLS examples, analyzed without executing them. |
| `queries/practice.qls` | Selects only the upstream `py/request-without-cert-validation` query. Not a study suite. |
| `queries/study.qls` | Selects five upstream checks at `codeql/python-queries` 1.9.1 and nine newly authored custom checks. |
| `queries/qlpack.yml` | Custom pack version 1.0.0; exact dependency `codeql/python-all` 7.2.10. Uses the installed bundle; no pack downloads. |
| `queries/lib/Study.qll` | Shared import/API, naming, URL, password-KDF and configuration helpers. Hashed with queries in run logs. |
| `tests/fixtures/examples.py` | Separate positive and negative examples for every selected study query. Not application code. |
| `verify-study.py` | Compiles the suite, extracts only fixtures, and compares native query IDs/alert lines to expectations. |
| `.work/<attempt>/source/` | Exact Python snapshot supplied to CodeQL. |
| `.work/<attempt>/database/` | Database, CodeQL internal logs, and analysis caches for inspection. Rebuilt on every run. |
| `.gitignore` | Keeps `.work/` out of Git. |
| `test_runner.py` | Eleven infrastructure checks using simulated scanner responses and a real subprocess stream check. |

The only retained files in each **results** folder are `findings.txt` and
`run-log.txt`. CodeQL database internals are working files outside that folder.
The study's existing `.gitignore` also excludes `evaluation-runs/` from Git.
Keep local run evidence; it is not automatically published with a commit.

## Read the result

The runner prints the results folder and database location. To open the newest
attempt from this CodeQL directory:

```powershell
$latest = Get-ChildItem "..\..\evaluation-runs\codeql" -Directory |
    Sort-Object CreationTimeUtc -Descending |
    Select-Object -First 1

Get-Content (Join-Path $latest.FullName "findings.txt") -Encoding UTF8
Get-Content (Join-Path $latest.FullName "run-log.txt") -Encoding UTF8 -Tail 12
```

Use `notepad` with the same paths to read the full files.

| Runner exit code | Meaning |
| --- | --- |
| `0` | Completed without findings (possible with explicitly supplied queries). |
| `1` | Completed with findings; expected for default practice. |
| `2` | Setup, extraction, analysis, report processing, or practice verification failed. |
| `130` | Interrupted; any findings are partial. |

CodeQL itself normally returns **0** for successful analysis even with findings.
The runner maps this to **1** when findings exist, matching the Semgrep interface.
Each command's real exit code remains in the log. Failed and interrupted attempts
remain available; empty findings after failure do not establish target absence.
The readable report preserves the native alert's name, severity, description,
message, and location. It does not invent CWE or query-ID fields absent from CSV;
the selected query identity and provenance are separately recorded in the log.

## Study queries and application commands

The runner requires an explicit `--queries` selection for application cases:

```powershell
python .\run-codeql.py --case version-A --queries .\queries\study.qls
python .\run-codeql.py --case version-B --queries .\queries\study.qls
```

These commands are provided for later execution. Query development and fixture
verification do not run or score either application version. Do not change
queries in response to missed application findings. The same ten target
categories remain in scope; there is no query for general missing authorization
(V7/CWE-862). Authentication (V6) and repeated-attempt restrictions (V10) cover
explicit Flask-Login/Flask-Limiter disabling only. Missing custom checks remain
gaps. Multiple queries can report the same location; matching and duplicate
treatment still belong to the future scoring procedure.

Repeat independent verification from this directory:

```powershell
python .\verify-study.py
python .\test_runner.py
```

`verify-study.py` returns 0 only when all selected queries compile and every
annotated alert location matches, with no unexpected alerts anywhere in the
fixtures. It does not execute the fixture Python. It uses temporary SARIF solely
to match native query IDs and locations, renders findings to text, then deletes
the intermediate file in `finally`. Only the two agreed text files remain in
the results folder. Snapshots, databases and compilation caches remain under
`.work/`. Each attempt, including failure, receives its own EST/repeat name.
The verification command uses two threads and a 4 GB analysis limit; the regular
runner keeps its existing 2 GB limit. All commands and diagnostics are logged.

Upstream queries are selected unchanged from the installed bundle at version
1.9.1, build SHA `ceeaafac4e629e0e39de04d40c719d7d18b4b612`; Python libraries
are 7.2.10. Their original query IDs and CWE metadata are retained. The CodeQL
query/library sources use MIT terms; the CLI has separate academic-research use
terms linked in the suite. Custom query source is newly authored QL, not a copy
of the Semgrep rule objects. No full vulnerability-coverage claim follows from
this selection. Built-in sensitive-data modeling and custom name heuristics can
miss unknown APIs and produce audit false alarms; inspect each query's limits.

Only `.py` files from `backend`, `frontend`, and `firmware` are staged, preserving
relative paths. `.venv`, `__pycache__`, `.local`, `.git`, `.env`, and symlinks are
excluded. SQL, credentials, answer keys, and research notes are not copied.
CodeQL's own extraction/modeling limits still apply: a staged-file inventory
does not prove every file or framework feature was analyzed. Inspect diagnostics
before interpreting a successful command or zero findings as useful evidence.
No application accuracy or complete study-target coverage is claimed.

## Verification record

Study-query verification, November 23, 2026: all **14 selected queries** compile
and pass independent fixtures, with **36 expected query/location matches,
zero missing and zero unexpected alerts**. Negative controls include environment
credentials, empty literal values, eight-character length floors, ordinary
checksums, password-KDF SQL writes, HTTPS and loopback URLs, ordinary output,
cryptographic randomness, verified TLS, and enabled enforcement settings.
Evidence: `../../evaluation-runs/codeql/2026-11-23_05-03-PM_EST_rule-verification-practice/`.
Only `findings.txt` and `run-log.txt` remain there; temporary SARIF was removed.
The source snapshot and database are in the corresponding `.work/` directory.
No application version or placement record was read to design or tune queries;
no application scan, independent answer review or scored study was performed.

The initial `05-00-PM` fixture attempt compiled all queries but failed Python
discovery in the restricted sandbox. It remains as failed evidence. The same
verification command succeeded outside the sandbox with Python 3.14.0 and
extractor 7.2.1. Discovery diagnostics include an unavailable Python 2 probe;
Python 3 extraction of `examples.py` succeeded. Standard-library skipping and
a query-loading cache warning are recorded in the successful log. These do not
establish support for every application API or runtime feature. Compilation
caches are now explicitly directed to `.work/cache` to keep working writes in
the scanner directory.

Regression verification after adding the suite: the unchanged default TLS
practice check still reports exactly one unsafe call at line 5 and leaves the
safe call unflagged (runner exit 1, scanner exit 0). Evidence:
`../../evaluation-runs/codeql/2026-11-23_05-06-PM_EST_practice/`.

November 23, 2026: CodeQL CLI **2.27.5**, `codeql/python-queries` **1.9.1**, and
`codeql/python-all` **7.2.10**. The real practice run created its Python database
and returned exactly one alert on the unsafe call at line 5. The safe call was
unflagged. Evidence: `../../evaluation-runs/codeql/2026-11-23_04-46-PM_EST_practice/`.
Eleven infrastructure checks pass (including helper-library hash capture):

```powershell
python .\test_runner.py
```

The earlier `04-45-PM` restricted-sandbox attempt failed during Python discovery:
`No installed Python found!`. The Windows launcher could not discover registered
Python there. The same runner succeeded outside the sandbox without installing
Python or changing the CodeQL bundle. If this recurs in a restricted terminal,
use normal Windows PowerShell and inspect the failed attempt's log.

CodeQL also emitted a non-fatal warning that the 2 GB analysis limit did not
allow query-loading stage caching; analysis still completed. Practice verification
is not an accuracy score, independent answer-key review, or study readiness.

References: [CodeQL setup](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/scan-from-the-command-line/set-up-codeql-cli),
[database creation](https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-cli-manual/database-create),
[CSV fields](https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-cli/csv-output),
[practice query](https://codeql.github.com/codeql-query-help/python/py-request-without-cert-validation/).
