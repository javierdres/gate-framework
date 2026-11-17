---
seed_id: SEED-BACK-26
kind: baseline
lesson: A migration away from a library started and stalled on a branch; without a block, every new piece of code used the old library again.
title: Libraries on their way out are declared forbidden and blocked by the linter
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [dependencies]
verification: auto
detected_by: pipeline
---

# SEED-BACK-26 · Libraries on their way out are declared forbidden and blocked by the linter

## Do not

Leave a library being retired open to new code.

## Do instead

Declare it in `forbidden:` of the project profile with its replacement, and block its import in
new code with the linter.

## Why

A migration nobody enforces is overtaken by the next change.

## How it is checked

The linter's restricted-imports rule, fed from the profile.
