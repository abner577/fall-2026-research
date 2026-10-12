# Possible application workflows

Updated October 12, 2026. These workflows describe the possible development milestone. They do not mean development has started or a detection method has been chosen.

## What both workflows do

A user provides code. The application identifies possible weaknesses and where they are. It then sends the findings, relevant code, and useful CWE guidance to an LLM to request suggested changes. It returns a report for the user to review and validate.

The comparison study helps us choose the detection method. It does not automatically show that the final suggestions are correct; that part would need its own checks.

## Workflow A: use a scanner to find weaknesses

1. Receive code and a short description of what the software does.
2. Prepare the files and identify the supported code. Keep file names and locations intact.
3. Run the selected scanner with the agreed checks.
4. Collect possible findings, locations, code evidence, and any limits of the scan.
5. Retrieve the relevant CWE entries and guidance for those findings.
6. Ask the LLM what changes would address the findings, using the code and guidance.
7. Return a report with the issue, location, explanation, suggested change, source, and any checks still needed.

The original app workflow used this approach. The choice of scanner remains open.

## Workflow B: use an LLM to find weaknesses

1. Receive code and a short description of what the software does.
2. Prepare the files and identify the supported code. Ordinary file preparation does not need AI.
3. Ask the detection LLM to identify the agreed weaknesses and related weaknesses, with file locations and evidence.
4. Read and check the structure of its findings. Record uncertainty and missing context; a well-formatted answer is not proof that the finding is right.
5. Retrieve the relevant CWE entries and guidance for those findings.
6. Make a subsequent LLM request for suggested changes, using the findings, code, and guidance.
7. Return the same kind of report as in Workflow A.

The detection and suggestion stages could use the same model in separate requests or different models. That choice is pending. An agent that makes retrieval requests may require several LLM calls within the suggestion stage, so this is a sequence of stages rather than a promise of exactly two API calls.

## General designs and designs for our two targets

For **each** workflow, we need a general diagram and a study-specific diagram.

The general design describes a reusable process with a chosen target list. It does not claim that the application detects every vulnerability.

The study-specific design names the two finalized targets, included related CWE entries, selected model or scanner, prompt or rule set, and supported code. For now, those names remain placeholders. Our current focus-area notes are proposals rather than two approved individual weaknesses.

A general detection request might say: identify weaknesses from the supplied target list and the allowed related entries, with locations and evidence. Our specific request must name the exact fixed list and its limits. These are descriptions of prompt intent; the exact prompts still need to be written and recorded.

## The final suggestion stage

The request should explain, in practical terms: given these findings, their code locations, the relevant code, and the supplied CWE guidance, what changes should we make, why would they help, and what should we check afterward?

Useful outputs include a suggested change or code example, an explanation tied to the finding, the source guidance used, assumptions, and checks needed before using the change. These are suggestions to review, not automatically validated fixes.

CWE entries can include mitigation advice and examples. They do not always provide a complete checklist or a corrected version of our code. The LLM has to apply the available guidance to the actual situation. See [MITRE's CWE-798 entry](https://cwe.mitre.org/data/definitions/798.html) for an example of the information available.

## Retrieving guidance: application or agent?

**Application-controlled retrieval:** the application looks up the detected CWE ID, selects the useful guidance, and supplies it with the code and findings. This is often called retrieval-augmented generation, or RAG: retrieve information, then use it to help generate an answer. See the [RAG research paper](https://arxiv.org/abs/2005.11401).

**Agent-controlled retrieval:** an LLM has tools that let it request CWE entries or search relevant passages. The application runs those requests and returns the results. The LLM can ask for more information before suggesting changes. The model and its tools together form the agent. See [Anthropic's explanation of agents and workflows](https://www.anthropic.com/engineering/building-effective-agents).

Yes, the proposed agent is possible. We would expose a limited lookup or search tool connected to our database. The LLM would not independently open a database without that connection.

In both options, the retrieved text still enters the LLM's context. An agent changes who decides what to retrieve and when; it does not eliminate the need to supply readable guidance or the limits on how much a model can read.

**Proposed starting choice, not a decision:** use an exact CWE ID lookup when the finding already has an ID. Use vector search, which finds passages with similar meaning, when additional guidance is needed. Start with application-controlled retrieval and add agent-controlled searches if useful. A vector database is an implementation option, not a requirement for exact ID lookup.

We have discussed storing CWE information in a database, but these notes do not establish that the database has already been built. Its contents, source versions, update process, and retrieval method need decisions.

Keep retrieval for recommendations separate from the initial detection comparison unless the evaluation explicitly includes it. Giving some detection models extra searches would change what we are comparing.

## Still open for development

Local versus deployed operation; input format; initial language and framework; application or device context; selected detector; models for the two stages; code size and cross-file context; database and retrieval design; how suggested changes will be validated; and whether development fits the remaining schedule.

See [the question list](decisions-and-professor-questions.md) for the decisions to take to the professor, and [diagrams](diagrams.md) for workflow drafts.
