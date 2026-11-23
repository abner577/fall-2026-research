# Scanner runners and saved results

Agreed November 23, 2026. This is the implementation guide for future agents
working on Semgrep Community Edition, CodeQL, and Snyk Code. Only the Semgrep
runner is implemented. Do not treat the other two as installed or verified.

## Shared behavior for all three scanners

Use one runner per scanner and the existing `evaluation-study/evaluation-runs/`
folder, with a subfolder for each scanner. Follow the Semgrep runner's behavior
when adding CodeQL and Snyk Code; tool-specific setup and exit codes will differ.

Each run folder must contain exactly two output files:

| File | Contents |
| --- | --- |
| `findings.txt` | The scanner's readable findings, also displayed in the terminal. |
| `run-log.txt` | Warnings, errors, scan progress, tool version, exact executed command, working directory, targets, rules/queries, exclusions, start/end timestamps, duration, scanner exit code, runner exit code, and outcome. |

Do not produce JSON, SARIF, separate metadata files, or extra report copies as
retained run outputs. This is the user's explicit November 23 simplification,
superseding earlier plans that required preserving structured scanner reports.
Keep existing historical outputs; do not delete or convert them automatically.
If a future scanner requires temporary intermediate files (for example CodeQL's
database), keep them in a separate working location, outside the run folder.

Use readable folder names, for example:

```text
evaluation-runs/semgrep/
  2026-11-23_11-30-AM_EST_practice/
    findings.txt
    run-log.txt
  2026-11-23_11-30-AM_EST_practice (1)/
    findings.txt
    run-log.txt
```

Time is **fixed EST, UTC-05:00, all year**, independent of the computer's timezone.
It does not switch to EDT in summer. Names use hours/minutes and AM/PM, without
seconds or milliseconds. The log uses precise timestamps with the UTC offset.
Number repeat names `(1)`, `(2)`, etc.; never overwrite a previous attempt.

Runners must resolve built-in paths from their own script location, without
depending on terminal variables such as `$run` or `$sg`. Launch tools with an
argument list, without a shell. Preserve failed attempts and partial findings;
an empty file after an error does not mean zero vulnerabilities. Display a final
outcome and the results folder. Capture both output streams concurrently so a
busy scanner cannot block on a full pipe. Write UTF-8 text and remove terminal
color escapes from saved output.

Record actual executable versions every time. Record local rule/query paths
and versions or hashes and source identity where practical. Semgrep records
SHA-256 hashes of local YAML rules and candidate Python files before scanning;
this is a candidate inventory, not proof every file was analyzed. Inspect the
scanner's skipped-file diagnostics. Do not edit source or rules during a run.
Treat tool warnings and omissions as limitations even when the exit code is 0/1.

Keep study configuration separate from run evidence. The intended master
constants reference is an external Word document, described in
[study-constants-document-plan.md](../../../fall-2026-research/evaluation-study-preparation/study-constants-document-plan.md).
Automatic per-run metadata belongs in `run-log.txt` so actual executions remain
traceable. Do not create a second maintained constants registry in the repository.

## Run Semgrep now

Open PowerShell. Enter this folder (the commands below assume this location):

```powershell
Set-Location "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\scanners\semgrep"
```

Python must be available, and Semgrep must be installed in this folder's `.venv`.
The runner itself uses only Python's standard library. It uses the scanner
executable in `.venv/Scripts/semgrep.exe` on Windows. There is no environment
activation requirement. If installation is needed, run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install semgrep
```

Once a version is agreed for the study, use that pinned version when recreating
the environment instead of installing an unpinned latest version.

Run the separate practice case:

```powershell
python .\run-semgrep.py --case practice
$LASTEXITCODE
```

This uses `rules/practice.yml` against `practice/tls_example.py`. Expected:
one finding on `verify=False`, none on `verify=True`, and runner exit code **1**.
This runner deliberately supplies `--error`, unlike the earlier manual tutorial:

| Runner exit code | Meaning |
| --- | --- |
| `0` | Scanner completed without findings. Check progress and skipped-file details. |
| `1` | Scanner completed with findings; this is an expected result, not a crash. |
| `2` | Setup/scan failed or was incomplete; consult the log. |
| `130` | Interrupted by the user; results may be incomplete. |

The log retains the actual scanner exit code separately. When the version check
or path validation fails before scanning, it records that no scan exit code is
available. Command-line argument errors are rejected before a run is created.

The runner displays findings and diagnostics while saving them. Semgrep can
buffer its findings until analysis finishes, so progress may appear first.

## Inspect the two files

The terminal prints the exact results folder. To open the newest attempt:

```powershell
$latest = Get-ChildItem "..\..\evaluation-runs\semgrep" -Directory |
    Sort-Object CreationTimeUtc -Descending |
    Select-Object -First 1

Get-Content (Join-Path $latest.FullName "findings.txt") -Encoding UTF8
Get-Content (Join-Path $latest.FullName "run-log.txt") -Encoding UTF8
```

For a longer log, use `notepad` instead of `Get-Content` with the same path.
To check completion quickly:

```powershell
Get-Content (Join-Path $latest.FullName "run-log.txt") -Encoding UTF8 -Tail 10
```

No transcript or manual copying is needed. A failed launch still creates both
files, provided the results folder itself is writable. Read `run-log.txt` first
if findings are empty.

## Application scans and rule selection

Version A and B require an explicit local configuration. For example, these
commands use the current practice rule only to check the application layout:

```powershell
python .\run-semgrep.py --case version-A --config .\rules\practice.yml
python .\run-semgrep.py --case version-B --config .\rules\practice.yml
```

These examples are not scored study runs or complete weakness coverage. They
are not executed automatically. Select and test the research rules on separate
practice cases before scored runs. Replace the `--config` argument with your
chosen local YAML file or directory when it is ready. Relative custom paths
resolve from your terminal's current directory; built-in paths do not.

The runner analyzes only Python files under the selected version's `backend`,
`frontend`, and `firmware` directories. It excludes `.venv`, `__pycache__`,
`.local`, `.git`, and `.env`. Semgrep's default ignore, size, and timeout rules
still apply and are reported in verbose diagnostics. SQL, README files, runtime
credentials, the answer key, and research notes are outside this Python scope.
Review the common scope with the other scanners before freezing the study.

To use a different installation, supply its executable explicitly:

```powershell
python .\run-semgrep.py --case practice --semgrep "C:\path\to\semgrep.exe"
```

The scan command uses `--oss-only --text --strict --error --metrics=off
--disable-version-check --verbose`, the selected local config, explicit Python
scope/exclusions, and target paths. The exact executable command is saved in the
log in PowerShell syntax on Windows. No account login, source execution,
autofix, or report upload is requested by the runner.

## Verification and remaining work

On November 23 the installed Semgrep distribution was 1.186.0. The practice
runner completed with the expected one finding at line 5 and exit code 1.
The sandbox's version command failed with
`ca_certs_iter_on_anchors: CertOpenSystemStore returned NULL`; the runner retained
the failed attempt, and running outside that sandbox succeeded. A terminal
encoding failure found during implementation was corrected; earlier failed
attempt folders remain as history. If that certificate-store error appears in
another environment, consult the saved diagnostics rather than treating it as
an empty successful scan or disabling TLS verification.

Seven temporary verification checks also passed: concurrent stdout/stderr capture
and Unicode/color handling, success with/without findings, scan failure, version
failure, missing executable, required explicit application configuration, and
EST/repeat-name behavior. These checks used controlled subprocess outputs for
failure/status scenarios; only the separate practice scan above used real Semgrep.

This verifies installation and practice reporting, not full ten-target coverage,
application integration, independent case review, or readiness for scored runs.
No application-version scan is claimed by this change.

Future agents should implement CodeQL and Snyk Code with the same two-file and
EST naming contract, preserving their different exit-code meanings and query
configuration. Use Snyk's free plan only. Keep practice and scored attempts
explicitly distinguishable, withhold answer keys/injection notes, and do not
tune detector rules against scored-case outputs. Record rule sources, applicable
usage terms, and coverage gaps when selecting final checks.

Reference: [Semgrep CLI options and exit codes](https://docs.semgrep.dev/cli-reference).
