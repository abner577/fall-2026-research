# Scanner evaluation run guide

Use Windows PowerShell with the installed scanners. These commands scan the
Python application files in `backend`, `frontend`, and `firmware` for each version.
The application and PostgreSQL do not need to be running.

## Semgrep

### How to run

Enter the scanner folder:

```powershell
cd "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\scanners\semgrep"
```

### Commands and what to expect

Run Version A, wait for completion, then run Version B:

```powershell
python .\run-semgrep.py --case version-A --config .\rules\study.yml
$LASTEXITCODE
python .\run-semgrep.py --case version-B --config .\rules\study.yml
$LASTEXITCODE
```

Uses the 16 study rules. Findings and diagnostics appear in the terminal,
followed by the outcome and results folder.

### Where the results will be

`CodeBeacon/evaluation-study/evaluation-runs/semgrep/<attempt>/`

## CodeQL

### How to run

Enter the scanner folder:

```powershell
cd "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\scanners\codeql"
```

### Commands and what to expect

Run Version A, wait for completion, then run Version B:

```powershell
python .\run-codeql.py --case version-A --queries .\queries\study.qls
$LASTEXITCODE
python .\run-codeql.py --case version-B --queries .\queries\study.qls
$LASTEXITCODE
```

Creates an analysis database and runs the 14 study queries. Progress appears
first, then readable findings, the outcome, and the results folder.

### Where the results will be

`CodeBeacon/evaluation-study/evaluation-runs/codeql/<attempt>/`

## Snyk Code

### How to run

Enter the scanner folder. Use the authenticated study organization and confirm
its free-plan allowance before running. Snyk sends selected source to its cloud
service for analysis; these commands do not request web-dashboard publication.

```powershell
cd "C:\Users\joser\Downloads\fall-2026-research\CodeBeacon\evaluation-study\scanners\snyk-code"
```

### Commands and what to expect

Run Version A, wait for completion, then run Version B:

```powershell
python .\run-snyk-code.py --case version-A
$LASTEXITCODE
python .\run-snyk-code.py --case version-B
$LASTEXITCODE
```

Uses Snyk's built-in security checks. No rule file is required. Readable findings
and a scan summary appear in the terminal, followed by the outcome and results folder.

### Where the results will be

`CodeBeacon/evaluation-study/evaluation-runs/snyk-code/<attempt>/`

## Read the results

Every attempt automatically saves exactly two report files:

- `findings.txt`: readable scanner output and findings.
- `run-log.txt`: commands, versions, source hashes, diagnostics, timing, and outcome.

The terminal prints the exact folder. Its name includes the date, fixed EST time,
and version. Repeated attempts get numbered folders without overwriting earlier runs.
These results are saved locally and are excluded from Git by the existing ignore file.

| Runner exit (`$LASTEXITCODE`) | Meaning |
| --- | --- |
| `0` | Completed without reported findings. |
| `1` | Completed with findings. This is not a scan failure. |
| `2` | Failed or incomplete. Read the log; do not grade it as a clean scan. |
| `130` | Interrupted. Results may be incomplete. |

Use the runner outcome and inspect warnings/skipped files. A completed scan
without findings does not establish that the application has no vulnerabilities.

## Study steps

1. Before scored runs, finalize and freeze the application versions, scanner
   settings, reviewed answer key, and scoring rules. These readiness items remain
   open in [the 11-23 checklist](../../../fall-2026-research/docs/meetings/checklist/11-23-checklist.md).
2. Run each scanner on Version A and Version B using the commands above. Keep
   the code and scanner rules unchanged between runs.
3. Check each outcome and log, then retain its two original report files in the
   automatically created folder. Keep failed attempts too.
4. Compare completed findings with the reviewed answer key using the agreed
   scoring rules. Record the scanner, version, exact run-folder path, finding
   location, matching vulnerability ID, and judgment in the study grading sheet.
5. Keep grading separate from the original scanner reports. The grading template
   and its final storage location still need to be agreed; the runners save
   evidence but do not calculate study scores.
