---
skill: define
stage: 1
name: Definition
triggered_by: [init]
triggers: [specify]
gate: product gate
gate_owner: Product owner
writes_outside: [ticket]
consults: [catalog]
---

# /define — Definition

## Purpose

Turn a need expressed in business language into a statement an engineering team can assess.

## Preconditions

An open dossier. Access to product documentation and to the record of past decisions.

## What it does

- Drafts the statement separating the observed problem from the solution someone already imagined. Most requests arrive with a solution inside and without the problem that motivated it.
- Flags ambiguity instead of resolving it: a statement that admits two readings comes back with both.
- Classifies the data involved: personal, health, financial, or regulated under any applicable rule.
- Looks for precedent: earlier tickets, decisions already taken, related incidents, catalog rules that apply to the domain.
- Checks the product's business rules in force. When the request changes one, it says so in plain words: that is a product decision, not a technical detail, and it has to be taken by product before anyone builds.
- Keeps the team's ticket format and the product owner's own wording. When the product owner already writes a certain way, it starts from that and completes what is missing. A product owner who sees their text replaced stops bringing it.

## What it does NOT do

- Does not design the solution.
- Does not estimate or prioritise.
- Does not move to stage 2 without a data classification.
- Does not create anything in the tracker without the product owner's confirmation.

## Gate

**Product gate.** Owned by: Product owner.

## Dossier

**Reads:** A dossier with the type of work and who is asking.

**Writes:** Problem, context, constraints and data classification.
