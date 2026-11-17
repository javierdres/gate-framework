---
id: HR-0000
title: A short phrase naming the rule, not justifying it
severity: hard
status: candidate
scope: [cross-cutting]
projects: [cross-cutting]
tags: []
verification: auto
detected_by: pipeline
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
runnable. `verification` says whether a tool checks it today (`auto`), a tool is identified
and queued (`auto-backlog`) or a person or agent applies explicit criteria (`manual`).
`detected_by` says who sees it first when it is missing: the `pipeline`, `self-review` or the
person who `review`s the change. A hard rule with a manual check carries the
`business-defect` tag: it blocks only because breaking it causes a business defect no tool
detects.

```bash
grep -rn "forbidden_pattern" --include="*.ext" .
```

If the check has known false positives, say so here.

## Exceptions

Cases where the rule does not apply, and why. A hard rule needs this section; if there are
none, write "None. This is a hard rule." A soft rule may leave it out. A rule that never
admits a project, change or line exception (see `exceptions.md`) also says
`waivable: false` in its frontmatter.

Optional frontmatter, when the rule only applies to some projects: `applies_when`, a list of
conditions on the project profile (`data.store != none`, `kind ~ worker`). See
`project-profile.md`.

## Evidence

(Optional) Links to real code, incidents or findings behind the rule.

## History

(Optional) One line per change of status or of demand.

- 2026-01-01 · Created as a candidate from the review of a change.
