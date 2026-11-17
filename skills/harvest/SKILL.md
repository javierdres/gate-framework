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
- Before harvesting a review, looks for open threads a later commit already addressed. With the person's OK it answers each one citing that commit and resolves it, because an addressed thread left open hides that the correction exists. Only then reads the threads, read-only.
- Takes resolved threads and applied suggestions as corrections the team accepted. A thread closed by rejecting a suggestion with a reason is a candidate for the false-positive record, not for a rule.
- Harvests only what meets both conditions: the thread closed with an explicit outcome, and the claim still holds outside that case.
- Classifies every finding into one of five kinds, and says which: a gate that failed (a rule in force that the pipeline or pre-review should have caught and did not), a candidate for automation, a missing rule, a contradiction with the catalog, or a preference without measured adoption. Only a missing rule becomes a new candidate; a preference without measured adoption is reported, not drafted.
- Discards what describes how a particular project is built, which belongs in that project's documentation, and generic good practice with no decision of our own behind it, which the industry baseline already covers.
- Deduplicates against the catalog before drafting. If the rule already exists, it edits the existing one, adding the origin and a line to its history. If an identical rule exists and a reviewer still had to flag it by hand, the candidate is a different one: automate its check, or raise its severity.
- Checks the catalog's seeds too. If a seed nobody adopted already says it, it proposes adopting that seed with this case as its local origin, instead of drafting the rule again.
- Checks the false-positive record and the not-adopted record of the scope. If the finding is there, it shows the reason and asks whether something changed.
- Drafts the rule as a candidate, never as in force, in the scope where it was learned. It rises to cross-cutting only once it is shown to apply in a second place.
- Proposes one change request per scope, to that scope's custodian.
- Prepares the monthly harvest when asked: the candidates of every scope with their age and origin, the false positives recorded since the last one, the candidates that already applied in a second place, and the rules in force nobody cited, as a short list per custodian of what each has to decide.
- Always closes with three lists: harvested, discarded with the reason, and pending decisions.

## What it does NOT do

- Does not promote a rule to in force.
- Never writes a rule without confirmation, rule by rule.
- Does not answer or resolve a thread on the code platform without the person's explicit OK.
- Does not settle in a review thread a question whose answer will become a rule. It raises it to the catalog's custodian, and the change merges with the behaviour the catalog already allows.
- Does not invent rules with no origin. The origin is a link when one exists, and otherwise the pattern it came from, never a name or a client's data.

## Gate

**Per-rule gate.** Owned by: Standard custodian.

## Dossier

**Reads:** Resolved threads and root causes, the catalog, its seeds and its rejection records.

**Writes:** Candidate rules, false-positive entries for rejected suggestions, and the three-list report.
