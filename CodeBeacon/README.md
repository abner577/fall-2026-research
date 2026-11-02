# CodeBeacon: research execution and application

**Required writing rule for detector inputs — November 2, 2026:** application
files supplied to LLMs or scanners must use ordinary project language. Do not
describe them as a demo, simulation, simulator, toy, teaching exercise, benchmark,
or deliberately vulnerable study case in comments, docstrings, README text,
configuration names, CLI help, or log messages. Use direct descriptions such as
"device client," "temperature reading," and "fan state." Keep comments sparse
and explain behavior only when useful. Do not add vulnerability labels, CWE IDs,
answer-key hints, or instructions aimed at the detector. Apply this consistently
to both Version A and Version B. Review all files supplied to detectors before
freezing a case, including its README and configuration template.

The detector input boundary is the selected application's `version-A/` or
`version-B/` source package, excluding `.env`, `.local/`, `.venv/`, and caches.
This README, the enclosing study READMEs, explanation notes, verification
material, and preparation documents stay outside that package. Preserve the
actual software-generated sensor and fan provenance in those external records.
Neutral project wording does not establish physical hardware integration; do
not claim hardware measurements, deployment, or verification that did not occur.
Keep the supplied project context consistent across detectors and record it
with the run evidence. This rule supersedes earlier guidance that placed
simulation explanations in the version-level project guide.

**November 2 folder clarification (supersedes older placement guidance below):** this folder is for actual implementation and execution materials. Application design, code-case planning, vulnerability selections and placement notes, and the answer key belong in [evaluation-study-preparation/](../fall-2026-research/evaluation-study-preparation/). Do not put preparation documents here. Keep them separate from detector input packages.

`CodeBeacon/` is the working root for carrying out the research. The repository has two main folders: this folder for execution and [fall-2026-research/](../fall-2026-research/) for the planning and meeting record. The repository-level [README](../README.md) and [research plan](../research-plan.md) provide overall context.

`CodeBeacon/` has two main subfolders:

| Folder | Purpose |
| --- | --- |
| [evaluation-study/](evaluation-study/) | Everything used to prepare and execute the evaluation study, including its code, documents, prompts, configurations, logs, evidence, analyses, and results. |
| [app/](app/) | The optional CodeBeacon application and its code, documentation, assets, and architecture, if the idea proceeds and there is time to develop it. |

Put the evaluation study's actual materials under `evaluation-study/`: the coherent IoT test project and its controlled versions, vulnerability placement explanations, independently reviewed answer keys, exact prompts and revisions, scanner configurations and commands, run settings, complete raw responses and reports, errors, screenshots, images, verification evidence, grading, scores, comparisons, and conclusions from the experiments. Keep answer keys and injection notes separate from the project inputs given to detectors.

Use `evaluation-study/` for the working study designs and revisions to earlier evaluation proposals. If application development proceeds, its code, configuration, tests, documentation, architecture, and related assets belong in `app/`. The evaluation project is study material; it is distinct from the optional CodeBeacon application being developed later.

The earlier planning notes, proposal diagrams, architecture discussions, and supporting images remain under [fall-2026-research/](../fall-2026-research/). Consult [the planning notes](../fall-2026-research/coming-up-w-research-plan/evaluation-plan.md) and [meeting records](../fall-2026-research/docs/) for their rationale and status. Weekly transcripts, preparation, checklists, and meeting conclusions continue to belong in `fall-2026-research/docs/`, including future meetings. Experimental conclusions and run evidence belong in `evaluation-study/`.

AI assistants should read the planning and meeting context before acting, then save study execution work under `CodeBeacon/evaluation-study/` and optional application development work under `CodeBeacon/app/`. Preserve exact inputs, code versions, prompts and revisions, complete outputs, errors, commands, configurations, settings, versions, dates, and reasons for changes. Keep raw evidence separate from normalized results and retain practice and unsuccessful runs. Record why and where each vulnerability was inserted and how and by whom it was verified. Do not present a proposed design, illustrative output, or unchecked answer key as a completed experiment or validated result.

The three selected scanners are Semgrep Community Edition, CodeQL, and Snyk Code, using Snyk's free plan only. The comparison remains the first milestone; application development depends on the findings and available time. This README establishes where work belongs; detailed subfolders can be chosen as the study is implemented, and no experiment, codebase, or completed implementation is implied by this guide.

The three selected detection model families are Mistral Large 4 (`mistral-large-4`), Gemini, and GPT-OSS-120B through Groq (`openai/gpt-oss-120b`). Mistral replaces the earlier direct OpenAI API choice as of October 29, 2026. GPT-OSS through Groq replaces Qwen; its verified fallback is GPT-OSS-20B (`openai/gpt-oss-20b`). The Mistral request script uses `ministral-14b-2512` and `ministral-8b-2512` as verified backups; these are alternatives within one detector branch, not additional study detectors. Select the exact Gemini study model and verify study allowances before scored runs. GPT-OSS-120B and its fallback, GPT-OSS-20B (`openai/gpt-oss-20b`), both returned HTTP 200 practice responses through Groq on October 29, 2026.

The Mistral script and Python requirements now live in `evaluation-study/`. Run its commands from that folder; `.env` and `.venv` also belong there. The script saves request logs to `evaluation-study/evaluation-runs/mistral/`. Keep preparation/practice outputs distinct from scored study outputs within the evaluation-study folder.
