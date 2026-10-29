# Scanner choices and report formats

Updated October 29, 2026. The student confirmed **Python for all study code examples** and selected **Semgrep Community Edition, CodeQL, and Snyk Code** as the three scanners. Exact versions and checks can be selected later; the framework and IoT component remain open.

| Tool | How it examines code and why we would use it | Report we would collect |
| --- | --- | --- |
| Semgrep Community Edition | Applies rules to the structure of source code, with support for many languages and custom rules. Free engine; use rules permitted for our study. | JSON: each item in `results` has `check_id`, `path`, `start` and `end` line/column positions, plus `extra.message` and `extra.severity`. CWE information may appear in rule metadata. CE does not guarantee the matched code text in `extra.lines`; we can read it from the original file. |
| CodeQL CLI | Creates a database representing the code, then runs queries that can examine relationships and data movement. Adds a different analysis approach to the comparison. | SARIF, a standard JSON format for scanner reports: findings in `runs[].results` have a rule ID, message, and location. File paths appear under `physicalLocation.artifactLocation.uri`; line/column positions under `physicalLocation.region`. Some queries add `codeFlows` tracing the problem through code. |
| Snyk Code | Analyzes source code for security weaknesses. Selected to replace Bandit following the professor's suggestion; use the free plan only. | JSON or SARIF export from `snyk code test`; preserve original reports and collect available rule, message, location, and evidence fields for comparison. |

Sources: [Semgrep CE](https://semgrep.dev/products/community-edition/), [Semgrep report fields](https://semgrep.dev/docs/semgrep-appsec-platform/json-and-sarif), [CodeQL reports](https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-cli/sarif-output), [Snyk Code report exports](https://docs.snyk.io/developer-tools/snyk-cli/scan-and-maintain-projects-using-the-cli/snyk-cli-for-snyk-code/view-snyk-code-cli-results).

The [CodeQL CLI terms](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md) permit academic research. Using it later to scan arbitrary user uploads needs a separate check of the applicable terms; research access does not establish unrestricted application use. For Semgrep, the engine and the chosen rules have separate licenses. These are tool-selection considerations, not changes to the planned experiment.

## Snyk Code: free plan

The professor suggested Snyk on October 26; the student has now selected Snyk Code to replace Bandit. The selected trio is Semgrep CE, CodeQL, and Snyk Code, with no paid Snyk access authorized. Checked October 29, 2026: [Snyk's pricing page](https://snyk.io/plans/) lists a $0 Free plan including Snyk Code (SAST), 100 Code tests per month, and five projects. Assess Snyk Code for source-code analysis; dependency scanning is a different product. Verify actual account limits, target coverage, and usable reporting during setup. If the study cannot fit the free offering, revisit the setup or scanner selection with the student; no paid upgrade is authorized.

For every scanner explored or run, retain its original reports and errors, exact project version, command, configuration/rules, tool version, and date. Keep exploratory results distinct from scored results and raw reports separate from normalized comparison tables.

## What a finding looks like

These are **invented, shortened examples of individual finding objects**, using documented field names. They omit report wrappers and other fields and are not actual scanner runs or a promise that the final checks detect this example. Both finding examples point to a hypothetical password written into `device.py` on line 12; the rule identifiers below are illustrative.

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

Snyk Code report export: use `snyk code test <project-path> --json` or `--sarif` to collect the original report. The final field mapping must be checked against the actual output; no Snyk run is claimed here.

The messages come from the rules or queries, so detail varies. A warning is a possible issue to check, and no warning does not prove the code is safe. Keep original reports and scan errors, then put findings into a shared format for comparison. For the application, collect the relevant code and retrieve CWE guidance before asking an LLM for proposed changes; the scanner report itself is not the later LLM explanation.

## Trade-off when extending coverage

Scanners include existing checks, so we do not need to write every rule from scratch. However, covering additional languages, frameworks, and libraries can require adapting or adding checks and testing their coverage. LLMs may reduce this repeated rule work by using learned code knowledge and broader instructions. Discuss this even if scanners score higher, while keeping it distinct from what our Python-only accuracy comparison demonstrates. See [the conclusion discussion](evaluation-plan.md#trade-off-to-discuss-in-the-conclusion).
