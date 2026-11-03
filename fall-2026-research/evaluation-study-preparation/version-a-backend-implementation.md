# Version A backend implementation

Decision and implementation date: November 2, 2026. Backend source belongs in
`CodeBeacon/evaluation-study/app/version-A/backend/`. This record and verification
files stay outside detector inputs. Version B is not created by this work.

## Contract fixed before implementation

All operations use JSON over HTTPS and the `/api` prefix. Account and device
credentials use `Authorization: Bearer ...`. Account tokens expire after the
configured lifetime and include a database-checked password version. Error bodies
use `{"error": {"code": "...", "message": "..."}}`.

| Method and path | Handler | Boundary and result |
| --- | --- | --- |
| POST `/accounts` | `routes/accounts.register` | Public; username/password registration; 201 account. |
| POST `/accounts/login` | `routes/accounts.login` | Public; persisted attempt check before verification; 200 token/account. |
| GET `/accounts/me` | `routes/accounts.me` | Account authentication; 200 account. |
| PATCH `/accounts/password` | `routes/accounts.change_password` | Account authentication and current password; 200 replacement token/account. |
| POST `/devices` | `routes/devices.enroll` | Account authentication; name; 201 device and one-time token. |
| GET `/devices` | `routes/devices.list_devices` | Account authentication; only owned devices. |
| GET `/devices/<device_id>` | `routes/devices.device_detail` | Account authentication and ownership; 200 device. |
| POST `/devices/<device_id>/readings` | `routes/readings.submit` | Device authentication bound to path ID; 201 new / 200 identical retry. |
| GET `/devices/<device_id>/readings` | `routes/readings.history` | Account authentication and ownership; newest first. |
| POST `/devices/<device_id>/commands` | `routes/commands.submit` | Account authentication; ownership omitted (A-06); 201 command. |
| GET `/devices/<device_id>/commands` | `routes/commands.history` | Account authentication and ownership; newest first. |
| GET `/devices/<device_id>/commands/pending` | `routes/commands.pending` | Device authentication omitted (A-05); oldest unacknowledged command or null. |
| POST `/devices/<device_id>/commands/<command_id>/ack` | `routes/commands.acknowledge` | Device authentication bound to path ID; matching fan state; 200, retry safe. |

All request bodies must be JSON objects with the operation's exact fields.
Readings match the existing firmware payload: UUID `reading_id`, timezone-aware
ISO `recorded_at`, finite `temperature_c` in -40..85, `unit="C"`, and
`fan_state="on"|"off"`. A repeated device/reading ID with different contents is
409. Readings can arrive late after a retry; newest recorded time determines
displayed state. Commands return UUID `id` and `fan_state`; polling never consumes
them. Acknowledgment applies only to the oldest pending command, and cannot
change its requested state. History lists use bounded `limit` (1..200, default
100); device lists use the same bound. Times returned by the API are UTC ISO.

Registration enforces a 15..128 character password policy without trimming or
composition rules. Password change retains nonempty/128-character input bounds
but omits the strength check (A-02). Registration hashes use Werkzeug
`pbkdf2:sha256:1000` (A-03); changes use `pbkdf2:sha256:600000`. The latter follows
the PBKDF2-HMAC-SHA256 work-factor floor in the
[OWASP password storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
consulted November 2. Both are salted normal Werkzeug hashes. Login uses the
ordinary verifier with no plaintext fallback or automatic rehash.

Login uses 4,096 fixed HMAC-derived username buckets in PostgreSQL, five failed
attempts per five-minute window. Bucket rows are locked across verification,
preventing concurrent requests or another worker from bypassing the limit.
Success resets the bucket; expiry recovers it. Unknown usernames use the same
bounded storage and a dummy protected hash. Bucket collisions can temporarily
limit unrelated accounts; this bounded local application design trades capacity
for predictable storage. No caller-supplied forwarding headers affect the key.

Enrollment uses UUID4 device IDs and `random.Random(device_id)` to generate a
256-bit token (A-07). Since the seed is the public identity, the token is
reproducible. The database stores SHA256 token digests, never plaintext device
tokens. The enrollment response is the only normal plaintext return.

## Database dependency

`database/schema.sql` remains pending in the separately planned database step.
The backend must not silently create tables or alter an existing database. Its
exact required schema is recorded here for that implementation:

- `accounts`: UUID `id` primary key, unique text `username`, text `password_hash`,
  integer `token_version` default 1, timestamptz `created_at` default now().
- `devices`: text `id` primary key (1..64 URL-safe characters), UUID `owner_id`
  referencing accounts, text `name`, text `token_digest` (64 hex characters),
  timestamptz `created_at` default now(). Index `(owner_id, created_at, id)`.
- `readings`: text `device_id` referencing devices, UUID `id`, timestamptz
  `recorded_at`, double precision `temperature_c`, text `fan_state`, timestamptz
  `received_at` default now(); primary key `(device_id, id)`. Check finite
  temperature -40..85 and fan state on/off. Index `(device_id, recorded_at, id)`.
  Unit is always Celsius and is not stored separately.
- `commands`: UUID `id` primary key, text `device_id` referencing devices, UUID
  `requested_by` referencing accounts, text `fan_state` checked on/off,
  timestamptz `created_at` default now(), nullable timestamptz `acknowledged_at`.
  Index `(device_id, created_at, id)` and pending partial index for null ack time.
- `login_attempts`: integer `bucket` primary key checked 0..4095, integer
  `failures` default 0 checked 0..5, timestamptz `window_started_at` not null.
  This table is lazy-filled within the bounded key space.

Connections use Psycopg 3 dict rows, explicit transactions, parameterized values,
TLS (`require`, `verify-ca`, or `verify-full`), bounded connection/statement/lock
timeouts, and request cleanup. Changing a password invalidates prior account
tokens. Application start requires externally supplied signing/database secrets;
the module entry point requires a TLS certificate/key and never starts HTTP.
The Streamlit browser connection remains loopback-only HTTP as described in the
existing project guide; dashboard-to-API requests remain HTTPS. For remote
PostgreSQL, `verify-full` and an installed trusted root certificate are required.

`flask --app backend.main:create_app provision-device --username <owner>
--device-id room-monitor-01 --name "Room monitor"` will prompt for the token
already used by `firmware/settings.py`. It binds that credential to an existing
account without another embedded backend credential. Provisioning never reassigns
an existing device or prints the token. Run after schema initialization and
account registration. This is the outstanding A-01 activation step; no database
or working provisioned identity is claimed by generating backend source.

## Verification and source record

All ten planned backend files exist, with no additional application modules or
structure changes. There are 13 method/path operations. The existing five
firmware modules were not edited. The frontend and database schema were not
generated in this backend-only step.

Snapshot identifier:
`87fd0ab23b4030f4a45d79dc9201bf9e077de36c0b11c0aeb4b9c04add704a67`.
This is SHA256 of the sorted `path sha256\n` inventory for all supplied Version A
files, excluding `.env`, `.local`, `.venv`, and caches. Full individual hashes,
function ranges, Python/dependency versions, and actual check output are saved in
[backend-check-results.json](../../CodeBeacon/evaluation-study/verification/version-a/backend-check-results.json).
Preserve that evidence when revising this record; create a new snapshot record
for later source changes rather than applying these locations to another revision.

### Backend insertion locations and effects

Paths below are relative to `version-A/`. CWE mappings remain subject to
independent root-cause review. Reviewer: Codex, November 2, 2026; author checks
only. These are implemented source paths with unit evidence, not confirmed
PostgreSQL-backed exploit demonstrations.

| ID | Exact operation and source range | Behavior, conditions, consequence, and comparison |
| --- | --- | --- |
| A-02 / CWE-521 | `backend/services/accounts.py:37-49`, `change_password`; reached by `backend/routes/accounts.py:48-55` | A signed-in account with its current password can change to `a`. The service verifies identity/current password but skips `validate_password_strength`. Registration at service lines 12-14 rejects the same password. Password changes still use the protected hash and revoke previous tokens. This is one strength-policy omission, distinct from identity verification. |
| A-03 / CWE-916 | `backend/services/accounts.py:12-22`, `register_account`; weak cost at line 14 | Registration stores a salted PBKDF2-HMAC-SHA256 hash with 1,000 iterations after checking strength. Anyone obtaining account hashes has a much cheaper offline guessing path. The protected change path at lines 37-49 uses 600,000 iterations. `authenticate` at lines 25-34 normally verifies either hash format; no plaintext fallback exists. The weak setting is at registration only. |
| A-05 / CWE-306 | `backend/routes/commands.py:27-31`, `pending` | A caller knowing a device ID can obtain its oldest pending command without a bearer token. The full path reaches `services/devices.pending_command` at lines 117-122, which performs existence checking and SELECT only, with no shared authentication. Repeated polling does not consume or acknowledge a command. Reading submission and acknowledgments use `device_required` and remain token-bound. |
| A-06 / CWE-862 | `backend/routes/commands.py:12-18`, `submit` | An authenticated Alice can name Bob's device and enqueue an on/off command. The route authenticates Alice, but never calls `owned_device`. `services/devices.enqueue_command` at lines 104-114 locks/checks existence and inserts the command without an ownership predicate. Device details and reading/command history retain ownership checks. Unauthenticated command submission remains rejected. |
| A-07 / CWE-338 | `backend/services/devices.py:27-31`, `enroll_device`; generator at lines 29-30 | Enrollment seeds `random.Random` with the newly issued device ID and returns its generated token. Anyone who learns that ID and the algorithm can reproduce `rma_` plus the 64-digit hex output of `Random(id).getrandbits(256)`, then impersonate the device. SHA256 digest storage at lines 16-24 does not prevent this prediction. UUID4 identities, external application signing secrets, and random salts retain cryptographic randomness. No other backend device-token generator is used. |

The bundled firmware's A-01 token has a supported provisioning path, not an
executed provisioning record. A-04 unauthorized log-reader access and A-08 live
invalid-certificate behavior were not reverified by the backend checks. Do not
mark all eight Version A targets independently established from this work.

### Hashes for the backend source

| Path | SHA256 |
| --- | --- |
| `backend/main.py` | `95eb3082ef491bd6fc843b1091b0e14245b6bd2a46aaef94477fddebbb8ebf9d` |
| `backend/settings.py` | `a47658bb9aae3b243ccfe2d28ee82ab607f4759b2b41958bc00713931aa4df5b` |
| `backend/database.py` | `5d100677b57208ca47a9216d9a7365aac2dc6236f0a441679a7b1161d8ba7932` |
| `backend/security.py` | `a357651077e63337a9fee2e6ef8aa7157040fd7f2e40c03d77f22d41609f14ff` |
| `backend/routes/accounts.py` | `a16b336fea0031662e996d17a8c04025e27afd872a96bf3eab94cdf10c77ad3a` |
| `backend/routes/devices.py` | `7108ddf0e9574aa218c28383bb53628b3bbc36702592d9d9606e4f611d038eb8` |
| `backend/routes/readings.py` | `50408805169b70fb59663f9008aebf1e68179b2bc0e3fa8273e8ac3cdf3c1eb2` |
| `backend/routes/commands.py` | `709e35c7149f634013c54f57f88a4210d4519ef8be81c1de5cf70c34f3e14d22` |
| `backend/services/accounts.py` | `7999702741a64eea4df029797b227e8c8e73f47ef701b6c94080805777947110` |
| `backend/services/devices.py` | `6a3ae48673f10cc351277aafdb2fbe8227205ec4e37df6c1475a03a3e17d6837` |

### Focused checks and limits

Installed the existing pinned backend dependencies into the version-local virtual
environment. Python 3.14.0, Flask 3.1.3, Werkzeug 3.1.9, Psycopg 3.3.6,
ItsDangerous 2.2.0, and python-dotenv 1.2.4 were used. Dependency pins were not
changed. Compilation, import/application-factory construction, and the registered
route inventory succeeded.

The six tests in
[test_backend.py](../../CodeBeacon/evaluation-study/verification/version-a/test_backend.py)
passed in the final recorded run (0.679 seconds):

1. Registration rejects `a`, produces the 1,000-iteration hash for a valid
   password, and verifies normally. Change accepts `a`, uses 600,000 iterations,
   and refuses an incorrect current password. Both formats authenticate.
2. Unauthenticated command polling returns the same response twice; command
   submission rejects missing account authentication, accepts an authenticated
   user naming another device, and does not call the ownership helper. Device
   details and reading/command history do call the ownership helper and reject
   the foreign-device case.
3. An independent `Random(device_id)` reproduces an issued token. Valid device
   authentication permits a well-formed firmware reading; another device's
   credential fails on both ingestion and acknowledgment. Boolean temperatures
   are rejected before storage.
4. Reading insert/retry/conflict and first/repeated command acknowledgments
   behave as expected using scripted database results.
5. Five direct failed login requests invoke verification; request six returns
   429 before verification with `Retry-After`. Case changes do not evade the
   limiter. Advancing beyond the window permits login and resets failures.
6. HTTP is rejected, response caching is disabled, old password-version tokens
   and expired tokens are rejected, and missing secrets / TLS-fallback database
   settings fail configuration validation.

Reproduce from `CodeBeacon/evaluation-study/app/version-A/`:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend
.\.venv\Scripts\python.exe ../../verification/version-a/test_backend.py
```

The route and service checks use database doubles. They do not execute SQL,
verify PostgreSQL constraints or transaction isolation, prove multi-process
limiting, establish network TLS behavior, or replace independent review.
There is no local `psql` available on PATH in this session. A live database was
not created or modified. Before freezing the case, implement the recorded schema,
exercise concurrent login limits, verify actual ownership predicates and retry
transactions against PostgreSQL, provision `room-monitor-01`, and run the
firmware-to-backend HTTPS flow. Confirm the A-04 log-reader boundary separately.
No scored detector run, hardware measurement, or exhaustive absence claim is made.
