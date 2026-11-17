---
seed_id: SEED-CROSS-13
kind: baseline
lesson: A standard that turns every small change into a large refactor is abandoned within a month; an agent that reports two hundred old findings on a three-line change trains the team to ignore the whole report.
title: Pre-existing debt never blocks a change request
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [review, legacy]
verification: manual
detected_by: review
---

# SEED-CROSS-13 · Pre-existing debt never blocks a change request

## Do not

Report, or block on, problems in lines the author did not touch.

## Do instead

Review what the change introduced. Serious debt found along the way goes separately, as a
proposed ticket.

## Why

Gradual adoption is the only way a standard survives contact with an existing codebase.

## How it is checked

In review, every finding points at a line the change added or modified.
