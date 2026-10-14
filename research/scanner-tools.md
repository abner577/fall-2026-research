# Scanner choices and report formats

Updated October 14, 2026. The student confirmed **Python for all study code examples** and selected **Semgrep Community Edition, CodeQL, and Bandit** as the three scanners. Exact versions and checks can be selected later; the framework and IoT component remain open.

| Tool | How it examines code and why we would use it | Report we would collect |
| --- | --- | --- |
| Semgrep Community Edition | Applies rules to the structure of source code, with support for many languages and custom rules. Free engine; use rules permitted for our study. | JSON: each item in `results` has `check_id`, `path`, `start` and `end` line/column positions, plus `extra.message` and `extra.severity`. CWE information may appear in rule metadata. CE does not guarantee the matched code text in `extra.lines`; we can read it from the original file. |
| CodeQL CLI | Creates a database representing the code, then runs queries that can examine relationships and data movement. Adds a different analysis approach to the comparison. | SARIF, a standard JSON format for scanner reports: findings in `runs[].results` have a rule ID, message, and location. File paths appear under `physicalLocation.artifactLocation.uri`; line/column positions under `physicalLocation.region`. Some queries add `codeFlows` tracing the problem through code. |
| Bandit | A free, open-source Python security scanner. Examines the structure of Python code using checks called plugins; simple to run on a folder. Fits the confirmed Python baseline. | JSON: each item in `results` includes `test_id`, `test_name`, `filename`, `line_number`, `line_range`, `code`, `issue_text`, `issue_severity`, and `issue_confidence`, with CWE information and a documentation link where available. |

Sources: [Semgrep CE](https://semgrep.dev/products/community-edition/), [Semgrep report fields](https://semgrep.dev/docs/semgrep-appsec-platform/json-and-sarif), [CodeQL reports](https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-cli/sarif-output), [Bandit](https://github.com/PyCQA/bandit), and [Bandit JSON format](https://bandit.readthedocs.io/en/latest/formatters/json.html).

The [CodeQL CLI terms](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md) permit academic research. Using it later to scan arbitrary user uploads needs a separate check of the applicable terms; research access does not establish unrestricted application use. For Semgrep, the engine and the chosen rules have separate licenses. These are tool-selection considerations, not changes to the planned experiment.

## What a finding looks like

These are **invented, shortened examples of individual finding objects**, using documented field names. They omit report wrappers and other fields and are not actual scanner runs or a promise that the final checks detect this example. All three point to a hypothetical password written into `device.py` on line 12; the rule identifiers below are illustrative.

Semgrep CE JSON finding:

```json
{
  "check_id": "study.hardcoded-credential",
  "path": "device.py",
  "start": {"line": 12, "col": 1, "offset": 180},
  "end": {"line": 12, "col": 23, "offset": 202},
  "extra": {
    "message": "Possible password embedded in source code.",
    "severity": "WARNING"
  }
}
```

CodeQL SARIF finding:

```json
{
  "ruleId": "study/hardcoded-credential",
  "message": {"text": "Possible password embedded in source code."},
  "locations": [{
    "physicalLocation": {
      "artifactLocation": {"uri": "device.py"},
      "region": {"startLine": 12, "startColumn": 1, "endColumn": 23}
    }
  }]
}
```

Bandit JSON finding:

```json
{
  "test_id": "ILLUSTRATIVE",
  "test_name": "example_credential_check",
  "filename": "device.py",
  "line_number": 12,
  "line_range": [12],
  "code": "12 password = 'example123'\n",
  "issue_text": "Possible password embedded in source code.",
  "issue_severity": "LOW",
  "issue_confidence": "MEDIUM"
}
```

The messages come from the rules or queries, so detail varies. A warning is a possible issue to check, and no warning does not prove the code is safe. Keep original reports and scan errors, then put findings into a shared format for comparison. For the application, collect the relevant code and retrieve CWE guidance before asking an LLM for proposed changes; the scanner report itself is not the later LLM explanation.

## Trade-off when extending coverage

Scanners include existing checks, so we do not need to write every rule from scratch. However, covering additional languages, frameworks, and libraries can require adapting or adding checks and testing their coverage. LLMs may reduce this repeated rule work by using learned code knowledge and broader instructions. Discuss this even if scanners score higher, while keeping it distinct from what our Python-only accuracy comparison demonstrates. See [the conclusion discussion](evaluation-plan.md#trade-off-to-discuss-in-the-conclusion).
