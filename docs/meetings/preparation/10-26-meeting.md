# October 26 meeting notes

This is the October 26 preparation walkthrough: the planned order of updates, proposals, questions, and diagrams to present. Dated walkthroughs belong in `docs/meetings/preparation/`. Use the [October 26 checklist](../checklist/10-26-checklist.md) for tasks and record confirmed feedback and conclusions there after the meeting; preserve raw transcripts in [docs/transcripts/](../../transcripts/README.md). This agenda does not establish what was approved or concluded.

## 1. Start with the plan for today

- Quick recap of where we left off.
- Go through the six methods he asked about last time.
- Share my screen and walk through the diagrams: evaluation study first, possible app second, worked example if there's time.
- End by agreeing on what I should have ready for the next meeting.

## 2. Quick recap + what I brought

- Last time, we put the app development idea on hold. The original idea was an app that scans IoT application code for selected vulnerabilities.
- First, we're doing an evaluation study: how well do LLMs find those vulnerabilities compared with code scanners?
- Then, depending on the findings and how much time is left, we can use what we learned to build the app. For example, if LLMs do better, use LLMs for detection in the app.
- I brought the full design proposal to review: study design decisions, the evaluation workflow, the possible app workflow/architecture, and explanations of the six methods. The exact experiment details can be finalized after his feedback.

## 3. Go through the six methods

Keep [six-methods-explanation](../checklist/six-methods-explanation.md) open for the fuller explanations. First four are for the study; last two are for the possible app.

1. **How we picked the vulnerabilities.** Started with the OWASP IoT list and picked password/credential security and insecure communication/data handling. Briefly explain why those fit, and confirm the scope with him. Exact checks and CWE entries still need to be pinned down [selected-vulnerabilities](../../../fall-2026-research/app-idea/selected-vulnerabilities.md)
2. **How the LLMs look at the code.** Same Python examples and selected weaknesses for each LLM. Ask for possible vulnerabilities and where they are. No supplied CWE guidance in this detection step; that comes later for suggestions.
3. **How the scanners look at the code.** Same examples, using Semgrep CE, CodeQL, and Bandit with checks for our selected weaknesses. Collect their findings, locations, and explanations in a shared format. (SNYK code scanner)
4. **How we compare results.** Check each detector against answers we prepared and independently checked beforehand. Briefly cover Found / Missing / Partially Found, proposed scores, and false alarms. Three LLMs and three scanners, with nine LLM-versus-scanner pairings. Show the flow in the evaluation diagram afterward; no need to get stuck on every formula here.
5. **How findings would look in the app.** Saved report for each upload; click a finding for the explanation, location, and code. Separate proposed-changes section. User can mark findings resolved and the unresolved count updates.
6. **How suggestions would be generated.** Findings + relevant code + CWE guidance go to an LLM for explanations and proposed changes. Explain both options and get his thoughts:
   - **Option 1:** Our app looks up the CWE guidance and includes it in the LLM request.
   - **Option 2:** An LLM agent uses a search tool to look up what it needs in our CWE database, then writes the suggestions.

## 4. Share screen — diagrams

1. **[Vulnerability Detection Evaluation](../../../fall-2026-research/diagrams/Vulnerability%20Detection%20Evaluation.png)** — main study workflow. Walk through the shared examples, LLM/scanner runs, grading against known answers, scores, and comparison. Use this to make method 4 easier to follow.
2. **[General Application Workflow ALL AI](../../../fall-2026-research/diagrams/General%20Application%20Workflow%20ALL%20AI.png)** — how the possible app would work if we go with LLM detection. Walk through upload → detection → CWE guidance → suggestions → report. App development still depends on the study and remaining time.
3. **Optional: [GPT vs Semgrep worked example](../../../fall-2026-research/diagrams/Example%20GPT%20vs%20Semgrep%20Diagram.png)** — a more detailed walkthrough of one comparison. These are illustrative outputs, not actual study results. If time is short, just give him the image to look at later.

## 5. Before wrapping up — agree on next meeting's checklist

If the overall design looks good, propose focusing on:

- [ ] Set up the LLMs and confirm the exact models/access.
- [ ] Set up the scanners and the checks we'll use.
- [ ] Finalize the selected vulnerabilities and test cases, including how we'll check the answer key.
- [ ] Nail down exactly how we'll compare: matching findings, partial credit, false alarms, and what counts as better or comparable results.
- [ ] Set the exact scoring values and formulas.
- [ ] Set the run conditions: same inputs/context, settings, number of runs, and how to handle errors.
- [ ] Finalize the prompts and expected output format.

Leave with a clear list of what I'm doing next and any design changes he wants.
