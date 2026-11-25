# Plan for the external study constants document

Requested November 23, 2026. This file records the requirements for a future
Word document. Do not create the Word document yet. Its eventual location is
outside the repository and has not been specified. This Markdown file is a
planning note, not a second maintained constants registry.

The document will be the human reference for the exact scanner versions and
LLM configurations agreed for the study, plus practical commands and workflows.
Keep it concise enough to use during meetings and repeated executions. Do not
infer that an installed or previously selected version has been formally frozen.

## What to record when the document is created

- Study configuration name/revision, agreement date, verification date, and who
  confirmed it. Record later approved changes and their reasons.
- Semgrep CE executable and package version, engine selection, Python/runtime
  version, relevant dependency versions, rule files/IDs, source, version or
  hashes, applicable terms, and known coverage limits.
- CodeQL CLI version, Python extraction/database creation procedure, query-pack
  versions, query suite/IDs, query sources, and limitations. Mark unverified
  details as pending rather than assuming installation is complete.
- Snyk CLI version, Snyk Code setup, account/plan limits, available check
  identifiers/configuration, and limitations. Use the free plan only; do not
  claim the cloud analysis engine is pinned by recording the CLI version alone.
- Each LLM's provider, exact requested model ID, endpoint, client/dependency
  versions, temperature, top-p, output-token limit, and other generation options.
  Distinguish requested aliases from returned model identifiers and fixed
  snapshots; note when a provider does not expose a pinned backend version.
- Explicit fallback policy: a fallback is a different model and must not be
  silently treated as the selected detector. Include exact single-model commands.
- The agreed source snapshot, case names, input scope, exclusions, rule/query
  revision, prompts, output interpretation, and practice versus scored procedure.

## Current sources to consult, not newly frozen constants

The API scripts currently select `mistral-large-4`, `gemini-3.6-flash`, and
`openai/gpt-oss-120b` (Groq) as their first-choice requested IDs. Read the actual
[Mistral](../../CodeBeacon/evaluation-study/llms/mistral-api-test.py),
[Gemini](../../CodeBeacon/evaluation-study/llms/gemini-api-test.py), and
[Groq](../../CodeBeacon/evaluation-study/llms/groq-api-test.py) scripts for settings and
fallback order when preparing the document; do not rely on an old prose copy.
Verify access and account details separately where needed.

The November 23 Semgrep runner verification used installed distribution and CLI
version 1.186.0. The evidence is in the Semgrep run folders, where the successful
practice attempt says `COMPLETED / FINDINGS REPORTED`. Treat this as an observed
version, pending the user's decision to freeze it for the study. CodeQL and Snyk
Code version verification remains pending in the checklist.

## General workflow sections

For each scanner, include installation/version-check commands, where to run them,
how to select a case and local rules/queries, the actual scan command or runner
invocation, and how to inspect findings and diagnostics. Explain exit codes and
how to distinguish completion, no findings, failure, and incomplete analysis.
Include scope, coverage limits, repeatability, practice separation, and applicable
free-access constraints. Do not include secrets or answer-key material in commands
or detector inputs.

The scanner output convention is already implemented for Semgrep and documented
in [the scanner guide](../../CodeBeacon/evaluation-study/scanners/README.md):
exactly `findings.txt` and `run-log.txt` per attempt under the existing
`evaluation-runs/<scanner>/` folder, fixed EST names with hours/minutes and
numbered repeats, and automatic version/command/configuration/diagnostic capture.
The two-file decision supersedes earlier structured-report requirements for new
scanner runs. Do not change existing LLM logging formats as part of this work.

For each LLM, include environment/credential setup without values, an exact
single-model invocation, prompt selection, saved-output location, errors and
incomplete-response handling, and inspection of the returned model identity.
Copy commands from the scripts after verifying them; don't invent unsupported
flags. Document the common study context and generation settings separately
from provider-specific differences.

## Relationship to automated logs

The external Word document records what the study intends to use. The two saved
scanner files record what actually ran. Keeping tool versions, rule/source hashes,
and exact commands in each `run-log.txt` is intentional evidence, not a duplicate
master constants document. Preserve readable scanner output without adding JSON
or SARIF. Structured normalization and automated grading are deferred; assess
what is possible from retained text before designing those later stages.
