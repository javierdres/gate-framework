---
seed_id: SEED-CROSS-07
kind: baseline
lesson: Of about thirty services measured, three ran their tests in a pipeline and two their linter; the most active one enforced its lint rules only in a local hook anyone could skip.
title: The existing tests and the linter run in the change request's pipeline
severity: hard
scope: [cross-cutting]
projects: [cross-cutting]
tags: [pipeline, tests]
verification: auto
detected_by: pipeline
---

# SEED-CROSS-07 · The existing tests and the linter run in the change request's pipeline

## Do not

Keep tests or lint that only run when someone remembers. Rely on local hooks as the gate.

## Do instead

The pipeline runs the linter and every existing test on each change request. Local hooks are a
convenience; the pipeline is the only real gate.

## Why

A test nobody runs rots, and then misleads.

## How it is checked

The pipeline definition.

## Exceptions

None. This is a hard rule.
