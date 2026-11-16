# Version B backend implementation

Recorded November 16, 2026. This is an implementation and author-verification
record, not an independently reviewed answer key or detector experiment.

## Completed scope and structure

`CodeBeacon/evaluation-study/app/version-B/` now has all ten backend modules,
matching Version A's filenames and responsibilities. `database/`, `frontend/`,
and `firmware/` exist as empty directories locally; Git will not retain empty
directories. Their source files remain pending. No placeholder source files
were added. Version A was not edited by this work; its existing local schema
change was preserved.

Root support includes a neutral project `README.md`, the same direct dependency
pins as A in `requirements.txt`, `.env.example`, and an ignored local `.env`
with blank required secrets. No credentials, database contents, certificates,
virtual environment, or runtime logs were copied from A. No application database
was created or modified. The external Excel workbook was not accessed or updated.

The backend uses the existing five-table contract: `"user"`, `devices`,
`readings`, `requests`, and `login_attempts`. Queries expect `token_hash` for
the stored device credential digest and `token_version` for account revocation.
The Version B schema must be supplied before normal database-backed operation.
Use a separate `room_monitor_b` database rather than A's database.

## API and runtime decisions

All 13 logical operations retain Version A's routes, methods, and response
contracts:

| Method | Path | Caller / behavior |
| --- | --- | --- |
| POST | `/api/accounts` | Public account registration |
| POST | `/api/accounts/login` | Public password login |
| GET | `/api/accounts/me` | Signed-in account |
| PATCH | `/api/accounts/password` | Signed-in account and current password |
| POST | `/api/devices` | Signed-in owner enrolls a device |
| GET | `/api/devices` | Signed-in owner's device list |
| GET | `/api/devices/<device_id>` | Owner's device details/latest reading |
| POST | `/api/devices/<device_id>/readings` | Authenticated matching device |
| GET | `/api/devices/<device_id>/readings` | Owner's reading history |
| POST | `/api/devices/<device_id>/commands` | Signed-in account; ownership omission recorded below |
| GET | `/api/devices/<device_id>/commands` | Owner's command history |
| GET | `/api/devices/<device_id>/commands/pending` | Authenticated matching device |
| POST | `/api/devices/<device_id>/commands/<command_id>/ack` | Authenticated matching device |

One `python -m backend.main` process starts two threaded Werkzeug development
listeners on `BACKEND_HOST`, default `127.0.0.1`: HTTPS on `BACKEND_PORT=8444`
and HTTP on `BACKEND_COMMAND_POLL_HTTP_PORT=8081`. Defaults avoid A's HTTPS port
8443. The configured ports must differ. TLS certificates must already exist;
TLS 1.2 or newer is required. Debugging/reloading remain disabled. Both listener
sockets are bound before threads start; partial startup releases a previously
bound socket. Ctrl+C shuts down both listeners. An unexpected listener stop
causes cleanup and a non-successful startup/runtime result.

The HTTP exception matches the resolved `commands.pending` endpoint and GET
method only. Authentication still runs normally. Other HTTP methods and routes,
including login, registration, readings, fan submission, and acknowledgment,
return 400 without redirecting or executing their route functions. Forwarded
scheme headers are not trusted. The same polling operation is available over
HTTPS. The future firmware will select HTTP only for polling via
`DEVICE_COMMAND_POLL_BASE_URL=http://127.0.0.1:8081`; its other operations use
`API_BASE_URL=https://localhost:8444`. Those client settings are documented in
the template but not consumed by a firmware implementation yet.

Werkzeug's [serving documentation](https://werkzeug.palletsprojects.com/en/stable/serving/)
describes its local development server and TLS configuration. Separate sockets
provide the HTTP and HTTPS listeners here. This is local development operation,
not a production deployment design.

## Selected vulnerability record

Paths and line ranges below are relative to `version-B/` and describe the saved
snapshot. Exact SHA-256 values for every module and root support file, AST
function locations, dependency versions, check output, and verifier hashes are
stored in [backend-check-results.json](../../CodeBeacon/evaluation-study/verification/version-b/backend-check-results.json).
Update locations and hashes after source changes; retain prior evidence before
freezing a scored case. CWE mappings below follow the selected root causes and
still require independent review.

| Placement / type | Location | Behavior, cause, consequence, and comparison | Status |
| --- | --- | --- | --- |
| B-01 / V4, CWE-319 | `backend/main.py` lines 35–39 and 100–132; `backend/settings.py` lines 66–74; future `firmware/api_client.py` and `firmware/settings.py` | The server accepts a credential-bearing GET poll over HTTP. A party able to observe that connection could obtain and reuse the device bearer token. Device authentication remains required; the defect concerns transport. The protected comparison sends the same request over certificate-verified HTTPS. Credentials belong in headers, never query strings. | Server support implemented and exercised with a real local HTTP request carrying a test bearer token, plus trusted HTTPS comparison. Firmware insertion and its final lines remain pending. Loopback testing does not prove remote-observer access or establish deployment exposure. |
| B-02 / V7, CWE-862 | `backend/routes/commands.py`, `submit`, lines 12–18; `backend/services/devices.py`, `enqueue_command`, lines 103–113 | An account token proves who submits a fan command, but neither the route nor its service verifies that the target device belongs to that account. An authenticated Alice can name Bob's existing device and queue a fan command. The service checks only device existence, then inserts the caller as `requested_by`. Protected comparison: call `owned_device(device_id, g.account['id'])` before enqueueing. Same operation/root cause as A-06. | Route-to-service author check with database doubles accepts the different-device command; source/query trace confirms no owner predicate. Unauthenticated submission fails; other owner-specific read routes reject a foreign device. Real two-user PostgreSQL exercise and independent review pending. |
| B-03 / V10, CWE-307 | `backend/routes/accounts.py`, `login`, lines 29–37; retained `backend/security.py`, `login_attempt`, lines 172–208 | Login calls the password verifier directly without entering the attempt-restriction context. Invalid guesses fail, but repeated guesses continue to reach verification without the intended five-failure/300-second block. Strong password policy and stored hashing remain. Protected comparison: invoke the existing limiter around authentication and record its result, as A does. | Twelve repeated failed API requests reach the mocked verifier and return 401, followed by successful login; no limiter database access or Retry-After response. Shared limiter code remains available. No proxy/middleware limiter is configured here. Infrastructure-level restriction and real PostgreSQL behavior require checking before freezing the case. |

## Selected targets intended to be absent

| Type | Implemented protection / remaining scope |
| --- | --- |
| V1: hardcoded credentials | Backend signing/database secrets are required from process environment or version-local `.env`; no active fixed backend/device credential is embedded. Future firmware must require its externally supplied device credential. |
| V2: weak password requirements | Registration and password change both invoke `validate_password_strength`, enforcing 15–128 characters. `backend/services/accounts.py` lines 12–14 and 37–46. Short-password rejection checked before database use. |
| V3: unsafe password storage | Both password-writing paths use shared `PASSWORD_HASH_METHOD`, `pbkdf2:sha256:600000`, matching A's protected comparison. Saved hashes and verification checked with the actual hashing library. No plaintext fallback. |
| V5: secrets in logs/files | Backend error logs contain error type only, and request logs do not include authorization headers. Future firmware failure logging still needs implementation and verification. No complete cross-application absence claimed. |
| V6: missing authentication | Pending-command polling now uses `@device_required` at `backend/routes/commands.py` lines 28–32. Readings and acknowledgments retain the same binding check. Missing and wrong credentials rejected, valid credentials accepted. Registration/login remain intentionally public. |
| V8: predictable generated credentials | `backend/services/devices.py` lines 27–30 calls `secrets.token_urlsafe(32)` independently of the public UUID and sensor seed. Database insertion stores its SHA-256 digest. Author checks verify storage and separation from A's device-ID-seeded prediction. This is source/library-based reasoning, not a statistical proof of unpredictability. |
| V9: disabled certificate verification | Server TLS is configured; live HTTPS author check validates a temporary trust anchor and rejects an untrusted certificate. Firmware/frontend client certificate validation remains pending. B-01's HTTP request is not counted again as a certificate-bypass defect. |

Account token expiry/revocation, current-password verification, reading retry
deduplication/conflict checks, device command acknowledgment/order handling,
parameterized queries, database TLS configuration, and owner checks on device
details/history are retained. These checks do not prove absence of every other
possible vulnerability.

## Verification and remaining work

Run from the repository root using a Python environment with the pinned
dependencies. This step reused A's existing environment without modifying it:

```powershell
& 'CodeBeacon/evaluation-study/app/version-A/.venv/Scripts/python.exe' CodeBeacon/evaluation-study/verification/version-b/run_checks.py
```

Ten author checks pass, along with Python compilation and `pip check`. Tests
are outside detector inputs in `verification/version-b/`. The network check
generates a temporary self-signed certificate, starts both actual listeners on
OS-assigned loopback ports, sends HTTP and certificate-verified HTTPS requests,
checks HTTP scope and credentials, rejects an untrusted HTTPS certificate, then
stops both listeners and confirms socket cleanup. A partial-bind failure also
checks cleanup. Database operations use doubles throughout these checks.

Next work: implement the five-table Version B schema, then firmware and frontend
using the same files/responsibilities as A; configure a separate database and
credentials; exercise all 13 operations against PostgreSQL and the complete
device/dashboard workflow; finalize B-01's client insertion and network exposure
assumptions; verify every selected presence and protected absence independently.
Freeze source locations, hashes, and grading rules only after that review. No
scored experiment or external workbook change is claimed.
