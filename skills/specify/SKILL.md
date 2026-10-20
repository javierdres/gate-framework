---
skill: specify
stage: 2
name: Requirements
triggered_by: [define]
triggers: [refine]
gate: requirements gate
gate_owner: Product owner and engineering lead
writes_outside: [ticket]
consults: [catalog]
---

# /specify — Requirements

## Purpose

Settle what done means, in terms that can be checked.

## Preconditions

Stage 1 approved.

## What it does

- Proposes acceptance criteria that can be verified. A criterion you cannot check against the finished system is not a criterion.
- Demands numbers on non-functional criteria: response time, expected volume, required availability, tolerable recovery window. Without a number they cannot be verified in stage 8 or watched in stage 10.
- Derives the compliance requirements that follow from the data classification: retention, audit trail, encryption, minimisation, data subject rights.
- Points out which criteria will need instrumentation, so stage 3 accounts for it.
- Sets the waiting period after which stage 11 can validate the outcome.
- Proposes the use cases the requirement adds or changes, in business language, and asks product to validate each one. A requirement that changes no journey says so, with its reason.

## What it does NOT do

- Does not define the implementation.
- Does not accept a non-functional criterion without a number.
- Does not turn a use case into a test before product validates it.

## Gate

**Requirements gate.** Owned by: Product owner and engineering lead.

## Dossier

**Reads:** Problem and data classification.

**Writes:** Functional and non-functional acceptance criteria, compliance requirements, validation window.
