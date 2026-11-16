# Version B frontend implementation

Recorded November 16, 2026. All four agreed frontend modules now exist at
`CodeBeacon/evaluation-study/app/version-B/frontend/`, matching Version A's
filenames, responsibilities, and features. Version A source, B's backend and
firmware, dependencies, and local configuration were not changed. Version B's
database schema remains pending. No external Excel workbook was accessed or
updated.

This record supersedes frontend-pending statements in earlier implementation
records. It records author verification, not independent review or a frozen
scored answer key. Device measurements and fan behavior remain software
simulations; no physical hardware or complete application deployment was tested.
Study explanations stay outside the detector input package.

## Files and behavior

| File | Responsibility |
| --- | --- |
| `frontend/main.py` | Starts Streamlit, loads API settings, selects account/dashboard views, validates the account through Flask, and supports sign-out. |
| `frontend/api_client.py` | Loads version-local settings, sends account and device API requests, validates HTTPS origin and CA file configuration, and converts API/transport errors into UI messages. |
| `frontend/views/account.py` | Registration, sign-in, password changes, replacement-token handling, session expiry, and session cleanup. |
| `frontend/views/dashboard.py` | Device enrollment, one-time credential display/dismissal, device selection, temperature/status metrics, history/chart, fan commands, and acknowledgment history. |

The frontend was derived from the existing Version A implementation to preserve
case comparability. `main.py` and `views/dashboard.py` match A's source apart
from line-ending normalization.
The only source differences are B's default API origin on port 8444 and a new
password-policy caption in account settings. Password validation remains
server-side; the frontend sends confirmed password input and displays rejection
without replacing the current token. No client-side limiter was added.

The dashboard fetches data every five seconds using a Streamlit fragment and
offers manual refresh. It shows the latest temperature and reported fan state,
flags readings received more than 30 seconds ago, and displays up to 100 readings
and commands, with UTC times. A requested fan change is queued; it does not
immediately alter the displayed reported fan state. Command history distinguishes
pending commands from device acknowledgments. Enrollment displays a masked token
until dismissed; dismissal/sign-out clears it from session state. Registration
and password forms clear inputs on submission. Streamlit session state is scoped
to the browser session and is not durable storage.

All frontend API methods use HTTPS with the supplied CA file, bounded timeouts,
and redirects disabled. Requests sessions do not use inherited proxy/netrc
settings. Relative settings resolve against B's project root, with process
environment overriding its explicit `.env`. The frontend never uses the separate
HTTP device-poll origin. The setup guide uses loopback port 8502 for Streamlit,
allowing A's port 8501 to remain available. The frontend requires only API/CA
settings; database/signing credentials are consumed by the backend.

## Weakness boundaries and source locations

Paths and lines below are relative to `version-B/`. The source hashes and full
function ranges are recorded in the linked JSON evidence.

| Target/operation | Frontend location and boundary |
| --- | --- |
| B-01 / V4: unencrypted device polling | No frontend insertion. `api_client.py`, `load_settings`, lines 37-75, accepts only an HTTPS origin; `_request`, lines 91-130, always supplies the CA path and disables redirects. B-01 remains at the existing firmware polling operation and HTTP listener. |
| B-02 / V7: missing device authorization | `views/dashboard.py`, lines 103-109, calls `ApiClient.request_fan`, `api_client.py`, lines 167-170. The dropdown normally lists the signed-in user's devices, but this UI is not an authorization boundary. The backend still permits a signed-in caller to name another owner's device in command submission. Original route/service locations and checks remain in the backend record. |
| B-03 / V10: repeated login guesses | `views/account.py`, `render_sign_in`, lines 44-74, calls `ApiClient.login`, `api_client.py`, lines 141-142. Each submitted login reaches Flask. The existing backend still omits attempt restriction. Generic handling of a possible HTTP 429 response is not evidence that B enforces a limiter. |
| V2 / V3: password policy/storage | `views/account.py`, `render_settings`, lines 77-97, sends current/new passwords and replaces the account token only after success. The backend enforces 15-128 characters and protected hashing on both password-writing operations. The UI's length caption does not supply that protection. Backend regression tests retain actual hash/strength checks. |
| V1 / V5 / V8: credentials and disclosure | No fixed active credential or credential generator is added. Account/device tokens stay in session state rather than URLs or shared caches. Device enrollment credentials come from the API and are removed on dismissal/sign-out. `_request` uses fixed transport-failure messages rather than raw Requests exceptions, and no frontend log sink is introduced. These checks do not prove all possible deployment/logging paths safe. |
| V6 / V9: authentication and certificate checks | Protected API calls attach account bearer credentials. Registration and login omit the bearer header. Missing, expired, and rejected sessions return to sign-in on protected account/dashboard access. TLS failures become errors with no insecure retry. Authentication and ownership enforcement remain backend responsibilities. |

No additional deliberate weakness is inserted in the frontend. This does not
establish absence of every possible defect. B-01/B-02/B-03 retain their prior
backend/firmware locations and hashes in the earlier
[backend](version-b-backend-implementation.md) and
[firmware](version-b-firmware-implementation.md) records.

## Verification and evidence

From the repository root, using the existing pinned Version A environment:

```powershell
& 'CodeBeacon/evaluation-study/app/version-A/.venv/Scripts/python.exe' CodeBeacon/evaluation-study/verification/version-b/run_frontend_checks.py
```

Eight frontend tests and ten backend regression tests pass. Frontend compilation
and `pip check` also pass. No dependency installation was required. The frontend
tests cover:

- HTTPS-only origins, version-local configuration, invalid timing values, CA
  selection, bearer headers, disabled redirects, safe TLS failures, and errors.
- Registration, login, password replacement/rejection, sign-out, and cleanup of
  expired/rejected sessions and undismissed enrollment credentials.
- Empty device lists, enrollment, empty/stale readings, temperature history,
  queued fan commands, rejected commands, and later device acknowledgments.
- Actual frontend request/response compatibility with Flask routes through a
  Requests-to-Flask test-client bridge, including server-side short-password
  rejection. Database and selected account/device service operations use doubles.

Exact saved source hashes for all 19 source modules and root support files,
function line ranges, verifier hashes, dependency versions, complete check
output, and limitations are in
[frontend-check-results.json](../../CodeBeacon/evaluation-study/verification/version-b/frontend-check-results.json).
Earlier backend and firmware evidence is preserved unchanged. This snapshot's
root README hash includes the dashboard run instructions; it supersedes the
earlier README hashes for the current project guide.

Streamlit AppTest checks widget behavior without a browser. Transport option
tests use mocked Requests responses; the Flask bridge uses no network and does
not validate real TLS. Backend regression tests exercise live local HTTP/HTTPS
listeners with database doubles, but do not run the frontend client over that
transport. Timed fragment refresh in a browser, visual browser QA, real B
PostgreSQL operations, complete device/backend/dashboard execution, deployment
exposure review, and independent review remain pending. No scored detector run
or answer-key freeze is claimed.
