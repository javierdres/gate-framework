---
skill: deploy
stage: 9
name: Deployment
triggered_by: [person]
triggers: [operate, validate-outcome]
gate: deployment gate
gate_owner: Operations owner
writes_outside: [production]
consults: []
---

# /deploy — Deployment

## Purpose

Put the change in production and check with data that it behaves the way the criteria said it would.

## Preconditions

Stage 8 approved. Instrumentation deployed. A rollback procedure that has been exercised, not merely documented.

## What it does

- Before each release, runs every automated flow of the product. A regression blocks the release.
- Gathers and presents whatever manual steps the deployment requires, instead of letting them surface during the window.
- Compares observed behaviour against the non-functional criteria from stage 2, using the data sources from stage 10.
- Watches the window after deployment for deviations from the previous baseline, not from an invented threshold.
- On detecting a deviation, presents the evidence and proposes a rollback.

## What it does NOT do

- Never takes any action on production without confirmation.
- Does not decide to roll back: it proposes it.

## Gate

**Deployment gate.** Owned by: Operations owner.

## Dossier

**Reads:** A change approved by QA.

**Writes:** A recorded post-deployment check, or a rollback with the evidence for it.
