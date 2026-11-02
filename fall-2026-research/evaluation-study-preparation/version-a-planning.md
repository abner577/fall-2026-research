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
