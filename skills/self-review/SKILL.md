---
skill: self-review
stage: 6
name: Pre-review
triggered_by: [build]
triggers: [verify, harvest]
gate: author gate
gate_owner: The builder, over their own work
writes_outside: [change proposal, QA script]
consults: [catalog, false-positives]
---

# /self-review — Pre-review

## Purpose

Review the change in private so it reaches human review already cleaned up. Its output goes to the author, never to a shared system.

## Preconditions

A branch ready. Access to every repository the change touches.

## What it does

- Identifies the ticket from the branch and pulls its definition without editing it.
- Determines every repository the change touches and checks none was left half done.
- Runs linters and static analysis. A syntax error is blocking.
- Checks every claim about project conventions against the actual code.
- Runs a full hard-rule pass if the change touches authentication, authorisation, tenant isolation, or the data stage 1 classified as sensitive.
- Cross-checks the artefacts that travel together: migrations with their changelog entry, instrumentation with the plan, documentation with the code it describes.
- Compares the whole branch against the base, not just the latest commits, against the criteria from stage 2.
- Reviews only what the change introduced. What was already there is not a finding of this change.
- Runs the automated flows of the use cases the change touches, and checks that the cases the ticket added are in the product's catalog and automated.
- Drafts the change proposal and the functional verification script.
- Hands whatever has no rule but deserves one to /harvest, as a suggestion.

## What it does NOT do

- Never publishes findings to any shared system. The change proposal and the verification script are published only on the author's approval.
- Does not merge.
- Does not replace human review.

## Gate

**Author gate.** Owned by: The builder, over their own work.

## Dossier

**Reads:** The implemented change.

**Writes:** Findings resolved, and, on the author's approval, a change proposal and a verification script.
