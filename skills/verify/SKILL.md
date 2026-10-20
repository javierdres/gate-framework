---
skill: verify
stage: 8
name: Functional verification
triggered_by: [self-review, person]
triggers: []
gate: QA gate
gate_owner: Verifier
writes_outside: []
consults: []
---

# /verify — Functional verification

## Purpose

Check against the criteria from stage 2, on the running system.

## Preconditions

The change deployed to a test environment. The script drafted in stage 6.

## What it does

- Runs the automated flows of the product's validated use cases, against a deployed test environment, on the machine of whoever verifies and with that person's own configuration.
- Refuses to run against a host that is not on the allowlist, and cuts any real-world effect (charging, buying, signing, writing to third parties) unless the environment simulates it and the run authorises it.
- Leaves local evidence of every run: who ran it, against what, and the result. A flow that never ran is not delivered as done.
- For whatever cannot be automated, writes the script with one checkbox per verifiable result, not one per case, so a failure points at what failed.
- One block per affected component, naming what to look at on each screen.
- The precondition written as a check the tester can perform, with what to do if it is not met.
- Steps executable with the tools the tester already has.
- Known false alarms, stated up front.
- What to do with whatever cannot be tested in that environment: leave it unchecked and note it, never mark it failed.

## What it does NOT do

- Does not sign off on any criterion. The verifier does, whoever ran the check.
- Never runs against production.
- Does not write a flow from what the code does today. The case comes from what product validated.

## Gate

**QA gate.** Owned by: Verifier.

## Dossier

**Reads:** The validated use cases of the product, and the verification script.

**Writes:** The flows run and their evidence, and a result per criterion.
