---
skill: review
stage: 7
name: Change review
triggered_by: [person]
triggers: [harvest]
gate: reviewer gate
gate_owner: A reviewer, not the builder
writes_outside: [comments]
consults: [catalog, false-positives]
---

# /review — Change review

## Purpose

Have someone other than the author validate the change, with support. Runs several times while the review lasts.

## Preconditions

An open change proposal. Access to every repository the ticket touches.

## What it does

- Reads the discussion threads across every change in the ticket in one pass, splitting them into open ones, which need answering, and resolved ones, which are the input for /harvest.
- Checks every suggestion from another reviewer against the actual code before backing it or pushing back. A pattern may be established in one component and absent in another.
- Raises its own findings with severity, file and line, and with the catalog rule id when the finding comes from there. Without that id nobody can go and argue with the rule.
- Consults the false-positive record before raising something the team already rejected.
- Watches the blast radius across components.
- Checks the change is up to date with its target branch, and raises conflicts or drift as a request to rebase.
- Reviews only what the change introduced. What was already there is not raised.
- Reminds that a push clears the approval: the branch is updated first, the review asked for afterwards.
- Triggers /harvest on every pass, over the threads resolved since the last one.

## What it does NOT do

- Never publishes a finding without confirmation, case by case.
- Does not approve or merge.
- Does not replace functional verification.

## Gate

**Reviewer gate.** Owned by: A reviewer, not the builder.

## Dossier

**Reads:** Change proposal and verification script.

**Writes:** Threads answered, findings published, decisions for stage 12.
