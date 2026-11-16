# Version B firmware implementation

Recorded November 16, 2026. All five agreed firmware modules now exist at
`CodeBeacon/evaluation-study/app/version-B/firmware/`. They retain Version A's
filenames and responsibilities. Backend source is unchanged by this step.
Database and frontend source remain pending. No local `.env`, real credentials,
configured database, or external Excel workbook was changed.

This record describes author checks, not independent review or a frozen scored
answer key. The temperature sensor and fan are software simulations behind
device interfaces; no physical hardware is exercised. Detector inputs retain
ordinary device-client language under the project writing rule.

## Files and behavior

| File | Responsibility |
| --- | --- |
| `firmware/main.py` | Runs the device, schedules readings/polls, retains pending readings and acknowledgments across transient failures, configures rotated logs, and stops the fan locally on shutdown. |
| `firmware/settings.py` | Loads this version's `.env` explicitly, applies process-environment overrides, requires device identity/token, validates API origins, CA file existence, timings, logging, and sensor parameters. |
| `firmware/api_client.py` | Sends authenticated readings and acknowledgments over HTTPS, polls commands over HTTP, validates responses, rejects redirects, classifies failures, and logs safe status details. |
| `firmware/temperature_sensor.py` | Implements the same first-order room-temperature model and seeded measurement noise as A. |
| `firmware/fan.py` | Maintains the same on/off actuator interface as A. |

`main.py`, `temperature_sensor.py`, and `fan.py` retain A's source behavior.
Changes are localized to settings and API communication. No additional package
dependencies or source files were introduced inside the firmware folder.

Readings default to every five seconds, polling every two seconds, and transient
retry delays to five seconds. A failed reading retains its original UUID,
timestamp, temperature, and fan state until accepted. A command is applied
before acknowledgment; an acknowledgment retry keeps that command's ID and
pauses further polling. A bounded sequential request can delay another due
operation. Pending work is in memory and lost at process exit. Shutdown turns
the fan off locally without sending a final reading or acknowledgment.

HTTP 408/429/5xx responses and transport failures are retryable. TLS errors,
permanent API rejection, unexpected redirects, malformed JSON, and invalid
command payloads stop the affected runtime via `ApiError`. The command-line
runner returns 1 for API rejection and 2 for invalid settings. Configuration
checking does not contact the API, confirm enrollment, or parse the CA file.

## Exact B-01 / V4 record: unencrypted command polling

Paths and line ranges below are relative to `version-B/`:

| Location | Role |
| --- | --- |
| `firmware/settings.py`, `origin`, lines 58–73; origin selections lines 75–76 | General API origin must be HTTPS; command-poll origin must be HTTP. Polling defaults to `http://127.0.0.1:8081`. Origins reject embedded credentials, paths, query strings, fragments, invalid ports, and whitespace. |
| `firmware/api_client.py`, constructor, lines 66–74 | Creates the bearer-token header and device-specific API path. |
| `firmware/api_client.py`, `_exchange`, lines 82–110 | Sends the request to the selected origin with the credential in a header, bounded timeouts, and redirects disabled. |
| `firmware/api_client.py`, `poll_command`, lines 128–143, especially line 131 | Selects the HTTP polling origin for `GET /api/devices/<device_id>/commands/pending`. This is the single client insertion operation. |
| `backend/main.py`, lines 35–39 and 100–132; `backend/settings.py`, lines 66–74 | Existing HTTP GET exception and separate reachable HTTP listener, implemented in the preceding step. |

The device sends its bearer token in an actual unencrypted HTTP request. A
party able to observe that connection could copy and reuse it to authenticate
as the device. Requiring the token does not encrypt its transmission. The
protected comparison sends the same polling request over certificate-verified
HTTPS. Readings and acknowledgments continue to use HTTPS. Credentials remain
out of URLs and failure logs, keeping this defect separate from V5. HTTP has
no certificate to validate; this defect is counted as V4 / planned CWE-319,
not also as V9.

Author verification: the actual `DeviceApiClient` submitted a reading, polled
a command, and acknowledged it through Version B Flask routes on live temporary
loopback HTTPS/HTTP listeners. The backend observed `https`, `http`, `https`,
respectively, with the test device's bearer header present in each request.
The pending-command route authenticated that device. Database authentication
queries and device service operations used doubles. A second untrusted CA
caused the HTTPS reading request to fail before reaching a route, with no
unverified retry. These checks establish local request behavior, not real
PostgreSQL operation, continuous device execution, remote interception, or
deployment exposure. Network-observer access assumptions and independent
review remain pending before a confirmed scored finding is frozen.

## Protected comparisons and unchanged selections

- **V1, hardcoded credentials:** settings lines 82–87 require externally
  supplied `DEVICE_ID` and `DEVICE_TOKEN`. The bundled A credential fallback is
  removed, including for `room-monitor-01`. The token is excluded from the
  settings representation. The local template contains blank credential fields.
- **V5, secrets in logs/files:** `_post_reading`, lines 112–123, logs only a
  fixed reason and status. Headers, response bodies, tokens, and raw exception
  text are excluded. Controlled failure tests include token-bearing exceptions
  and response data and verify that the token is not logged. This does not
  prove all possible log sinks safe; log permissions and deployment review
  remain relevant.
- **V9, disabled certificate verification:** `_exchange`, line 90, always
  supplies the configured CA path. `submit_reading`, lines 125–126, has no
  certificate-bypass fallback. TLS failures are terminal, and runtime transient
  retries continue to use the same verified path. Redirects are disabled.
  Real trusted HTTPS succeeds and an untrusted CA fails before an API handler.
  Requests ignores the CA argument for the separate HTTP polling operation.
- **V6, endpoint authentication:** firmware attaches its credential to all
  operations; B's backend keeps device binding on readings, polling, and
  acknowledgments. Both transports require authentication for polling.
- **V8, predictable credentials:** firmware receives its token from enrollment
  or local configuration. Sensor seed/randomness is limited to temperature
  behavior and is never used to generate a device credential.

V2/V3 password policy and hashing stay in the backend. B-02/V7 (fan-command
ownership omission) and B-03/V10 (unrestricted login attempts) are unchanged;
their exact locations remain in the [backend record](version-b-backend-implementation.md).
Version B still selects exactly the same three weakness types.

## Evidence and progress

Current source SHA-256 hashes for all 15 backend/firmware modules and root
support files, function line ranges, verifier hashes, dependency versions, raw
check output, and limits are in
[firmware-check-results.json](../../CodeBeacon/evaluation-study/verification/version-b/firmware-check-results.json).
The earlier backend snapshot is preserved in `backend-check-results.json`;
its backend source hashes remain applicable, while its earlier root README
hash predates the firmware setup instructions. Preserve prior evidence and
update line/hash records when source changes.

Run from the repository root using the existing pinned dependency environment:

```powershell
& 'CodeBeacon/evaluation-study/app/version-A/.venv/Scripts/python.exe' CodeBeacon/evaluation-study/verification/version-b/run_firmware_checks.py
```

Results: nine firmware checks and ten backend regression checks pass. Python
compilation, firmware CLI help, and dependency consistency checks also pass.
Tests cover origin/credential validation and explicit version-local settings,
transport routing and request headers, certificate rejection without fallback,
safe failure logs, response/command validation, redirect rejection, retained
reading and acknowledgment identities, retry scheduling, fan shutdown, and
sensor behavior. Runtime scheduling uses a fake clock/client; network tests
exercise actual firmware client methods and Flask listeners with database
doubles. Temporary test certificates, keys, threads, and listeners are cleaned
up afterward. No dependencies were installed or local runtime credentials
generated as part of this step.

Remaining work: implement Version B's database schema and frontend, provision a
separate database/device credential, run all API operations against PostgreSQL,
exercise the complete device/backend/dashboard workflow, review deployment
exposure, and independently check selected presences and protected absences.
The external Excel workbook remains unchanged and unverified.
