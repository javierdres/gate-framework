---
seed_id: SEED-CROSS-11
kind: baseline
lesson: Rules left as warnings and gates switched off accumulated over a hundred violations across years; in one codebase the count of type escapes went from dozens to hundreds with the rule switched off.
title: A gate with debt is frozen, not softened
severity: hard
scope: [cross-cutting]
projects: [cross-cutting]
tags: [ratchet, pipeline]
verification: auto
detected_by: pipeline
---

# SEED-CROSS-11 · A gate with debt is frozen, not softened

## Do not

Lower a threshold, let a job fail, or turn a rule into a warning because existing code breaks it.

## Do instead

Count today's debt and block against that count, so the gate fails only when it rises. The same
ratchet for coverage, linter violations, known dependency advisories and files the formatter
would change.

## Why

A softened gate lets today's debt and tomorrow's through alike, and nobody knows how much there
is.

## How it is checked

The catalog's gate (`ci/`), which counts against the target branch.

## Exceptions

None. This is a hard rule.
