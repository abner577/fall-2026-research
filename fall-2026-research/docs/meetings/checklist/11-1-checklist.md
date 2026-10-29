# Follow-up checklist: 11-1

Carry out the actions below under [CodeBeacon/](../../../../CodeBeacon/README.md), saving project code, prompts, outputs, images, verification evidence, and working designs there. This checklist and other meeting records remain in `fall-2026-research/docs/`.

Working checklist following the [October 26 conclusions](../conclusions/10-26-conclusions.md). The filename does not confirm the date of the next meeting. These are pending actions, not completed work or experiment results.

- [ ] Choose or build a coherent Python IoT application with connected features. Decide the framework and scope; APIs and a database are possible examples, not requirements. Preserve a baseline intended to lack the selected weaknesses, then prepare controlled vulnerable versions instead of unrelated demonstration snippets.
- [ ] Define the specific weaknesses and CWE entries within the two accepted broad focus areas. Choose a manageable variety and count; document why each belongs in scope and why its placement fits the application.
- [ ] Record each injection's exact code change, file, and location, and prepare the answer key. Verify target presences and absences independently; record reviewer, method, date, evidence, and outcome. Arrange professor review before scored runs without assuming that it has already occurred.
- [ ] Update the evaluation diagram to show one common IoT project feeding both detector branches, with the answer key and injection notes kept separate from detector inputs. Text descriptions have been updated; the image still needs revision.
- [ ] Set up the selected scanners: Semgrep CE, CodeQL, and Snyk Code. Use the Snyk free plan only and check actual account limits, relevant coverage, and report usability; Snyk Code replaces Bandit. No paid access or upgrade is authorized. See [scanner notes](../../../coming-up-w-research-plan/scanner-tools.md#snyk-code-free-plan).
- [ ] Set up the LLM and scanner access without additional spending; record exact models, versions, settings, and checks. Finalize prompts, common reporting fields, matching rules, partial credit, false alarms, and scoring before scored runs.
- [ ] Give every detector the same project version and agreed context without the answer key or injection notes. Preserve the exact supplied code and input context for each run.
- [ ] During preparation and every run, AI assistants must save exact prompts and revisions, complete responses, scanner reports/errors, code versions, commands, configurations/rules, settings, and dates. Keep original evidence separate from normalized tables and scores, retain practice and unsuccessful runs, and document the reasons for revisions.
