# Evaluation study answer key comparison table

Recorded November 25, 2026 from [application-constants.xlsx](application-constants.xlsx). The **Vulnerabilities** tab defines V1–V10; **Version A**, rows 3–10, and **Version B**, rows 3–5, list the present instances and their evidence. Targets not listed for a version are shown as Missing below. The workbook remains the source for exact snippets, complete explanations, and conditions affecting each vulnerability.

Use this table with the [scoring rubric](scoring-rubric.md). Keep both files and the workbook outside detector input packages. This transcription does not complete the checklist's independent answer verification.

## Expected results for all ten targets

**Found** means the target is present in that version. **Missing** means it is absent from the version's answer key. **Partially Found** is a grading outcome for detector results, so no expected answer is Partially Found.

| ID | Target vulnerability type | Version A | Version B |
| --- | --- | --- | --- |
| V1 | Hardcoded credentials | Found — A-01 | Missing |
| V2 | Weak password requirements | Found — A-02 | Missing |
| V3 | Unsafe password storage | Found — A-03 | Missing |
| V4 | Unencrypted sensitive communication | Missing | Found — B-01 |
| V5 | Secrets exposed in logs or files | Found — A-04 | Missing |
| V6 | Missing endpoint authentication | Found — A-05 | Missing |
| V7 | Missing endpoint authorization | Found — A-06 | Found — B-02 |
| V8 | Predictable generated credentials | Found — A-07 | Missing |
| V9 | Disabled certificate verification | Found — A-08 | Missing |
| V10 | Insufficient restriction of repeated authentication attempts | Missing | Found — B-03 |

Version A: **8 Found, 2 Missing**. Version B: **3 Found, 7 Missing**. Each version has ten scored targets and a maximum of ten points.

## Version A locations and matching evidence

Paths are relative to `app/version-A/`. Line numbers and supporting references are transcribed from the workbook. Each row below is one answer-key instance; supporting locations are context for that instance.

| Target and instance | Primary location | Supporting locations | Behavior to match |
| --- | --- | --- | --- |
| V1 / A-01 | `firmware/settings.py:11–12` | `firmware/settings.py:81–83` | An embedded device token is used as a fallback for `room-monitor-01`. It permits impersonation only if the backend has that identity registered with the same token. |
| V2 / A-02 | `backend/services/accounts.py:37–49`; missing strength check before line 45 | `backend/routes/accounts.py:48–55`; `frontend/views/account.py:86–93` | Password change verifies the current password but accepts a new password below the signup policy, making the account easier to guess. |
| V3 / A-03 | `backend/services/accounts.py:12–14`, especially line 14 | — | Registration hashes passwords with `pbkdf2:sha256:1000`, making stolen hashes cheaper to guess offline. |
| V5 / A-04 | `firmware/api_client.py:117–122` | `firmware/api_client.py:70–73` | A failed reading submission logs the request headers, including the bearer token; an unintended log reader could reuse a valid token. |
| V6 / A-05 | `backend/routes/commands.py:28–31`; `GET /api/devices/<device_id>/commands/pending` | `backend/services/devices.py:117–122` and `42–49` (`require_device`) | A caller knowing a valid device ID can read its pending command without authentication. This endpoint does not send, remove, or acknowledge commands. |
| V7 / A-06 | `backend/routes/commands.py:12–18`; `POST /api/devices/<device_id>/commands` | `backend/services/devices.py:104–114`; `frontend/views/dashboard.py:103–105` | Login is required, but device ownership is not checked before queuing a command. A signed-in user can queue a command for another user's device. |
| V8 / A-07 | `backend/services/devices.py:27–31` | — | Device tokens use `random.Random(device_id)`. Knowing the ID and algorithm allows recreation of the token and device impersonation. |
| V9 / A-08 | `firmware/api_client.py:124–132`, especially line 132 | — | After a certificate error, a reading retry uses `verify=False`. An interceptor or redirector could impersonate the server and receive the reading and token. |

V4 and V10 are **Missing** for Version A; there is no expected vulnerable location for those targets.

## Version B locations and matching evidence

Paths are relative to `app/version-B/`. Supporting references follow the workbook, including references outside the primary operation; use its detailed explanation to establish their relevance.

| Target and instance | Primary location | Supporting locations | Behavior to match |
| --- | --- | --- | --- |
| V4 / B-01 | `firmware/api_client.py:128–132`, especially line 131; `GET /api/devices/<device_id>/commands/pending` | `firmware/settings.py:58–76`, especially line 76, and `81–83`; `firmware/api_client.py:70–74` and `82–93`; `backend/main.py:35–39` and `112–113`; `backend/settings.py:66–74` | Command polling sends the bearer token over HTTP. Observing that connection can expose the token; the loopback default requires local traffic access or a deployment exposing the traffic. Readings and acknowledgments still use verified HTTPS. |
| V7 / B-02 | `backend/routes/commands.py:12–18`; missing ownership check before line 17; `POST /api/devices/<device_id>/commands` | `backend/services/devices.py:103–113` and `51–59` (ownership helper); `frontend/views/dashboard.py:103–105`; `backend/routes/accounts.py:48–55`; `frontend/views/account.py:86–93` | A signed-in user can queue a command for someone else's device because ownership is not checked. This is the same operation and root cause as A-06. |
| V10 / B-03 | `backend/routes/accounts.py:29–37`; missing attempt restriction around line 34; `POST /api/accounts/login` | `backend/services/accounts.py:25–34`; `backend/security.py:17–19` and `172–208`; `frontend/api_client.py:141–142` | Login calls authentication without the existing `login_attempt` helper, bypassing its intended five-failure limit within 300 seconds. Repeated online guesses remain possible; incorrect passwords still fail. |

V1, V2, V3, V5, V6, V8, and V9 are **Missing** for Version B; there are no expected vulnerable locations for those targets.

If the workbook or application changes, reconcile these statuses and locations before grading another code version.
