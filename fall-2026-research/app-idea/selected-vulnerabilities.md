# Selected security focus areas

This file is part of the planning record in `fall-2026-research/`. Under the student's November 2 folder clarification, code-case designs, selection and placement notes, and the answer key belong in [evaluation-study-preparation/](../evaluation-study-preparation/). Actual evaluation implementation and execution materials belong under [CodeBeacon/evaluation-study/](../../CodeBeacon/evaluation-study/); later app implementation belongs under [CodeBeacon/app/](../../CodeBeacon/app/) if it proceeds. Meeting records remain in `fall-2026-research/docs/`.

## November 2 selection update

The student confirmed these seven distinct weakness types: hardcoded credentials, weak password requirements, unsafe password storage, unencrypted sensitive communication, secrets exposed in logs or files, missing endpoint authentication, and missing endpoint authorization. Authentication and authorization are separate checks. The student subsequently accepted all three additions below, bringing the selection to ten weakness types. This does not yet fix the number of injected instances or project versions.

The following three additions are accepted:

| Accepted addition | Possible location in the temperature/fan application | Distinction from the original seven targets |
| --- | --- | --- |
| Predictable generated credentials | Device enrollment generates a credential from a device identifier or predictable sequence. | The application generates a guessable secret; it is not a fixed credential embedded in source or a weak user-chosen password. Already present in the candidate list below. |
| Disabled certificate verification ([CWE-295](https://cwe.mitre.org/data/definitions/295.html)) | One device API-client path bypasses server certificate checks. | A TLS connection can encrypt traffic while failing to establish that the server is authentic. Already present in the candidate list below. |
| Insufficient restriction of repeated authentication attempts ([CWE-307](https://cwe.mitre.org/data/definitions/307.html)) | One login path permits repeated password guesses without effective throttling or other restrictions. | Authentication exists, but repeated guesses are not adequately restricted. This is separate from missing authentication and weak password requirements. |

These are plausible placements, not finalized routes, functions, or CWE mappings for all ten targets. Define exact defects and check shared middleware, infrastructure protections, and scanner coverage before freezing cases. The older text below records the original candidate rationale; it does not revoke the ten choices confirmed above.

The complete accepted set is:

1. Hardcoded credentials.
2. Weak password requirements.
3. Unsafe password storage.
4. Unencrypted sensitive communication.
5. Secrets exposed in logs or files.
6. Missing endpoint authentication.
7. Missing endpoint authorization.
8. Predictable generated credentials.
9. Disabled certificate verification.
10. Insufficient restriction of repeated authentication attempts.

**Status updated October 29, 2026:** the professor accepted these two broad focus areas on October 26 after clarifying that each contains multiple weaknesses. They are not two finalized individual CWE targets. Exact entries, checks, and placements in the coherent IoT project still need definition and review. For each selected weakness, document why it is included, why it belongs at that application location, the exact code change, and independent verification evidence. See [the decision list](../coming-up-w-research-plan/decisions-and-professor-questions.md).

The earlier proposal was to start with two focus areas from the OWASP IoT Top 10 2018: password and credential security under category 1, and insecure communication and data handling under category 7. Each area includes several possible checks, rather than one individual vulnerability. The individual checks below remain candidates for review; acceptance of the areas does not finalize every listed check.

## 1. Password and credential security

Based on category 1: Weak, Guessable, or Hardcoded Passwords.

We will look for:

- **Hardcoded credentials:** Passwords, tokens, or other credentials embedded in source code or configuration and used to access a device or service.
- **Predictable password generation:** Code that creates passwords using predictable values, such as a device identifier or a fixed pattern.
- **Weak password requirements:** Registration or password-change logic that allows weak passwords under the policy we define for the prototype.
- **Unsafe password storage:** User login passwords stored as readable text or processed with an unsuitable password hashing method. This also overlaps with category 7.
- **Insufficient restriction of repeated authentication attempts:** A login path permits repeated password guesses without effective throttling or other restrictions. Accepted November 2; candidate mapping is CWE-307. Check protections in shared middleware and deployment configuration before confirming an instance.

For login passwords that the app verifies, we will look for an appropriate password hashing method and salt. Credentials the app must send to another service need protected storage; hashing them is not always a usable replacement.

**Why we chose it:** These weaknesses can appear directly in code and configuration. We can create clear examples, test whether the app detects them, and explain practical fixes.

## 2. Insecure communication and data handling

Based on category 7: Insecure Data Transfer and Storage, with related endpoint checks from category 3.

We will look for:

- **Unencrypted sensitive communication:** Code that sends passwords, tokens, private information, or sensitive device commands over connections without appropriate transport protection.
- **Disabled certificate verification:** Connection settings that bypass checking the server's certificate.
- **Secrets exposed in logs or files:** Code that writes credentials or other sensitive information to logs or files without suitable protection. Writing to a file is not automatically insecure; how it is protected matters.
- **Missing endpoint authentication:** Backend endpoints that expose sensitive information or actions without checking the caller's identity.
- **Missing endpoint authorization:** Endpoints that identify the caller but do not check whether that caller may access the requested data or control the requested device.

Endpoint checks require the relevant backend code. The app must consider checks in middleware and shared functions before reporting a missing protection. Public endpoints are not automatically vulnerable.

**Why we chose it:** IoT devices and their companion applications exchange information with other systems. Connection code, data handling, and backend handlers provide useful evidence for focused checks and understandable fixes.

## Why the other categories are not separate starting targets

| Category | Reason |
| --- | --- |
| 2. Insecure Network Services | Source code may show unsafe behavior, but determining which services actually run and are exposed usually needs deployment information. |
| 3. Insecure Ecosystem Interfaces | We are including focused authentication and authorization checks, but broader coverage of web, mobile, and cloud interfaces would expand the project too much. |
| 4. Lack of Secure Update Mechanism | Requires the relevant update code and an understanding of the device's update process. It is a more specialized starting target. |
| 5. Use of Insecure or Outdated Components | Feasible with dependency files, but detection mainly involves matching versions to known vulnerability records. We chose to focus first on code behavior and fixes. |
| 6. Insufficient Privacy Protection | Often depends on how information is collected, used, and permitted, which code alone does not fully explain. |
| 8. Lack of Device Management | Requires information about deployed devices and how they are monitored, updated, and retired. |
| 9. Insecure Default Settings | Some defaults are visible in files, but actual deployment settings may differ. Relevant credential and connection defaults can be examined within our chosen areas. |
| 10. Lack of Physical Hardening | Requires information about the physical device and its protections. |

The app will report potential issues with supporting code evidence and identify missing context when it cannot decide. Selecting these areas does not mean we can detect every weakness within them.

Source: [OWASP IoT Top 10 2018 and category descriptions](https://owasp.org/projects/internet-of-things?tab=seek-and-understand). Password storage guidance: [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
