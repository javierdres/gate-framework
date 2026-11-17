---
seed_id: SEED-FRONT-04
kind: baseline
lesson: A detail screen patched a missing field in the backend every time it rendered: impossible to audit, invisible in the user's history, fired on every refetch and from several tabs at once.
title: Opening a read view never writes to the backend
severity: hard
scope: [frontend]
projects: [cross-cutting]
tags: [data, business-defect]
verification: manual
detected_by: review
---

# SEED-FRONT-04 · Opening a read view never writes to the backend

## Do not

Write to the backend from the rendering of a view whose purpose is to read.

## Do instead

Fix missing data in the backend, in a migration, or through an explicit user action.

## Why

A hidden write runs as often as the screen renders, from wherever it is open, and nobody can say who
changed the record.

## How it is checked

In review, no mutation in the render or load path of a read view.

## Exceptions

None. This is a hard rule.
