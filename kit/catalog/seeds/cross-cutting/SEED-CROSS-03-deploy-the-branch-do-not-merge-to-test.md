---
seed_id: SEED-CROSS-03
kind: baseline
lesson: Over a hundred change requests came in trial-and-error bursts, more than half merged within five minutes of opening; debugging code was merged into the integration branch.
title: To test a change, deploy its branch; do not merge it
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [branching]
verification: manual
detected_by: review
---

# SEED-CROSS-03 · To test a change, deploy its branch; do not merge it

## Do not

Merge into a shared branch to see whether something works.

## Do instead

Deploy the working branch to an environment, or use the ephemeral environment the project
declares.

## Why

Every trial merge deploys, and dirties the history the next person has to read.

## How it is checked

In review, a burst of tiny change requests to the same place is the signal.
