---
seed_id: SEED-AI-04
kind: baseline
lesson: Generated code is plausible: when what the assistant sees is wrong, it reproduces the error in excellent style.
title: A person reads the whole diff before the change request
severity: soft
scope: [ai-assisted-work]
projects: [cross-cutting]
tags: [agents, review]
verification: manual
detected_by: review
---

# SEED-AI-04 · A person reads the whole diff before the change request

## Do not

Open a change request on code nobody has read. Let the assistant approve its own code.

## Do instead

Before the change request, lint and tests pass and the author reads the whole diff. If the
author cannot explain a line, that line does not merge.

## Why

Review by someone else checks a change; it does not replace its author knowing what it does.

## How it is checked

Self-review, and the reviewer's questions.
