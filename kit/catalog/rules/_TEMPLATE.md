---
id: HR-0000
title: A short phrase naming the rule, not justifying it
severity: hard
status: candidate
scope: [cross-cutting]
projects: [cross-cutting]
tags: []
origin:
  - The review thread, incident or postmortem it came from, told as a pattern
approved_by: []
created: 2026-01-01
updated: 2026-01-01
supersedes: []
superseded_by: null
---

# HR-0000 · A short phrase naming the rule

## Do not

What is forbidden, concretely. Nameable in code: a function, a pattern, a way of writing
something. If you cannot point at it in a diff, it is not a rule yet.

## Do instead

The concrete alternative that replaces it. With code if it helps.

## Why

What breaks if it is not followed. Real impact, not "it is bad practice".

## How it is checked

The heuristic a person or an agent uses to check this rule against a change. Concrete and
runnable:

```bash
grep -rn "forbidden_pattern" --include="*.ext" .
```

If the check has known false positives, say so here.

## Exceptions

Cases where the rule does not apply, and why. A hard rule needs this section; if there are
none, write "None. This is a hard rule." A soft rule may leave it out.

## Evidence

(Optional) Links to real code, incidents or findings behind the rule.

## History

(Optional) One line per change of status or of demand.

- 2026-01-01 · Created as a candidate from the review of a change.
