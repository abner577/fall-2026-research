# Selected security focus areas

We will start with two focus areas from the OWASP IoT Top 10 2018: password and credential security under category 1, and insecure communication and data handling under category 7. Each area includes several specific weaknesses we will look for, rather than one individual vulnerability.

## 1. Password and credential security

Based on category 1: Weak, Guessable, or Hardcoded Passwords.

We will look for:

- **Hardcoded credentials:** Passwords, tokens, or other credentials embedded in source code or configuration and used to access a device or service.
- **Predictable password generation:** Code that creates passwords using predictable values, such as a device identifier or a fixed pattern.
- **Weak password requirements:** Registration or password-change logic that allows weak passwords under the policy we define for the prototype.
- **Unsafe password storage:** User login passwords stored as readable text or processed with an unsuitable password hashing method. This also overlaps with category 7.

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
