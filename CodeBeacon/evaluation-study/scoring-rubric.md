# Evaluation study scoring rubric

Agreed November 25, 2026. Apply the same rubric to the three LLMs and three scanners. Score each detector separately for Version A and Version B against the [answer-key comparison table](answer-key.md), using [application-constants.xlsx](application-constants.xlsx) for the detailed evidence.

## Scoring unit and total

Each version has ten target vulnerability types, V1 through V10. Each type earns at most 1 point, regardless of how many instances or supporting locations it has. Present and absent targets both count toward the ten-point maximum.

**Score percentage = (sum of the ten target scores / 10) × 100.**

For example, seven full-credit targets, three partial-credit targets, and no zero-credit targets earn 8.5/10, or 85%. Report this as the rubric score across the ten targets, including correct absences; it is not a percentage of present vulnerabilities found.

## Found, Missing, and Partially Found

Normalize each detector's results into these labels, then compare them with the expected answer. A label alone does not determine the points: Found can be correct or incorrect, depending on the answer key and reported evidence.

| Normalized result | Meaning |
| --- | --- |
| Found | The detector reports the target as present and identifies its instances. Check the locations and explanation against the answer key before awarding credit. |
| Missing | The detector reports no instances of the target. This means absent from its findings, not necessarily absent from the code. |
| Partially Found | The detector identifies the target but covers only some actual instances, or provides incomplete or partly incorrect location information that warrants partial credit in context. |

| Expected answer | Detector result and evidence | Points |
| --- | --- | ---: |
| Found | Correctly identifies the vulnerability and all its instances at the correct locations, with an explanation matching the vulnerable behavior. | 1 |
| Found | Identifies only some instances, or the location/evidence warrants partial credit after contextual review. | 0.5 |
| Found | Misses the vulnerability or otherwise provides an incorrect finding that does not warrant partial credit. | 0 |
| Missing | Reports no instances of the target. | 1 |
| Missing | Reports the target as present. | 0 |

## Reviewing locations and explanations

Judge the reported weakness, location, and explanation together. There is no automatic zero-credit rule for a wrong or unrelated location: decide between 0, 0.5, and 1 using the actual context and evidence. Record a short reason for partial credit and any disputed location judgment, and apply comparable judgments consistently across detectors.

The workbook distinguishes primary vulnerability locations from supporting code. Supporting references help explain an instance; they are not automatically separate instances that each earn points. Repeated warnings for the same instance do not increase the target's score.

Match findings by the behavior they describe, rather than requiring identical wording or an exact CWE label. An omitted or different CWE label alone does not decide the score; assess whether the described weakness and evidence match the target. Vague findings, conflicting claims, and mixtures of correct and incorrect locations require contextual review and a recorded reason.

## False positives and scope

When a detector reports one of the ten targets as present but the answer key says Missing, award 0 for that target. Apply no extra deduction or separate false-positive penalty. Findings outside the ten selected types are excluded from this score. Do not assume a detector cannot produce extra findings.

## Successful runs and retries

For LLMs, map an explicit negative result to Missing. For scanners that report findings only, no finding for a target maps to Missing after a successful, complete scan.

Exclude failed or incomplete scans from scoring and rerun them until a successful, complete scan is available. Do not treat a failed scan as ten Missing results or as a zero-point scored run. Retain the failure log and identify the successful rerun used for grading. A successful scan with no findings is still a valid result.

## Practical grading procedure

1. Select the detector, application version, and successful run; keep its original output available.
2. Make ten rows in V1–V10 order. Record each target's expected answer, normalized detector result, reported locations, and explanation or reference to the raw finding.
3. Compare each row with the answer key and assign 1, 0.5, or 0. Record the reason for partial credit and contextual judgments.
4. Add the ten scores and convert the total to a percentage. Report Version A and Version B separately, each out of 10.

Confusion-matrix treatment of partial credit and detector-to-detector comparisons remain separate checklist tasks; this rubric defines the agreed ten-target score.
