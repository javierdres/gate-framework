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
- Writes new use cases into the ticket without an id. The id is assigned when a case enters the product's catalog, so two tickets in flight never take the same number.
- Prepares the handover. It suggests one or two people to take the work, each with a reason drawn from the product's context and from who has worked on the code involved; product decides with the engineering lead. Creating the ticket and assigning it are two separate confirmations.
- Treats the handover as finished only when the builder confirms they understood it, and records who took it, which questions were answered and what changed in the ticket. A ticket created is not a ticket understood.
- When the same gap keeps appearing across requirements, such as a missing success criterion, proposes it as a candidate product rule.

## What it does NOT do

- Does not define the implementation.
- Does not accept a non-functional criterion without a number.
- Does not turn a use case into a test before product validates it.
- Does not assign the ticket on the strength of the creation's approval.

## Gate

**Requirements gate.** Owned by: Product owner and engineering lead.

## Dossier

**Reads:** Problem and data classification.

**Writes:** Functional and non-functional acceptance criteria, compliance requirements, validation window.
