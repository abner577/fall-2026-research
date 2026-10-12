# Evaluation plan

Updated October 12, 2026. This is a proposed procedure with confirmed choices marked below. The open details are listed in [decisions and questions](decisions-and-professor-questions.md).

## What is confirmed

We will compare **three LLMs and three scanners**. Each will analyze the same evaluation cases for the selected weaknesses. We will define independent correct answers, define what **Partially Found** means, and give each detector an accuracy score against those answers. We will also compare every LLM with every scanner, making nine pairings.

This first study measures finding and locating weaknesses. Testing the quality of suggested fixes would be a later evaluation if we develop the application.

## The procedure

1. **Set the scope.** Decide the two targets, related CWE entries, code language, application context, and limits. Explain why these were selected.
2. **Choose the six detectors.** Record their exact names and versions. Explain why they fit the selected code and weaknesses. Coding-focused LLMs can be considered. Model brands alone are not enough to identify the model used.
3. **Build the test set.** Include code with known weaknesses and code where those weaknesses are absent. Include different ways the weaknesses can appear. Decide the number of cases and how they will be checked.
4. **Write the correct answers first.** For each case, identify which target weaknesses are present or absent, their locations, and the evidence. Have the answers checked independently of the six detectors being evaluated.
5. **Write and test the procedures.** Finalize the prompts, scanner commands and rules, supplied context, output format, run settings, and scoring rules. Use separate practice cases to improve the procedure before the main evaluation.
6. **Run all six detectors.** Supply the same cases and comparable context. Keep the answer files away from the inputs sent to detectors. Save the original output and any errors from every run.
7. **Put outputs into a shared format.** Use consistent fields for weakness, file, location, evidence, and uncertainty. Preserve the original output so formatting does not silently change what a detector found.
8. **Grade against the independent answers.** Apply the agreed matching and partial-finding rules. Record correct detections, misses, false alarms, partial findings, and cases the tool could not assess.
9. **Calculate scores and build visuals.** Give each detector its own accuracy score and confusion matrix. Build the nine pairwise comparison summaries. Include supporting measures that explain misses and false alarms.
10. **Interpret and review.** Explain differences, variation between repeated runs, and limits. Meet with the professor to decide whether to conclude the comparison or continue development.

## What a correct answer contains

A correct-answer record should include the case ID, exact code version, target CWE ID, whether the weakness exists, expected file and location, explanation, supporting evidence, known missing context, and who checked the answer.

The independent answer cannot simply be whichever scanner output we trust most. If an LLM helped write an example or an answer, that alone does not validate it. Record how someone checked it using the code and reference guidance. Decide how disputed or incomplete cases will be handled before scoring.

Known answers and code locations are central to static analysis evaluation. See [NIST's SATE V report](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.500-326.pdf).

## Found, Missing, and Partially Found

These are required reporting categories, but their scoring definitions still need a decision.

**Proposed interpretation for grading a known weakness:**

| Category | Proposed meaning |
| --- | --- |
| Found | The detector identifies the expected weakness and meets our agreed location and evidence rules. |
| Missing | The weakness exists in the answer, but the detector does not identify it. |
| Partially Found | The detector identifies a defined part of the expected finding but does not meet the full rule. |

For example, identifying the correct weakness but pointing only to the file, when the rule requires a specific function or line, might count as partial. This example is a proposal, not the final rule.

**A weakness absent from the code is different from a missed finding.** On a case where the target weakness is absent, record either a correct absence or a false alarm. Lack of output alone does not prove that an entire application is safe.

Finding a related weakness is not automatically partial credit. We must define which related weaknesses are in scope and how they match the answer. A detector's uncertainty is also different from a partial detection; record both separately.

Decide how to handle several findings in one case, duplicate findings, wrong locations, wrong CWE labels, out-of-scope findings, missing context, and failed runs.

## Accuracy scores

The student has decided that each of the six detectors should have an accuracy score against the independent answers. The scoring formula and unit still need agreement.

**Proposed starting point:** one scored item is one test case checked for one target weakness. Every detector sees the same items. Include items where the weakness is present and items where it is absent.

Under a simple present-or-absent rule:

**Accuracy = correctly answered items ÷ all scored items × 100.**

For example, 18 correct answers out of 20 scored items gives 90% accuracy. This is an illustration, not a project result.

Before using this formula, decide whether a partial finding counts as correct or incorrect under the main rule. One proposed option is a strict main accuracy score, with partial findings reported separately. Another is a clearly labeled partial-credit score. If we award half credit or any other amount, we must justify and label that rule; it is not already agreed.

A present-or-absent score can hide poor location accuracy, so also report how well the detector found the correct location. Accuracy can also look high if most items have no weaknesses. We should therefore show how many real weaknesses were found and how many warnings were false alarms. The professor should help finalize these supporting measures and the mix of cases.

## Confusion matrices and the nine pairings

A confusion matrix is a table showing how reported answers match the correct answers. For each detector, the basic table has four outcomes:

| Independent answer | Detector reports a weakness | Detector reports no weakness |
| --- | --- | --- |
| Weakness present | Correct detection | Missed weakness |
| Weakness absent | False alarm | Correct absence |

The mapping of partial findings into this table needs to be settled. If we use three answer classes instead, each class needs an independent definition and matching reference answers. A detector's own label cannot serve as the correct answer.

There will be **six detector-versus-answer matrices** for one overall set of results: one for each LLM and each scanner. There may be more if we break results down by target or run.

The **nine pairwise comparison pages** will place the relevant LLM and scanner results side by side. They can include both accuracy matrices, score differences, and examples where outputs disagree. A table comparing their predictions directly measures agreement, not correctness. Label it as an agreement table if we include one.

Run six detectors on the shared cases; then reuse those results for the nine pairings. These are nine comparisons, not nine separate detector systems.

The exact table layout requested by the professor remains a question. See the draft layout in [diagrams](diagrams.md) and the blank forms in [record templates](experiment-records/templates.md).

## Conditions to keep consistent

- Use the same code versions, target list, product description, and agreed file context.
- Define comparable scanner rule coverage. Do not treat an unsupported check or failed setup as proof that a detector cannot find that weakness.
- Record prompts, model settings, scanner rules, commands, versions, and dates.
- Decide whether detection LLMs receive CWE guidance and whether retrieval is allowed. Keep this consistent or label it as a separate experiment condition.
- Give LLMs the output structure, without the scanner's answers for the scored case.
- Decide how many repeated LLM runs to use and how to summarize them. Keep each run rather than choosing the best response.
- Log errors, unsupported cases, and incomplete runs. Agree in advance whether these count in a score or are reported separately.
- If grading requires judgment, agree how a second reviewer checks it. Keep disputed decisions and their reasons.

The final report must include the exact materials and outputs, not just a winning score. [Experiment records](experiment-records/README.md) explains how to keep them.
