# Research plan

Updated October 12, 2026. This is the working plan following the mentor meeting and the student's follow-up decisions. The revised scope, scoring rules, and schedule still need professor review.

**Working project name:** CodeBeacon. The earlier title was "CodeBeacon: AI IoT Code Scanner." A revised formal title has not been agreed.

**Current study:** compare three LLMs with three static code analysis tools for finding selected weaknesses in IoT software code. Application development is a possible second milestone.

## Problem and purpose

IoT software can contain weaknesses that expose information or allow unauthorized access. Before choosing how our proposed application should find those weaknesses, we will compare LLMs with code scanners on shared test cases. We want to learn how accurately the selected detectors identify the targeted weaknesses and their locations, including when they miss a weakness or raise a false alarm.

The process will be described generally, while the actual experiment uses a fixed, limited set of targets. The current two focus areas are proposals that still need to be translated into an agreed list of specific CWE entries and checks.

## Milestone 1: evaluation study

1. Document how we choose two targets and related weaknesses from CWE.
2. Choose three LLMs and three scanners suited to the code and checks.
3. Prepare cases with and without the targeted weaknesses and define independently checked answers.
4. Write exact prompts, scanner procedures, a common result format, and scoring rules, including Partially Found.
5. Run all six detectors on the shared cases and preserve exact inputs and outputs.
6. Grade against the independent answers, assign accuracy scores, and organize the six detector matrices into nine LLM-versus-scanner comparison pages.
7. Explain results and limits; review with the professor whether to conclude the study or continue development.

## Milestone 2: possible application development

If evidence and time support it, build a limited app using the chosen detection method. Both possible approaches share the final step: use findings, relevant code, and retrieved CWE guidance in an LLM stage that suggests changes. Those suggestions need their own review and validation.

The old development plan is preserved in [the history folder](research/history/research-plan-before-2026-10-12.md). Development is no longer the first promised milestone.

## Planned documentation and deliverables

- Plain-English methods and reasons for target and detector selection.
- General and target-specific diagrams for both app workflows.
- General and specific evaluation designs, plus six detector-specific procedures.
- Exact cases, independent answers, prompts, commands, settings, original outputs, grading, scores, and comparison visuals.
- A conclusion supported by the evaluated cases and a recorded milestone decision.
- If continuing, a prototype and a separate evaluation of its findings and suggested changes.

## Schedule to confirm

The earlier plan targeted an initial prototype and preliminary evaluation by the first week of December 2026, and a final poster by the end of the third week of January 2027. Those were earlier planning dates, not newly confirmed deadlines for the revised direction.

Ask the professor which dates and deliverables still apply. Set dates for design review, practice runs, main comparison, and the development decision after resolving scope and workload. No revised experiment or development dates have been agreed in these notes.

## Detailed notes

Start with [the research notes index](research/README.md). The [evaluation plan](research/evaluation-plan.md), [diagram checklist](research/diagrams.md), and [professor questions](research/decisions-and-professor-questions.md) describe the practical next work and all current open decisions.
