# How we're going to write the scanner rules

November 23, 2026

These are just notes to remember what we agreed. We're starting with Semgrep.

## Keep the same ten things we're looking for

1. Hardcoded credentials.
2. Weak password requirements.
3. Unsafe password storage.
4. Unencrypted sensitive communication.
5. Secrets exposed in logs or files.
6. Missing endpoint authentication.
7. Missing endpoint authorization.
8. Predictable generated credentials.
9. Disabled certificate verification.
10. Insufficient restriction of repeated login attempts.

We're keeping these categories. What we need to rewrite is the plain-English
description of what a scanner should look for in each one.

## Start from the problem, not our code

We won't open our application code or use its placement notes to work out how to
make a rule catch our examples. We already know some of the code from earlier
work, so this doesn't mean we've never seen it. It means we won't use those
details to design the rules.

For example, we can say: "Look for HTTPS requests that turn off server
certificate checking, including retries."

We won't say: "Look in this file, in this function, for the exact line we put
there." The requirements and rules shouldn't depend on our application names,
known secret values, or known vulnerable locations.

## Use existing checks first

For each category, look for existing Semgrep rules that match the general
problem. Choose them because of what they check, not because we've tried them
on our application and know they catch our example.

If we need more coverage, we can add a few custom rules for other ways the same
problem can appear. That might mean two or three custom rules for a category,
but there's no required number. Don't add rules just to fill a quota.

Use separate small examples to check whether a rule works and whether it leaves
similar safe code alone. Don't copy our application's defect into those examples
as a way to tune the rule to it.

## Keep the explanations with the rules

We don't need another document listing every exact rule. Keep the rule's name,
what it checks, and any important limits in the rule file itself. For existing
rules we use, keep their original IDs and source/version information with the
saved rule files or configuration. Make it clear which rules we wrote or changed.

## Let the results be the results

Once we run the rules on our application, some things might be found and some
might be missed. That's fine. Don't change a rule just to make a known missed
line get reported. Missing coverage is something to record, not hide.

We're not adding extra held-back cases or a requirement to freeze everything as
part of this approach. Those earlier suggestions aren't part of this decision.
We're using the existing application versions, so the results describe these
cases; general rules alone don't prove how well a scanner works on every project.

The next step is to write the general descriptions for the ten categories, then
find existing checks and add custom rules where needed. This note records the
approach; it doesn't implement or claim coverage for those rules yet.
