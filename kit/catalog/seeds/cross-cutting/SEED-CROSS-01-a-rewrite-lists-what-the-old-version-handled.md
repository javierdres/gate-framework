---
seed_id: SEED-CROSS-01
kind: lesson
lesson: A rewritten integration lost the handling of an odd response the old version recognised; the same failure reached users and had to be fixed again years later.
title: A rewrite lists the cases the previous version handled
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [rewrites]
verification: manual
detected_by: review
---

# SEED-CROSS-01 · A rewrite lists the cases the previous version handled

## Do not

Replace a service, a bot or a module with a new version on the strength of its main flow alone.

## Do instead

The change request that replaces it lists the special cases the previous version handled, taken
from its code, its fixes and its incidents, and says how the new one covers each, or why it no
longer applies.

## Why

The special cases of an old system are the lessons nobody wrote down. A rewrite that does not read
them learns them again, in production.

## How it is checked

In review, the list exists and each item points at code or a test in the new version.
