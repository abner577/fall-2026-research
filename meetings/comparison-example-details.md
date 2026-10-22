# Worked comparison example: GPT and Semgrep

Prepared October 22, 2026. Supporting content for the remaining Method 4 visual, following [Vulnerability Detection Evaluation.png](../diagrams/Vulnerability%20Detection%20Evaluation.png).

**Illustration only.** All detector responses below are invented to explain the workflow. No GPT request or Semgrep scan was run. The answer key is a reasoned draft for this illustration, not a claim of completed independent human review. An actual study must have its answers independently checked before scored runs. The example does not select the study methodology or finalize its targets, model, or rules.

## 1. Shared preparation

Use one small Python file, `device_client.py`, containing six independent functions from an imagined IoT client. Evaluate only hardcoded authentication credentials, cleartext transmission of sensitive information, and disabled TLS certificate verification. These are illustrative checks within our two proposed focus areas. They do not replace the final target selection.

For this example, assume `access_token` is a secret, `reading` is private device telemetry, environment variables are supplied at deployment, and the endpoint URLs refer to remote services. Assume normal Requests behavior without external overrides. The display label is public and is never used for authentication. No claims are made about security properties outside the specified checks.

Both detectors receive the same code and context. Neither receives the answer key, the other detector's output, CWE definitions, or retrieval tools.

### Code supplied to both detectors

Line numbers shown in the prompt are presentation annotations, not part of the Python file. Count from `import os` as line 1, including blank lines.

```python
import os
import requests

def login_with_literal():
    password = "demo-device-password"
    return requests.post("https://iot.example/login", json={"password": password}, timeout=5)

def send_reading(access_token, reading):
    return requests.post("http://iot.example/readings", json={"token": access_token, "reading": reading}, timeout=5)

def fetch_config():
    return requests.get("https://iot.example/config", verify=False, timeout=5)

def login_from_environment():
    password = os.environ["DEVICE_PASSWORD"]
    return requests.post("https://iot.example/login", json={"password": password}, timeout=5)

def send_reading_tls(access_token, reading):
    return requests.post("https://iot.example/readings", json={"token": access_token, "reading": reading}, verify=True, timeout=5)

def device_label():
    return "admin-display"
```

### Shared answer key — evaluator only

Each row is one predefined function/weakness check, giving six binary evaluation units. This is not every possible function-by-weakness combination. Both detectors use the same six checks. The three grading visuals use the known vulnerabilities U1?U3; U4?U6 supply separate false-alarm and correct-absence counts. Count one outcome per row; duplicate warnings earn no extra credit. Findings outside these rows would be reviewed separately rather than silently discarded.

| ID | Function / checked weakness | Answer | Location | Evidence and reason |
| --- | --- | --- | --- | --- |
| U1 | `login_with_literal` / hardcoded credential | Present | Lines 5–6 | A literal password is assigned at line 5 and sent as an authentication password at line 6. |
| U2 | `send_reading` / cleartext sensitive transmission | Present | Line 9 | The request sends a secret token and private telemetry to an `http://` endpoint without transport encryption. |
| U3 | `fetch_config` / disabled certificate verification | Present | Line 12 | `verify=False` disables verification of the HTTPS server certificate. |
| U4 | `login_from_environment` / hardcoded credential | Absent | Lines 15–16 | The password comes from the environment; `DEVICE_PASSWORD` is a variable name, not an embedded credential value. |
| U5 | `send_reading_tls` / cleartext sensitive transmission | Absent | Line 19 | The sensitive payload is sent over HTTPS, with verification explicitly enabled. |
| U6 | `device_label` / hardcoded credential | Absent | Line 22 | `admin-display` is a public display label and has no authentication role. |

For evaluator reference, the three positive examples correspond to [CWE-798: hardcoded credentials](https://cwe.mitre.org/data/definitions/798.html), [CWE-319: cleartext sensitive transmission](https://cwe.mitre.org/data/definitions/319.html), and [CWE-295: improper certificate validation](https://cwe.mitre.org/data/definitions/295.html). These references support the draft key; their definitions are not supplied during detection.

## 2. Exact illustrative GPT prompt

The diagram's API arrow can read **“OpenAI API call → GPT model (exact model pending)”**. This is the complete prompt text for the example, without API transport code or a finalized model choice:

```text
Review device_client.py, a small Python IoT client, for only these issues:
1. Hardcoded authentication credentials.
2. Sensitive data sent over unencrypted HTTP.
3. Disabled TLS certificate verification.

Context: access_token is secret and reading is private telemetry. Environment
variables are supplied at deployment. URLs identify remote services. Assume
normal Requests behavior without external overrides. The device label is public
display text and is never used for authentication. Functions are independent.

Inspect the code without executing it. Base findings on the supplied code and
context. For each finding, identify the weakness, function, file and line(s),
supporting code, and a short explanation of why it is a problem. State uncertainty
when evidence is insufficient. Do not infer missing vulnerabilities from names
alone. Do not propose fixes in this detection response.

Return a findings table with columns:
Weakness | Function | File | Lines | Code evidence | Explanation
List only issues you detect; do not grade yourself as Found, Missing, or Partially
Found. If there are no findings, return an empty table and say so. After the table,
list any functions with no detected in-scope issue; this is not a security guarantee.

File: device_client.py (line-number prefixes are annotations)
01 | import os
02 | import requests
03 |
04 | def login_with_literal():
05 |     password = "demo-device-password"
06 |     return requests.post("https://iot.example/login", json={"password": password}, timeout=5)
07 |
08 | def send_reading(access_token, reading):
09 |     return requests.post("http://iot.example/readings", json={"token": access_token, "reading": reading}, timeout=5)
10 |
11 | def fetch_config():
12 |     return requests.get("https://iot.example/config", verify=False, timeout=5)
13 |
14 | def login_from_environment():
15 |     password = os.environ["DEVICE_PASSWORD"]
16 |     return requests.post("https://iot.example/login", json={"password": password}, timeout=5)
17 |
18 | def send_reading_tls(access_token, reading):
19 |     return requests.post("https://iot.example/readings", json={"token": access_token, "reading": reading}, verify=True, timeout=5)
20 |
21 | def device_label():
22 |     return "admin-display"
```

## 3. Invented GPT response

Every row below has file `device_client.py`. This shortened table is the illustrative response, including deliberate errors and incomplete detail so the example demonstrates grading.

| Weakness | Function | Lines | Code evidence | Explanation |
| --- | --- | --- | --- | --- |
| Hardcoded authentication password | `login_with_literal` | 5–6 | `password = "demo-device-password"`; `json={"password": password}` | The embedded password is used to authenticate to the remote login service. Anyone with the source can read the credential. |
| Sensitive information over HTTP | `send_reading` | 9 | `"http://iot.example/readings"`; `json={"token": access_token, "reading": reading}` | A secret token and private telemetry are sent without transport encryption and may be intercepted. |
| Disabled TLS certificate verification | `fetch_config` | 12 | `verify=False` | Explanation omitted. |
| Hardcoded authentication credential | `device_label` | 22 | `return "admin-display"` | This embedded administrator credential could be recovered from the source. |

No in-scope issues detected in `login_from_environment` or `send_reading_tls`.

Evaluator notes: the third row correctly identifies and locates the problem but omits why it matters, earning partial credit. The fourth row is a false alarm: the context explicitly says the string is a display label, not a credential. These are invented response shortcomings, not observed GPT behavior.

## 4. Scanner preparation and invented output

Use **Semgrep Community Edition** as the one scanner branch. A diagram note can say:

> Configure Python checks for hardcoded authentication credentials, HTTP transmission of sensitive data, and disabled certificate verification. Scan the same file; collect JSON and normalize findings.

Command preview:

```text
semgrep scan --config example-rules.yml --json device_client.py
```

`example-rules.yml` is a conceptual configuration name for the visual, not a file supplied or tested here. Coverage is intended for all three targets. Final rule implementation and validation remain separate work. The invented missed finding below does not establish a Semgrep limitation or a failure of any particular rule pack.

### Invented, shortened JSON response

This preview uses documented Semgrep field names but omits other report fields. Rule IDs and messages are illustrative.

```json
{
  "results": [
    {
      "check_id": "example.hardcoded-auth-password",
      "path": "device_client.py",
      "start": {"line": 5},
      "end": {"line": 6},
      "extra": {
        "message": "Literal password is used in the authentication request; the credential is exposed in source code.",
        "severity": "WARNING"
      }
    },
    {
      "check_id": "example.disabled-certificate-verification",
      "path": "device_client.py",
      "start": {"line": 12},
      "end": {"line": 12},
      "extra": {
        "message": "verify=False disables server certificate verification, allowing an untrusted server to be accepted.",
        "severity": "WARNING"
      }
    }
  ],
  "errors": []
}
```

### Normalized scanner findings

Every row has file `device_client.py`. Evidence can be read from the shared source when missing from JSON; normalization does not invent an explanation that was absent in the original response.

| Weakness | Function | Lines | Evidence | Explanation from output |
| --- | --- | --- | --- | --- |
| Hardcoded authentication password | `login_with_literal` | 5–6 | Literal password and its use in the login payload | Credential exposed in source code. |
| Disabled TLS certificate verification | `fetch_config` | 12 | `verify=False` | Untrusted servers may be accepted when verification is disabled. |

The invented response contains no finding for `send_reading`, so U2 is a miss. It contains no finding for U4–U6. Treat absence of a finding as a negative prediction only because this example assumes a completed, error-free scan with intended coverage of the targets. A failed, skipped, or unsupported check must be recorded separately in the real study.

Scanner preview references: [running local rules](https://semgrep.dev/docs/running-rules), [CLI scan options](https://semgrep.dev/docs/cli-reference), and [JSON report fields](https://semgrep.dev/docs/semgrep-appsec-platform/json-and-sarif). These support the command and report structure, not the invented detections.

## 5. Shared illustrative rubric

These rules make this example reproducible. They are an explicit example convention for review, not a final study-wide rubric.

**Distinguish the code from the detector's report.** The answer key records whether each specified weakness is present or absent and supplies its location and evidence. Found, Missing and Partially Found describe the completeness of a detector's identification of a real weakness. They do not describe a weakness being partly present in the code. For example, `verify=False` at line 12 is an actual vulnerability; GPT's response is Partially Found because it identifies that code but omits the required security explanation. A suspicious hint or poor design pattern needs its own defined target and evidence; it does not automatically earn partial vulnerability credit. Missing means the detector missed a real vulnerability, not that the code lacks one.

| Outcome | Rule | Points |
| --- | --- | --- |
| Found | Correct weakness, correct function and relevant line(s), supporting evidence, and a short explanation of the security problem. | 1 |
| Partially Found | Identifies the actual weakness and function with supporting evidence, but omits a required location detail or an explanation of why it matters. | 0.5 |
| Missing | A known vulnerability is not identified. A vague concern without evidence of the actual issue also earns no credit. | 0 |
| False alarm | Reports the checked weakness where the key says it is absent. Track separately from the known-vulnerability points. | No points; separate count |
| Correct absence | Does not report the checked weakness where the key says it is absent. | No points in the known-vulnerability denominator; separate count |

Do not require identical wording, a particular CWE label, or suggested fixes. Apply the same evidence standard to both detectors. Duplicate findings are merged into one scored outcome per unit.

**Known-vulnerability score = (Found + 0.5 × Partially Found) / 3 × 100.** This measures detection with partial credit; it is not overall binary classification accuracy. False alarms do not reduce this score under the existing proposal, so show them beside it.

Partially Found is a reporting-quality grade, not a property of the code. GPT's U3 earns 0.5 rubric points because its finding is incomplete.

## 6. Grading and scores

| Unit | Key | GPT grade | GPT points | Semgrep grade | Semgrep points |
| --- | --- | --- | --- | --- | --- |
| U1 | Present | Found | 1 | Found | 1 |
| U2 | Present | Found | 1 | Missing | 0 |
| U3 | Present | Partially Found | 0.5 | Found | 1 |
| U4 | Absent | Correct absence | — | Correct absence | — |
| U5 | Absent | Correct absence | — | Correct absence | — |
| U6 | Absent | False alarm | — | Correct absence | — |

| Summary | GPT illustration | Semgrep illustration |
| --- | --- | --- |
| Found / Partially Found / Missing | 2 / 1 / 0 | 2 / 0 / 1 |
| Points / known vulnerabilities | 2.5 / 3 | 2 / 3 |
| **Known-vulnerability score** | **83.3%** | **66.7%** |
| False alarms / correct absences | 1 / 2 | 0 / 3 |
| Binary TP / FN / FP / TN | 3 / 0 / 1 / 2 | 2 / 1 / 0 / 3 |
| Binary accuracy: (TP + TN) / 6 | 83.3% | 83.3% |
| Binary precision: TP / (TP + FP) | 75.0% | 100.0% |
| Binary recall: TP / (TP + FN) | 100.0% | 66.7% |

Suggested comparison caption:

> In this invented example, GPT has the higher partial-credit detection score (83.3% versus 66.7%), but produces one false alarm. Semgrep misses one real weakness and produces no false alarms. Both have 83.3% binary accuracy. This small illustration explains the comparison; it does not establish which methodology is better.

## 7. Three grading visuals for the method diagram

The three PNG images were generated using Matplotlib and Seaborn and use the agreed **Missing, Found, Partially Found** categories:

1. [GPT grading against the key](../diagrams/comparison-gpt-grading.png): one row per known vulnerability (U1–U3), one column per grade, and rubric points in the assigned cell.
2. [Semgrep grading against the key](../diagrams/comparison-semgrep-grading.png): the same rows and columns for the scanner.
3. [GPT versus Semgrep grade agreement](../diagrams/comparison-grading-agreement.png): a 3 × 3 cross-tabulation of the evaluator-assigned grades on those three vulnerabilities.

The first two are **grading heatmaps**, because the evaluator assigns these grades after comparing findings with the key. They are not conventional three-class confusion matrices: the code has no independent true class called Partially Found. A conventional confusion matrix needs independent true classes and corresponding predicted classes; see [the scikit-learn definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html). The third is an agreement matrix, with neither detector acting as the correct answer. False alarms and correct absences remain visible separately below the two grading heatmaps.

Grade agreement counts, with row/column order Missing, Found, Partially Found:

| GPT grade / Semgrep grade | Missing | Found | Partially Found |
| --- | --- | --- | --- |
| Missing | 0 | 0 | 0 |
| Found | 1 (U2) | 1 (U1) | 0 |
| Partially Found | 0 | 1 (U3) | 0 |

Exact grade agreement is **1/3 = 33.3%** (U1). Grade agreement is separate from the partial-credit detection score. Scores remain **GPT 83.3%, Semgrep 66.7%**.

## 8. Assets for the later diagram

Use the shared preparation and key centrally, the prompt/API/response/grading sequence on the blue left branch, and configuration/command/JSON/normalization/grading on the green right branch. Merge into the scored comparison, the three grading visuals in section 7, and the illustrative conclusion. Each image has an illustration label so it remains identifiable when copied elsewhere.

The three exported grading images are the retained assets. The notebook, generation script, dependency list and temporary Python environment were removed after the calculations and exports were verified. The final workflow diagram has not been created in this step.

### Report-preview images

The following PNGs can replace the corresponding text panels in the worked-example diagram. They preserve the illustrative findings and scores above and are labeled as invented examples, rather than screenshots of actual detector runs.

| Diagram panel | Image |
| --- | --- |
| GPT response table | [example-gpt-response.png](../diagrams/example-gpt-response.png) |
| GPT grading table | [example-gpt-grading.png](../diagrams/example-gpt-grading.png) |
| Semgrep JSON output | [example-semgrep-json.png](../diagrams/example-semgrep-json.png) |
| Normalized Semgrep findings | [example-semgrep-findings.png](../diagrams/example-semgrep-findings.png) |
| Semgrep grading table | [example-semgrep-grading.png](../diagrams/example-semgrep-grading.png) |
| Combined comparison table | [example-comparison-table.png](../diagrams/example-comparison-table.png) |

These are report previews separate from the three grading-matrix images. Only the rendered PNGs are retained; no additional notebook or generation script is needed.
