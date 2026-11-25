# LLM evaluation workflow

1. Send each model the same study context, the 10 vulnerability types to check, and one project version's files as text. Label each file with its relative path. We can read the files from a local folder; no ZIP upload or new API setup is needed. Don't include vulnerability definitions, detection hints, the answer key, or scanner results.

2. Use the same [detection prompt](llm-detection-prompt.txt) for all three models. The complete [Version A](llm-detection-prompt-version-A.txt) and [Version B](llm-detection-prompt-version-B.txt) text files already include the code. Pass either one with `--prompt-file`. Ask it to check only those 10 types and use the approved output format below.

3. Save each model's full response. Manually compare its findings, locations, and explanations against our shared answer key.

4. Keep our grades in a separate file. Use Found when it gets all known instances of a type with correct locations and good explanations. Use Missing when it misses a type that is present. Use Partially Found when it finds only some instances, or recognizes the problem but gets part of the location or explanation wrong. Record false alarms and made-up details too; don't automatically give an unrelated finding partial credit.

5. Use our grading table to calculate each model's percentage, then compare the results with the scanners to help choose the detection approach. Agree on the points and percentage formula before scoring. Found, Missing, and Partially Found are our grades, not the LLM's output.

## Approved LLM output format

Repeat this block for each of the 10 types, in the prompt's order. Include every detected instance, numbering them from 1 within each type.

```text
Vulnerability: [type we asked it to check]
Detected: Yes

Instance 1:
File: [relative file path]
Location: [function and line number or range]
Explanation: [why the code at this location has this vulnerability]

Instance 2:
File: [relative file path]
Location: [function and line number or range]
Explanation: [why the code at this location has this vulnerability]
```

If it finds none for a type, use only:

```text
Vulnerability: [type we asked it to check]
Detected: No
```

No extra text or Markdown fences in the response. No means the model didn't detect that type; we still check whether that's correct.
