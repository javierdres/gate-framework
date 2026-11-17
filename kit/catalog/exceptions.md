# Exceptions

Skipping a rule on purpose is part of normal work, not a fault. There are legitimate cases: a
production hotfix, a third party's constraint, an external system that leaves no alternative.
What is not legitimate is skipping it in silence, because then nobody knows whether it was a
decision or an oversight, and an agent reads it as the pattern to follow.

## Three levels, in order of preference

**Project.** The case is permanent or recurring. It goes in `exceptions:` of the project
profile (see [`project-profile.md`](project-profile.md)), with the rule, the reason, who
authorised it (a role), the ticket and when it expires.

```yaml
exceptions:
  - rule: HR-0007
    reason: the registry takes up to four minutes to answer; cutting earlier leaves the request in a state nobody can query
    authorised_by: Custodian of backend
    ticket: PROJ-123
    expires: 2027-06
```

**Change.** The case is one-off. It goes in the change request description, under its own
heading, naming the rule, the line and the reason:

```markdown
## Exceptions
- `HR-0007` at `registry_client.py:40`: the registry takes up to four minutes to answer.
  A 300 s timeout instead of 30 s.
```

**Line.** The linter's directive to skip one line, always with the rule and the reason on the
same line. A directive with no reason is a finding in itself.

## Every exception expires

A project exception with no expiry is not accepted, and an expired one stops covering anything.
`bin/applicable.py` reports both. When it expires, the custodian renews it on purpose or the
project complies.

## What no exception covers

A rule with `waivable: false` never admits an exception at any level. They are the rules about
the attack surface: secrets committed to the repository, security controls switched off,
authorisation per endpoint. Breaking one needs the written authorisation of the custodian of
security, recorded in the project profile with a closing date, and it is tracked as an incident
rather than as an exception. `catalog.json` lists which rules these are, so the list never lives
in a document that can drift.

## An exception that switches a gate off carries its debt counted

A job allowed to fail, or a rule left as a warning until some date, detects nothing new every
day until that date. The right form is to freeze the debt: the gate counts against the target
branch and fails only if the count goes up. What is already broken blocks nobody, and whatever
breaks tomorrow fails. See [`ci/README.md`](ci/README.md).
