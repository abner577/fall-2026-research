# IoT code case design decisions

Recorded November 2, 2026, from the student's architecture approval and realism requirements. This is a design record; no application code or verified vulnerability cases have been produced by this documentation step.

## Version selections, November 2

The student subsequently authorized choosing and documenting the targets for
both versions before generating application code. The selections are recorded
in [Version A planning](version-a-planning.md) and
[Version B planning](version-b-planning.md). These documents supersede the
earlier approximate counts and statements that the version subsets are undecided.

- Version A: eight types — hardcoded credentials, weak password requirements,
  unsafe password storage through an insufficient-cost hash, secrets in logs,
  missing endpoint authentication, missing device authorization, predictable
  generated device credentials, and disabled certificate verification.
- Version B: three types — unencrypted sensitive communication, missing device
  authorization, and insufficient restriction of repeated login attempts.

The versions cover all ten accepted types with missing device authorization as
the only overlap, at the same user command-submission operation. Each type has
one intended insertion site per version. This is not a verified final instance
count or a claim of zero other vulnerabilities. The selected unsafe-storage
defect refines the earlier plaintext illustration to a low-work-factor password
hash that preserves ordinary login behavior.

The planning files identify intended component/operation locations, protected
comparisons, and verification requirements. Full endpoint inventory, exact
routes/functions, per-file behavior, and runtime parameters remain the next
design step. No executable application code or scored answer key is produced by
this selection step. Keep both planning documents outside detector inputs.

### Root-file implementation update, November 2

The student subsequently authorized the first four root files at
`CodeBeacon/evaluation-study/app/version-A/`: `README.md`, `requirements.txt`,
`.env`, and `.env.example`. That exact capitalization supersedes the lowercase
version names in earlier notes; use `version-B/` for the counterpart when it is
created. No counterpart or third version is created in this step.

The root files define a local HTTPS API on port 8443, a loopback Streamlit UI on
port 8501, explicit version-local environment loading, a dedicated PostgreSQL
database, and timing/simulation settings. Psycopg 3 with its binary extra is the
selected database driver. Werkzeug password hashing and ItsDangerous signed,
expiring account tokens are the planned shared account mechanisms. These are
implementation decisions, not evidence that the corresponding features exist.
Direct dependency versions are pinned; transitive packages are not yet locked.

No application operations or deliberate vulnerability instances are implemented
by these root files. Required secrets and enrollment credentials remain blank.
At that root-file stage, the Version A subset and detailed defects were still
pending. The version planning files now record the selections and intended
defects. Maintain an implementation vulnerability record with final source
locations and evidence as operations are built; no independent verification or
scored run is claimed.

## Accepted application direction

Before generating code or assigning vulnerability locations, check the [Markdown file-structure reference and future-chat instructions](project-file-structure.md). It is the sole structure reference; no Word document is required. Use the agreed structure for `version-A/` and `version-B/`; no baseline folder or third version is planned. Update the Markdown reference with any agreed structure changes and check existing application files against it. Earlier baseline-folder proposals are superseded; protected behavior still needs to be documented and verified within the two versions.

Build a small room temperature monitoring and fan-control system in Python, retaining Streamlit for the dashboard, Flask for the API, and PostgreSQL for storage. A device program will simulate the temperature sensor and fan instead of requiring physical hardware.

The device program sends readings and reported fan state to Flask through network requests. The dashboard obtains data through Flask and lets a user request fan changes. Flask handles access checks, storage, and command delivery; the device retrieves commands, changes its simulated fan state, and reports the outcome. Readings and actuator behavior are simulated; communication and application processing should actually execute once implemented.

Describe the study as an IoT application with simulated devices. It does not evaluate actual hardware or establish results about physical sensors, radio behavior, or deployed firmware.

## Realistic, localized vulnerabilities

- Build coherent application behavior first, preserving a baseline intended to lack the selected weaknesses. Insert controlled defects into plausible application paths.
- Do not repeat a selected weakness across every endpoint or many endpoints just to make detection easy. Prefer a localized mistake within otherwise consistent handling where that fits the weakness.
- For example, a single route might omit a required authentication check while comparable protected routes retain it, or one code path might call an inappropriate method. These illustrate realistic mistakes; they do not select authentication as a study target or establish an endpoint count.
- Do not force every vulnerability into a one-line change. Choose the smallest plausible change that produces the intended behavior and document its full effect, including shared callers if relevant.
- Use ordinary names, comments, and structure. Do not put vulnerability labels, CWE IDs, hints such as "authentication intentionally missing," or answer-key information into detector inputs.
- Aim for representative developer mistakes, not code obfuscation or artificial difficulty. Do not change scored cases in response to which weaknesses a detector catches or misses.
- Preserve target-absent controls and independently verify each selected presence and absence. Localized code can still produce a widespread effect; record the actual affected behavior.

## Realistic device behavior and interfaces

- Structure the device program like a normal device client: acquire a sensor reading, read actuator state, construct a message, authenticate, communicate with the API, process commands, and report outcomes.
- Obtain temperature through a dedicated sensor interface, such as a method for reading the current room temperature. Keep the simulated measurement implementation behind that interface so the communication code has the same responsibilities it would have with a physical sensor.
- Keep fan control behind an actuator interface that changes and reports state. A requested command and the device's reported outcome are distinct steps.
- Avoid scattering hardcoded sample temperatures or arbitrary random values through request-building code. The simulated sensor should produce a coherent sequence of readings with documented, reproducible behavior; its exact model remains to be designed.
- Include plausible device identity, measurement units, timing, command handling, and communication failure behavior as the implementation is designed. Exact message fields, routes, and retry policies remain open.
- Keep simulation provenance explicit in study documentation and setup. The goal is realistic device-facing code and interfaces, not disguising synthetic readings as physical measurements. All detectors must receive the same agreed project context.

## Required vulnerability record for every code version

The student requires a separate, maintained document that explains every deliberately inserted vulnerability and exactly where it appears in each version. We must understand and explain each weakness rather than simply generate code and assume it contains the intended problems. Add any other vulnerabilities discovered during review, clearly distinguishing confirmed issues from concerns awaiting verification. Do not claim that the record proves there are no undiscovered vulnerabilities.

November 2 clarification: the student selected an Excel constants/reference workbook, maintained in a personal folder outside this repository. Its requirements and progress live in [application-constants-progress.md](application-constants-progress.md) under `fall-2026-research/evaluation-study-preparation/`. The initial workbook has only the V1–V10 overview. Add the version-specific records described below alongside implementation when requested; Version A and Version B tabs remain deferred. Keep the workbook and answer-key information outside detector inputs. This supersedes the earlier open-format and repository-storage proposal for the workbook and does not authorize code generation. Agents can use the Markdown requirements without access to the external file.

For each vulnerability instance in each code version, record:

- A stable vulnerability ID, the weakness name, and the applicable CWE once confirmed.
- The case/version ID and exact saved code revision or file hashes.
- The file path, function or API operation, and exact line number or line range. For a missing check, identify the operation and lines where the check is required; there may be no single faulty line to point to.
- What the code does, why that behavior is vulnerable, what must be true for it to be exploited, and the possible consequence, in plain language.
- Why the weakness belongs in this part of the application and what changed from the protected baseline, including other files needed to understand the behavior.
- How the behavior was verified, the evidence, reviewer, date, and whether independent review is complete. An AI-generated explanation alone is not verification.

For each version, also identify which selected weaknesses are absent and explain the relevant protections. Include comparable safe examples and why they are not vulnerabilities where this helps distinguish a real issue from a false alarm. Record a resolved false alarm or disputed finding with its reasoning rather than silently losing it.

Keep the record synchronized with code changes. If edits move lines or change behavior, update the affected entries and preserve the earlier version's locations and evidence. Freeze a matching source snapshot and answer-key version before scored runs so that file paths and line numbers always refer to identifiable code.

## Next step and pending choices

The version planning files now select the weakness types, planned CWE mappings,
intended operations, protected comparisons, and verification goals. Before
generating application code, complete the endpoint inventory and per-file plan:
exact routes/functions, checks and omissions on each operation, controlled
changes, runtime assumptions, and concrete verification procedures. Record final
file/function locations and line ranges against the preserved source once
implementation exists.

The student accepted ten weakness types on November 2; see the [complete selection](../app-idea/selected-vulnerabilities.md#november-2-selection-update). The version planning files assign eight to A and three to B. The shared structure and Psycopg 3 driver have been chosen. Final source-level defects and CWE mapping review, exact placements, verified instance count, endpoint count, database schema, sensor model, and runtime settings remain to be completed. Keep placements within the agreed focus areas.

Keep this design record and later injection notes separate from the source packages supplied to detectors. No application code is authorized by this documentation-only request.

---

## Different code test cases
- So now that I think about it, it makes alot of sense to have one application with at least two controlled code versions. Instead of just having one static version of code that we use. This lets us compare detection when more weaknesses are present and when most of the code is protected.

Version A (8 selected weakness types; see the current planning file)
- Examine how many real weaknesses each detector finds when several are distributed through the application. The main thing we are trying to test is can we find them all, most likley you will find alot but how about all?

Version B (3 selected weakness types; see the current planning file)
- Example if you hallucinate to make new weaknesses present that arent there or if because most of the code is good you hallucinate and maybe guess that the rest of the code will be safe.

Both versions should preserve the same features, structure, and overall size. Version B should implement the protections for absent targets, rather than remove the relevant functionality. Otherwise, we would partly be comparing different applications.

Your concern about false alarms is valid: a detector should be able to conclude that a requested weakness is absent. We should give each version the same instructions.

## How we could represent each weakness

These are possible examples for the code versions we build. We have not finalized the exact locations, and a version does not need to contain all ten weaknesses.

### 1. Hardcoded credentials

The device sends temperature readings to Flask and includes a secret access token, which acts like the device's password. While getting the connection working, a developer types that token directly into the device's Python file and forgets to move it into a protected setting. The device keeps using that token when it contacts Flask. Someone who obtains the code could copy the token and pretend to be the device. We could leave one working token in the connection setup; simply reusing a token is not the problem here, storing the secret directly in the code is.

### 2. Weak password requirements

When someone creates an account, the app checks that their password meets the rules we have defined. But when they change their password later, the developer forgets to run the same check. That screen accepts a password that the account-creation screen would reject. We could put the mistake in this one password-change operation while keeping the checks in account creation.

### 3. Unsafe password storage

Normally, the app turns a user's password into a protected value called a password hash before saving it in PostgreSQL. It can use that value to check later login attempts without keeping the readable password. In one password-update operation, a developer accidentally saves the password exactly as the user typed it. Anyone able to read that database entry could see the password. We would check how login works afterward so the example really stores a readable password and does not merely stop users from signing in.

### 4. Unencrypted sensitive communication

The device normally uses an HTTPS address to contact Flask, protecting the information sent over the connection. But one operation, such as checking for fan commands, uses a separate address accidentally left as HTTP. The device sends its secret access token over that connection without encryption, so someone able to observe that network traffic could read it. We could put the wrong address in that operation's settings while keeping the other connections protected.

### 5. Secrets exposed in logs or files

If the device fails to contact Flask, the program writes details to a log file to help explain what went wrong. A developer accidentally includes the device's secret access token in those details and leaves it readable to people who should not have it. Those people could obtain the secret from the log. We could make this happen only when a request fails, while normal logs contain temperatures, times, and error messages without secrets. Writing a log file by itself is not the vulnerability; exposing the secret is.

### 6. Missing endpoint authentication

The device asks Flask whether there are any fan commands waiting for it. Flask should check the device's secret token before returning those commands. A developer forgets that check in this one API operation, allowing someone to ask for the commands without proving that they are the device. Other sensitive operations still check who is contacting them. We would make sure a check elsewhere in Flask is not already protecting this operation.

### 7. Missing endpoint authorization

Alice and Bob each have an account and a device. Flask checks that Alice is signed in when she asks to turn on a fan, but forgets to check whether she is allowed to control the particular device she names. By changing the device ID in her request to Bob's device ID, Alice can send a command to Bob's fan. The missing check is permission to control that device, even though Flask already knows who Alice is.

### 8. Predictable generated credentials

When a new device is added, Flask creates a secret access token for it. A developer uses a random-number method that is suitable for things like generating sample temperatures but is not designed to create hard-to-guess secrets. The token may look random while being easier to predict than it should be. We could put the wrong method in the token-creation step. Unlike the hardcoded-credential example, the app creates a new secret here; the mistake is how it creates that secret.

### 9. Disabled certificate verification

The device uses HTTPS to contact Flask. As part of that connection, it should check the server's certificate, which helps confirm that it is talking to the intended server. After a connection error, a developer adds a retry that skips this check to get the request working. That retry could send the device's secret to an impersonating server. We could leave this mistake in the retry while the normal connection still checks the certificate. The connection uses encryption, but the device no longer properly checks who is receiving its information.

### 10. Insufficient restriction of repeated authentication attempts

Flask checks whether a username and password are correct when someone signs in. The app also has a check that slows down or temporarily blocks repeated failed attempts. One way of signing in accidentally skips that second check, allowing someone to keep guessing passwords without an effective restriction. We could make that login operation call the password-checking function directly and forget the attempt-limit check. We would confirm that no other part of the system already limits those attempts. The mistake is allowing repeated guesses, even though each guess is still checked.

- How we are going to implement these weaknesses is that they are going to be plausible mistakes in a functioning workflow. Most of the code is going to be protected like a real-world case scenario and only have minor slip ups that would cause these vulnerabilities to be exposed.
