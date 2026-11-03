# Version A database implementation

Recorded November 2, 2026. The student accepted five tables and renamed
`accounts` to `user` and `commands` to `requests`. The schema is saved at
`CodeBeacon/evaluation-study/app/version-A/database/schema.sql`.

## Structure

| Table | Purpose and relationships |
| --- | --- |
| `"user"` | User identity, unique username, password hash, login-token counter, creation time. |
| `devices` | Device identity, name, credential digest, creation time; `owner_id` references `"user".id`. |
| `readings` | Temperature in Celsius, reported fan state, measurement and receipt times; `device_id` references `devices.id`. |
| `requests` | Requested fan state, creation and acknowledgment times; `device_id` references `devices.id` and `requested_by` references `"user".id`. |
| `login_attempts` | Bounded login buckets, failure counts, and window start times used by the existing limiter. No account foreign key: attempts can name nonexistent accounts. |

`user` is a reserved PostgreSQL keyword, so SQL identifiers use `"user"`.
The three existing backend modules that query the renamed tables were updated:
`backend/security.py`, `backend/services/accounts.py`, and
`backend/services/devices.py`. Their line counts and vulnerability function
locations did not change. API routes, response fields, and filenames retain
their existing names; this decision concerns database table names.

`token_version` starts at 1. A password change increments it to 2 and issues a
token carrying 2; prior tokens carrying 1 fail the existing comparison.
`token_hash` stores the 64-character SHA-256 hash of a device token. The
backend hashes a supplied token and compares the digest. No device token is
inserted by the schema.

Reading identity is unique per device (`device_id`, `id`), supporting retry
deduplication. `acknowledged_at IS NULL` means a request is pending. There is no
separate status or acknowledgment table. Foreign keys prevent orphan records;
no automatic cascading deletion is added. Three indexes support device lists,
reading history, and request history/polling. The script creates all objects in
one transaction in an empty database; it does not replace existing tables or
insert accounts, credentials, or sample data. No Version B files were created.

## Verification and evidence

Created an isolated PostgreSQL 17.4 cluster under the ignored Version A `.local/`
folder, listening only on `127.0.0.1:55439`. The schema executed successfully and
created exactly the five agreed tables. Exercised all 13 API operations using
Flask's test client with real PostgreSQL queries. Checked reading retry behavior,
request acknowledgment retries, password-token revocation, device credential
verification and provisioning, persisted login limits and window recovery, and
basic foreign-key/value constraints. All six existing backend checks passed.
The temporary database server was stopped afterward; the configured application
database and local `.env` were not changed.

Initial schema source SHA-256 hashes, Python function line ranges, checks, and limits
are saved in
[`database-check-results.json`](../../CodeBeacon/evaluation-study/verification/version-a/database-check-results.json).
Earlier source evidence remains unchanged in `backend-check-results.json`.
The subsequent column rename to `token_hash` updates the schema, device insert
and authentication queries, local variable names, and backend test fixtures.
Hashing behavior and source function line ranges are unchanged. Current hashes
and the six passing backend checks for this rename are recorded in
[`token-hash-rename-check-results.json`](../../CodeBeacon/evaluation-study/verification/version-a/token-hash-rename-check-results.json).
The earlier PostgreSQL integration checks describe the pre-rename snapshot;
they were not rerun for this name-only change.
The backend's existing weakness selections and descriptions remain in
[Version A planning](version-a-planning.md) and
[backend explanations](explaining-code-files/backend-version-a.md).

These are author checks, not independent review. The Flask test client supplies
an HTTPS request scheme without exercising live TLS. The isolated database
connection uses loopback plaintext for testing; application settings still
require PostgreSQL TLS. Live frontend/firmware/API integration, the bundled
`room-monitor-01` credential provisioning, the A-04 log-reader boundary, and
independent vulnerability review remain pending.
