---
skill: harvest
stage: 12
name: Learning
triggered_by: [review, postmortem, self-review, person]
triggers: []
gate: per-rule gate
gate_owner: Standard custodian
writes_outside: [catalog]
consults: [catalog, false-positives]
---

# /harvest — Learning

## Purpose

Make decisions and root causes outlive the conversation or the shift where they appeared.

## Preconditions

Write access to the standards repository. Catalog and false-positive record up to date.

## What it does

- Takes four sources, in this order of strength: the root cause of an incident, the resolved threads of a review, a finding of the pre-review that no rule covers, and a correction made during a session. The first two are the primary sources; the last two are suggestions the person may choose to raise.
- Runs on its own when a review closes, when a postmortem closes and when a pre-review leaves something without a rule. When review happens outside the assistant, as it often does in phase one, the person runs it when the review closes, and the SDLC's instructions remind them.
- A pre-review is private, so a candidate drawn from it is raised only if its author chooses to, and its origin is told as a pattern ("pre-review of a change to the payments module") rather than linked to a private record.
- Harvests only what meets both conditions: the thread closed with an explicit outcome, and the claim still holds outside that case.
- Discards what describes how a particular project is built, which belongs in that project's documentation, and generic good practice with no decision of our own behind it, which the industry baseline already covers.
- Deduplicates against the catalog before drafting. If the rule already exists, it edits the existing one, adding the origin and a line to its history.
- Drafts the rule as a candidate, never as in force.
- Always closes with three lists: harvested, discarded with the reason, and pending decisions.

## What it does NOT do

- Does not promote a rule to in force.
- Never writes a rule without confirmation, rule by rule.
- Does not invent rules with no origin. The origin is a link when one exists, and otherwise the pattern it came from, never a name or a client's data.

## Gate

**Per-rule gate.** Owned by: Standard custodian.

## Dossier

**Reads:** Resolved threads and root causes.

**Writes:** Candidate rules and the three-list report.
