# Governance

Who approves what in this repository and what can change. `CODEOWNERS` translates it into
rules the code platform enforces on every change request.

The SDLC is organised by roles, not by people. The whole repository names roles; names live
only in the tables at the end of this document. When someone rotates, those tables change and
nothing else.

## Current phase: formulation

While the SDLC is being formulated, the orchestrator is responsible for everything: proposes,
approves and merges. Custodians give their view and get ready, but do not approve yet.

The phase ends when its exit criteria are met, checked on the review date:

- [ ] A person other than the orchestrator installed the SDLC alone and has access verified
- [ ] A product owner used it on a real requirement
- [ ] A builder took one of those without product questions
- [ ] A rule harvested from real work entered the catalog

Review date: <YYYY-MM-DD>. If none is met by then, the approach is reviewed before building
more. From the day formulation ends, the orchestrator is bound by the same incompatibilities as
everyone else.

## Roles

| Role | What they do |
| --- | --- |
| Orchestrator | Builds and evolves the SDLC, chooses the assistant, assigns roles and profiles, decides when formulation ends |
| Custodian of <layer> | Approves the rules of that layer |
| Custodian of operations | Approves operations rules, guides and tools, and everything that touches production |
| Custodian of security | Approves security rules and owns security findings until they close |
| Custodian of product | Approves product rules, product context and product skills |
| Product owner of each product | Decides what is built in their product and validates its business rules and use cases |

## What can change and who approves it

| Part | Anyone may change it by change request | Approves |
| --- | --- | --- |
| `AGENTS.md`, `GOVERNANCE.md`, `CODEOWNERS`, `method/`, `GATE.md` | Yes | The orchestrator and every custodian |
| Rules with scope `cross-cutting` | Yes | Every custodian |
| Rules of any other scope | Yes | That scope's custodian, as listed in `catalog/scopes.md` |
| `products/<product>/` | Yes | The product owner and the custodian of the affected layer |
| `tools/`, `adapters/` | Yes | The custodian of operations |
| Skills | Yes | The custodians of the profile the skill serves |
| `catalog/calibration/false-positives.md` | Yes | No approval: whoever discards writes the reason |

Nobody merges their own change request once formulation ends.

## How a rule is born

1. A review, an incident or a correction leaves a candidate rule, with its origin.
2. It enters by change request to its scope, marked as a candidate. It never blocks.
3. At the monthly harvest its custodian approves it or discards it with the reason.
4. A blocking rule needs the agreement of every custodian.

A rule is born in the scope where it was learned, and becomes cross-cutting once it is shown to
apply in a second place.

## Monthly harvest

Thirty minutes a month with the custodians: candidates, discards, candidates that applied in a
second place, rules in force nobody used, and what did not work in the method. Whatever is
decided stays in the repository.

## Who holds each role today

| Role | Person | Verifiable identity |
| --- | --- | --- |
| Orchestrator | | |

## Profiles enabled

The assistant identifies a person by their verified account, never by the name they type. A
profile not in their row cannot be used.

| Person | Verifiable identity | Profiles |
| --- | --- | --- |
| Everyone else | — | building profiles |
