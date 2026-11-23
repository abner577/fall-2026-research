# Notes for adding the scanner rules to Application Constants later

November 23, 2026

We're not editing Excel yet. This is just a reminder of what we want to do once
all three scanners and their rules/checks are implemented. Semgrep is the one
we've worked on so far. CodeQL and Snyk Code still need to be added and verified.

## What the Excel update is for

I already have an Excel workbook called **Application Constants** that I keep
outside this repository. Later, I want to add scanner-rule information to that
existing workbook so it's easy to see:

- Which rules or checks we have for each scanner.
- What each one detects and why it matters in our Python application.
- Which rules apply to which vulnerability. More than one rule can apply to the
  same vulnerability.
- Which CWE items go with those vulnerabilities.
- Any limits or gaps, including vulnerabilities a scanner doesn't cover.

This is just to keep everything organized in one place. It isn't an application
configuration file or a table of which vulnerabilities the scanners actually
found in Version A or Version B.

## How I'll do it when we're ready

1. Finish implementing and verifying Semgrep CE, CodeQL, and Snyk Code, along
   with the rules, queries, or available checks we're going to use.
2. Upload my current **Application Constants** Excel file to a normal ChatGPT
   chat. Use that uploaded workbook, not a newly recreated workbook or a guessed
   copy from this repository.
3. Give that chat enough project context: we're comparing three scanners and
   three LLMs on the same Python IoT application cases, and we want a convenient
   reference showing how the scanner checks relate to our selected weaknesses.
4. Explain why we're adding this information and give it these notes, the table
   below, and the finished information for the other two scanners.
5. Ask it to add the new tab to the existing workbook. For the Semgrep tab, use
   the table below as the content I asked to save. Keep the rule IDs and the
   explanations, including the coverage gaps.
6. Have it follow the workbook's existing format, colors, fonts, headers, table
   style, and general template. It needs to look at the uploaded workbook first
   instead of inventing a different design. Leave the existing tabs and their
   contents intact.
7. Check the updated workbook before treating the task as done: the new content
   should be readable, match the existing style, and include every requested row.

The exact tab names and how we arrange the CodeQL and Snyk information can be
settled when we do the update. Don't invent their rules or assume Snyk accepts
custom rule files like Semgrep. For now, just keep their parts pending.

## Semgrep table to carry into the workbook

This is the table I supplied on November 23. Keep it here so the future chat
knows exactly what I wanted in the Semgrep tab. It describes the selected rules;
it doesn't claim that they detect every example of these vulnerabilities.

| Vulnerability | Rules added | What they detect and why it matters |
| --- | --- | --- |
| **Hardcoded credentials — CWE-798** | `hardcoded-password-default-argument`; `study-python-hardcoded-credential` | Detect literal passwords in function defaults, credential-like variables, dictionary entries, and environment fallbacks. Credentials embedded in Python source can be recovered from repository access or shared code. |
| **Weak password requirements — CWE-521** | `study-python-short-password-length` | Detect explicit password-length comparisons with a minimum below eight characters. Short accepted passwords make guessing easier. Eight is this rule’s screening threshold; the rule does not assess the entire password policy. |
| **Unsafe password storage — CWE-916, CWE-256** | `study-python-fast-password-hash`; `study-python-plaintext-password-sql` | Detect password-like input reaching fast hashes such as MD5 or SHA-256, or flowing directly into SQL password writes. Fast hashes permit inexpensive guessing; plaintext storage exposes passwords directly. Ordinary checksums and recognized password-KDF outputs have negative controls. |
| **Unencrypted communication — CWE-319, CWE-523** | `request-with-http`; `no-auth-over-http` | Detect HTTP request URLs and Requests authentication sent over HTTP. Without transport encryption, network observers may read transmitted data or credentials. The broader HTTP rule requires review of whether sensitive information is involved and excludes localhost URLs. |
| **Secrets exposed in logs or files — CWE-532, CWE-312** | `python-logger-credential-disclosure`; `study-python-secret-in-output`; `study-python-secret-in-file` | Detect credential-related logger formatting and credential-like values flowing into logging, `print()`, or file-style writes. These outputs can persist secrets somewhere with broader access than the original credential store. |
| **Missing authentication — CWE-306** | `study-flask-login-disabled` | Detect explicit settings that disable Flask-Login enforcement. This can allow protected endpoints to accept unauthenticated requests. Coverage is limited to this recognizable bypass; it does not detect every missing custom authentication check. |
| **Missing authorization — CWE-862** | **No rule added; documented coverage gap.** | Determining whether a user may access a particular device or operation requires ownership and permission context. These rules cannot reliably establish that such checks are missing across routes, services, middleware, and database queries. |
| **Predictable generated credentials — CWE-330** | `study-python-predictable-credential` | Detect noncryptographic randomness, timestamps, or UUID1 values reaching credential-like assignments or generation-function returns. Attackers may predict these values. Ordinary sensor randomness and secure `secrets` generation have negative controls. |
| **Disabled certificate verification — CWE-295** | `disabled-cert-validation`; `study-python-session-disabled-tls`; `study-python-unverified-tls-context` | Detect explicit verification disabling in Requests calls and sessions, HTTPX, and Python SSL contexts. Encryption without certificate validation can still connect to an impersonating server. |
| **Insufficient login-attempt restriction — CWE-307** | `study-flask-rate-limit-disabled` | Detect explicit settings that disable Flask-Limiter. This matters when affected authentication endpoints consequently permit unrestricted guessing. Missing custom lockouts or ineffective throttling remain coverage gaps. |

## Reminders for future AI agents

- This request only saves the plan and the Semgrep table. It does **not** ask
  anyone to create, edit, move, or synchronize an Excel workbook now.
- Wait until all three scanners and their selected checks are ready, and use
  the workbook the user supplies for the actual Excel-editing task.
- Read [the scanner guide](README.md), [our rule-writing approach](scanner-rule-approach.md),
  and [the actual Semgrep YAML](semgrep/rules/study.yml) for context. The YAML
  keeps the detailed rule definitions, sources, and limits. This note keeps the
  requested future Excel content and workflow.
- If the rule selection changes before the Excel update, point out what changed
  and carry the current, verified information forward. Don't silently present
  this dated table as a fresh verification of a changed rule set.
- Keep unsupported checks and partial coverage visible. A CWE mapping isn't
  proof of complete detection, and a successful rule test isn't an accuracy score.
- The older [workbook notes](../../../fall-2026-research/evaluation-study-preparation/application-constants-progress.md)
  explain the existing external Application Constants workbook. The separate
  [Word-document plan](../../../fall-2026-research/evaluation-study-preparation/study-constants-document-plan.md)
  is about scanner versions, settings, and workflows; this request records a
  later Excel tab for rule-to-vulnerability information.

Status right now: notes saved here; Excel update still pending.
