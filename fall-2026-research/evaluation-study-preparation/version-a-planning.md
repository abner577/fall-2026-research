# Version A planning

Decision date: November 2, 2026.

## Purpose and decision status

Version A will contain **eight selected weakness types**, with one planned
insertion site per type. These are the implementation selections made under the
student's instruction to decide the two versions. They are not implemented or
independently verified findings. An insertion can affect many requests or stored
records; eight insertion sites does not mean only eight affected requests.

Use the application and file responsibilities in
[code-case-design.md](code-case-design.md) and
[project-file-structure.md](project-file-structure.md). Paths below are relative
to `CodeBeacon/evaluation-study/app/version-A/`. This document stays outside
detector inputs.

This step selects the weaknesses and intended operations. The complete endpoint
count, exact routes, function names, per-file contents, and line locations will
be planned next, before application code is generated. The operation names below
are descriptions, not a frozen API specification.

## The eight selected weaknesses

| ID | Selected weakness and planned CWE mapping | Intended insertion site | Controlled mistake |
| --- | --- | --- | --- |
| A-01 | Hardcoded device credential — [CWE-798](https://cwe.mitre.org/data/definitions/798.html) | `firmware/settings.py`, one simulator credential setup path | A working device access token is embedded in source instead of supplied through local configuration. |
| A-02 | Weak password requirements — [CWE-521](https://cwe.mitre.org/data/definitions/521.html) | `backend/services/accounts.py`, password-change operation reached through `backend/routes/accounts.py` | Password changes omit the shared strength-policy check that account registration performs. |
| A-03 | Unsafe password storage — [CWE-916](https://cwe.mitre.org/data/definitions/916.html) | `backend/services/accounts.py`, account-registration password hashing | Registration uses an obsolete password-hash work factor, making offline guessing much cheaper than with the protected hashing path. |
| A-04 | Device secrets exposed in logs — [CWE-532](https://cwe.mitre.org/data/definitions/532.html) | `firmware/api_client.py`, reading-submission failure logging | An error log includes the device credential or the complete credential-bearing request headers. |
| A-05 | Missing endpoint authentication — [CWE-306](https://cwe.mitre.org/data/definitions/306.html) | `backend/routes/commands.py`, device command-poll operation | The operation returns a device's pending commands without authenticating the requesting device. |
| A-06 | Missing device authorization — [CWE-862](https://cwe.mitre.org/data/definitions/862.html) | `backend/routes/commands.py`, signed-in user's fan-command submission operation | The operation authenticates the user but omits the check that the named device belongs to that user. |
| A-07 | Predictable generated device credentials — [CWE-338](https://cwe.mitre.org/data/definitions/338.html) | `backend/services/devices.py`, device-enrollment credential generation | Enrollment uses a non-cryptographic pseudo-random generator with predictable initialization to create a device secret. |
| A-08 | Disabled server-certificate verification — [CWE-295](https://cwe.mitre.org/data/definitions/295.html) | `firmware/api_client.py`, reading-submission retry after a certificate-validation failure | A retry sends the authenticated HTTPS request with certificate verification disabled. |

The CWE identifiers describe the planned defects. Confirm the final mapping
against the implemented root cause before freezing the answer key. A detector
reporting a related CWE should be assessed against the agreed matching rules,
not rejected solely for choosing a different abstraction level.

## Why this set makes sense

These choices exercise account handling, device enrollment, device-facing APIs,
user permissions, error handling, and TLS. They fit the accepted application
without adding unrelated functionality. They include both visible credential
mistakes and mistakes that require tracing checks across routes and services.
Selection is based on application relevance, not an expectation that a specific
scanner will recognize each defect.

Unsafe password storage is specifically a **low-cost password hash**, not
plaintext storage. This narrows the earlier illustrative plaintext example while
retaining the accepted unsafe-storage weakness type. Registration will still
store a salted, recognizable hash that the normal password verifier can check.
Password changes will retain the protected hashing method. The weak work factor
must be fixed explicitly during detailed design and justified against current
password-storage guidance; do not introduce a custom plaintext fallback merely
to keep login working.

The other two accepted types, unencrypted sensitive communication and inadequate
login-attempt restriction, are reserved for Version B. Missing device
authorization is the one shared target. Consequently, the two versions cover all
ten accepted types, with one overlap: `8 + 3 - 1 = 10`.

## Boundaries and protected comparisons

| Target | Required boundary and comparison |
| --- | --- |
| A-01 | The embedded value must actually authenticate a provisioned local device. Finalize the matching enrollment/initialization record; an unused example string is not a vulnerability. Other device credentials and the application signing secret remain externally configured. Use only study-local credentials. |
| A-02 | Registration enforces the shared password policy. Password changes still require the signed-in user's identity and current password. The omission concerns the new password's strength, not identity checking. The policy and a clearly rejected short-password example must be specified before implementation. |
| A-03 | Registration enforces password strength but uses the weak hashing configuration. Password changes use the protected hash configuration. Login must verify both stored formats normally. This separates the storage defect from A-02's policy omission. |
| A-04 | Only the reading-submission error path leaks the secret. Successful requests and other logs omit credentials. Specify the log sink and who can read it; a secret visible only to its legitimate owner is insufficient evidence of unauthorized disclosure. |
| A-05 | Only device command polling omits device authentication. Reading submission and command acknowledgment authenticate the device and bind the supplied device identity to its credential. Polling must not consume a command just because someone fetched it. |
| A-06 | Only a user's command submission omits device ownership authorization. Device lists, device details, reading retrieval, and command-history retrieval retain owner checks. Device authentication and acknowledgment binding remain enforced. |
| A-07 | Limit the weak generator to enrollment credentials. Account signing secrets and other security tokens retain cryptographic randomness. Sensor simulation randomness is unrelated and must not be counted as a credential weakness. Demonstrate token prediction from information an attacker could know. |
| A-08 | The initial request and all other HTTPS paths validate the configured server certificate. Only the reading-submission certificate-error retry bypasses validation. It must remain HTTPS; this is not an HTTP downgrade. |

If an operation is protected by shared middleware or a service-level check,
removing a route decorator alone does not establish a missing check. Trace the
entire request path. A-05 and A-06 are separate operations with different caller
types; do not count the authentication failure and its downstream permission
consequences as two independent omissions at the same site.

A-04 and A-08 may both be reached during request failure. Verify them separately:
one requires a credential written to an inappropriate log sink; the other
requires an HTTPS request to proceed despite an invalid server certificate.
Neither finding proves the other.

## The two targets intended to be absent

| Target | Required protected behavior in Version A |
| --- | --- |
| Unencrypted sensitive communication — [CWE-319](https://cwe.mitre.org/data/definitions/319.html) | The device and dashboard use HTTPS for all credential-bearing API operations. No HTTP retry or alternate command-poll URL sends a credential. Certificate-validation failure in A-08 does not itself remove encryption. |
| Inadequate restriction of repeated authentication attempts — [CWE-307](https://cwe.mitre.org/data/definitions/307.html) | Login applies an effective server-side attempt restriction before password verification, with bounded failure tracking and a defined recovery window. Repeating direct API calls must not bypass it. |

These are intended controls, not verified absences. Review existing local
transport defaults before making a whole-project claim: `.env.example` currently
uses PostgreSQL `sslmode=prefer`, and the browser accesses Streamlit over loopback
HTTP. Define and document those trust boundaries, or strengthen the defaults, in
the common deployment plan. Do not silently ignore another in-scope cleartext
credential path while marking CWE-319 absent.

---

## Version A implementation plan

### Vulnerabilities detected in version A
1. V1 - Hardcoded credentials
File: firmware/settings.py

- The simulated device needs a secret token when it sends readings to the server. We will write one working device token directly into this Python file instead of reading it from the separate local settings file.

- The server must recognize that token, so it actually works as the device’s password. Someone who obtains the source code could copy it and pretend to be that device. An unused sample token would not demonstrate this vulnerability.

2. V2 - Weak password requirements
File: backend/services/accounts.py
Request handled by: backend/routes/accounts.py

- When someone creates an account, we will call a shared function that checks whether their password meets our password rules.

- When that person changes their password, we will deliberately forget to call that same strength-checking function. They could therefore change their password to something that account creation would reject.

It's kind of like we have one endpoint for creating an account, right? In that endpoint, the password requirements are properly enforced, but we have another endpoint for changing a password. In that endpoint, we forget to enforce these password creation rules

3. V3 - Unsafe password storage
File: backend/services/accounts.py

- When an account is created, the server will turn its password into a stored value called a password hash. However, we will choose a setting that makes this calculation take too little work.

- Login will still work normally. The problem appears if someone steals the stored password data: they can try possible passwords against it much faster than they should.

- Password changes will use the stronger storage setting. This keeps two separate mistakes: V2 accepts a weak new password; V3 gives stored passwords insufficient protection.

4. V5 - Secrets exposed in logs
File: firmware/api_client.py

- The device will send a temperature reading to the server. If that request fails, an error-handling section will write diagnostic information to a log.

- We will make that section include the device’s secret token, such as by recording the complete request information containing it. Someone who can read that log could copy the token and impersonate the device. Normal messages will leave secrets out.

5. V6 - Missing endpoitn authentication
File: backend/routes/commands.py

- That endpoint should check the device’s secret token before returning its commands. We will deliberately omit that check and let the caller request commands using the device’s identifier alone. Someone who knows that identifier could retrieve its pending commands without proving they are the device.

6. V7 - Missing endpoint authorization
File: backend/routes/commands.py
Related command handling: backend/services/devices.py

- There will be another endpoint where a signed-in user asks to turn a particular device’s fan on or off. We will check that the user is signed in, but forget to check whether the requested device belongs to them. Alice could submit a fan command using Bob’s device identifier, and the server would accept it.

7. V8 - Predictable generated credentials
File: backend/services/devices.py

- When a user registers a new device, the server will generate its secret access token. We will use a random-number generator intended for ordinary simulations, and start it from a predictable value. Its output may look random, but someone who knows how it starts could reproduce the sequence and work out device tokens.

8. V9 - Disabled certificate vertification
File: firmware/api_client.py

- When the device sends a temperature reading over HTTPS, it will initially check the server’s certificate—the evidence that it is talking to the expected server. If that check fails, we will make the error-handling section retry the request with certificate checking switched off. The device would then send its authenticated request without properly checking who receives it.

### Vulnerabilities detected in version B
1. V4 - Unencrypyed sensitive communication: protected
Files: firmware/settings.py, firmware/api_client.py, frontend/api_client.py, and backend/main.py

- The device and dashboard will use HTTPS when communicating with the API. The server will provide the HTTPS connection, and neither client will retry a failed request using ordinary HTTP.For example, the device’s secret token will travel inside an encrypted request when it submits readings.

2. V10 - Unrestrictied repeated login attempts: protected
Files: backend/routes/accounts.py and backend/security.py
Supporting storage: database/schema.sql

- When a login request arrives, the endpoint will first call a shared function that checks whether too many failed attempts have already occurred. Failed attempts will be recorded. Once the limit is reached, the server will temporarily reject further attempts before checking another password.