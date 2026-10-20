---
dossier: EXP-0000
title: A short phrase naming the work
type: project | change | incident
opened: YYYY-MM-DD
current_stage: 0
data_classification: [none | personal | health | financial | regulated]
requester: role or name
---

# EXP-0000 — Title

## 0 · Entry
Who is asking, what for, and what type of work this is.

## 1 · Definition
Observed problem, context, constraints. Data classification with its justification.

## 2 · Requirements
Functional acceptance criteria. Non-functional criteria, **with numbers**. Compliance
requirements. The window after which stage 11 can validate. Use cases added or changed, each
validated by product with its date, or "no use cases" with the reason.

## 3 · Refinement
Subtasks. Affected components. Risks, each with an owner. Test plan. Observability plan.

## 4 · Design
Alternatives considered and their consequences. Decision. What was ruled out and why. What
would have to change to revisit it.

## 5 · Development
Proposed changes. Instrumentation added. Tests written.

## 6 · Pre-review
Findings resolved before exposure. Automated flows of the affected use cases, with environment
and result. Verification script published.

## 7 · Change review
Threads and their outcome. Findings published. Decisions going to stage 12.

## 8 · Functional verification
Automated flows run, with who ran them, against what and the result. Result per stage 2
criterion, signed by the verifier.

## 9 · Deployment
Full regression of the product before release. Manual steps executed. Post-deployment check against the non-functional criteria.

## 10 · Operations
Incidents. Root causes. Recovery drill results.

## 11 · Outcome validation
Was the stage 1 problem solved? Solved, half solved and what was missing, or not solved and why.

## 12 · Learning
Rules harvested. Discards with their reason. Pending decisions.
