# Research notes: start here

Updated October 12, 2026. These files record the change discussed in the October 12 mentor meeting and the student's follow-up decisions. They are planning notes; no experiments have been run as part of this documentation work.

**Current direction:** compare three large language models (LLMs) with three static code analysis tools. An LLM is an AI model that works with text and code. A static code analysis tool, called a scanner in these notes, checks code without running the application. Application development is a possible second milestone.

We call both LLMs and scanners **detectors** when discussing their shared job of finding weaknesses. A **finding** is one issue a detector reports, along with its location and evidence.

## Where to find things

| File | What it answers |
| --- | --- |
| [Direction and history](direction-and-history.md) | What changed, what we keep, and when we decide whether to build the app. |
| [Evaluation plan](evaluation-plan.md) | How the three-versus-three comparison will work, including correct answers, partial findings, scores, and comparison tables. |
| [Application workflows](application-workflows.md) | How the app could work with either detection method, and how CWE guidance supports the final suggestions. |
| [Diagrams](diagrams.md) | All required visuals, draft diagrams, and what still needs to be filled in. |
| [Decisions and professor questions](decisions-and-professor-questions.md) | Confirmed decisions, unresolved choices, and questions to take to the professor. |
| [Experiment records](experiment-records/README.md) | Where to keep the exact tools, prompts, cases, answers, settings, outputs, and results. |
| [Record templates](experiment-records/templates.md) | Copyable forms for recording the experiments and their scores. |
| [Earlier research plan](history/research-plan-before-2026-10-12.md) | The development-first plan before this change. |
| [Earlier app workflow](history/app-workflow-before-2026-10-12.md) | The original scanner-first application workflow. |

The short [research plan](../research-plan.md) now reflects the comparison-first direction. Older preparation files remain useful background, but they do not establish final tool choices or the current order of work.

## First things to do

1. Take the unresolved scope and scoring questions to the professor.
2. Define the two targets, related weaknesses, and supported code for the study.
3. Choose three LLMs and three scanners that fit that scope.
4. Prepare test cases and independently checked answers.
5. Finalize the prompts, procedures, scoring rules, and diagrams.
6. Run a small practice batch, fix problems with the procedure, and then run the main comparison.
7. Review the evidence and remaining time with the professor before deciding on app development.

Do not fill a blank result with a guess. Use **Not chosen**, **Not run**, or **Needs a decision** until the information exists.
