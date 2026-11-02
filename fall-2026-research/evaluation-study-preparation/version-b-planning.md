# Version B planning

Decision date: November 2, 2026.

## Purpose and decision status

Version B will contain **three selected weakness types**, with one planned
insertion site per type. It retains the same application features, file
responsibilities, and planned API operations as Version A. The seven other
selected types receive working protections; their functionality is retained.

This is a design decision, not an implemented or independently verified code
case. Paths below are relative to the planned
`CodeBeacon/evaluation-study/app/version-B/` folder. This step does not create
that folder or any application source files. Keep this planning document outside
detector inputs.

Read [code-case-design.md](code-case-design.md),
[project-file-structure.md](project-file-structure.md), and
[Version A planning](version-a-planning.md) together. The full endpoint inventory,
per-file content plan, exact route/function names, and line locations remain the
next step. Operation descriptions below identify intended placements without
claiming that an API specification is already complete.

## The three selected weaknesses

| ID | Selected weakness and planned CWE mapping | Intended insertion site | Controlled mistake |
| --- | --- | --- | --- |
| B-01 | Unencrypted sensitive communication — [CWE-319](https://cwe.mitre.org/data/definitions/319.html) | `firmware/api_client.py`, device command-poll request, with its address in `firmware/settings.py` | Only command polling uses a reachable HTTP address and sends the device credential without transport encryption. |
| B-02 | Missing device authorization — [CWE-862](https://cwe.mitre.org/data/definitions/862.html) | `backend/routes/commands.py`, signed-in user's fan-command submission operation | The operation verifies the user but omits the check that the target device belongs to that user. This is the same operation and root cause as A-06. |
| B-03 | Inadequate restriction of repeated authentication attempts — [CWE-307](https://cwe.mitre.org/data/definitions/307.html) | `backend/routes/accounts.py`, login operation using helpers in `backend/security.py` and `backend/services/accounts.py` | Login checks the password but skips the server-side attempt restriction used by the protected Version A path. |

Confirm CWE mappings against the implemented root causes when freezing the
answer key. Related CWE labels may describe the same finding; the scoring rules
must account for this without counting one root cause several times.

## Why these three

This version remains mostly protected but still contains three consequential
mistakes in different workflows: device communication, user/device permissions,
and account login. A small number of targets can reveal missed findings and
false alarms on the seven protected targets, without deleting the relevant code.

B-01 and B-03 are the two accepted types intentionally absent from Version A.
B-02 is shared, giving one common defect and placement to compare across the two
application contexts. The combined selection covers all ten accepted types:
eight in A and three in B, with one overlap. Version B is deliberately not just a
subset of A. Different target mixtures mean the results cannot isolate the
effect of vulnerability count alone, and one shared instance is not sufficient
for a general claim about context sensitivity.

## Boundaries and protected comparisons

### B-01: HTTP command polling

The command-poll endpoint still authenticates the device and binds the token to
the device ID. Its defect is that the client transmits that credential over HTTP.
Reading submission, command acknowledgment, and all dashboard-to-API calls use
HTTPS with certificate validation. Keep credentials in headers, not URL query
strings, so this choice does not create a separate URL/log disclosure defect.

This case requires a real HTTP listener reaching the intended Flask operation.
Changing an HTTPS URL to an unused HTTP port would only break the application.
The detailed runtime plan must specify that listener, its port, and startup
behavior alongside the HTTPS listener using the existing `backend/main.py` and
settings files. Version A retains HTTPS-only credential transmission. The
logical API operations and device features remain the same in both versions.

A redirect from HTTP to HTTPS does not protect a credential already sent in the
first HTTP request. Verification must inspect the actual initial request and
establish what a network observer can access. Review the local-only versus
device-facing deployment assumptions before making a confirmed exposure claim.

### B-02: Fan command ownership omission

Use the same user command-submission operation as A-06. An unauthenticated caller
must still be rejected. Alice's valid account can name Bob's device because the
ownership check is absent on this operation alone. Device listing, details,
reading retrieval, and command-history retrieval enforce owner checks. Device
polling and acknowledgment authenticate the actual device.

Trace routes, services, and database predicates. If a shared helper or query
already limits the target device to Alice's ownership, an omitted route check
does not create this defect.

### B-03: Unrestricted login guesses

The normal login operation verifies valid and invalid passwords correctly but
omits the effective attempt-limit check. Keep the shared helper and supporting
data structures present, with the same responsibilities as Version A. Do not
invent a second login endpoint solely to carry the defect.

Repeated direct API attempts must reach password verification without the
restriction. Check that middleware, database state, a proxy, or another service
does not already limit them. UI delays alone do not supply a server-side
protection. Strong password policy and proper password hashing remain in place;
they do not replace attempt restriction.

## The seven targets intended to be absent

| Accepted target | Required protected behavior in Version B |
| --- | --- |
| Hardcoded credentials — [CWE-798](https://cwe.mitre.org/data/definitions/798.html) | Load device credentials and signing secrets from supplied local settings. No active fixed credential is embedded in source or database fixtures. Preserve device startup and enrollment functionality. |
| Weak password requirements — [CWE-521](https://cwe.mitre.org/data/definitions/521.html) | Registration and password changes apply the same server-side strength policy. A password rejected by one operation is also rejected by the other. |
| Unsafe password storage — [CWE-916](https://cwe.mitre.org/data/definitions/916.html) | Registration and password changes use the protected salted password-hashing configuration. Login uses the normal hash verifier; no plaintext fallback is introduced. |
| Secrets in logs — [CWE-532](https://cwe.mitre.org/data/definitions/532.html) | Reading-submission failure logs contain operation/status details without credentials or full authorization headers. Keep error handling and diagnostics functional. |
| Missing endpoint authentication — [CWE-306](https://cwe.mitre.org/data/definitions/306.html) | Command polling, reading submission, and acknowledgments authenticate and bind the device; user operations require account identity. Registration and login remain intentionally public entry points, not missing-authentication findings. |
| Predictable generated credentials — [CWE-338](https://cwe.mitre.org/data/definitions/338.html) | Enrollment uses a cryptographically suitable secret generator independently of public device IDs and the sensor simulation seed. |
| Disabled certificate verification — [CWE-295](https://cwe.mitre.org/data/definitions/295.html) | Every HTTPS operation and retry validates the configured trust anchor and server identity. An invalid certificate stops that request. B-01's HTTP request has no TLS certificate to validate; count that as cleartext transport, not a second certificate-bypass defect. |

These are selected-target controls to implement and verify, not assertions that
the unfinished project is vulnerability-free. Other discovered weaknesses must
be recorded and resolved or classified before freezing a scored case.