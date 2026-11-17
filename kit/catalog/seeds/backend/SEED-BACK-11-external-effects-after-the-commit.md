---
seed_id: SEED-BACK-11
kind: baseline
lesson: A synchronisation with an external registry ran inside the database transaction; when the local transaction rolled back, the other system kept the change and the two disagreed.
title: What affects another system goes after the commit
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [integrations, transactions, business-defect]
verification: manual
detected_by: review
---

# SEED-BACK-11 · What affects another system goes after the commit

## Do not

Call another system to change something (sync, notify, enqueue, submit) inside a database
transaction.

## Do instead

Make the call after the commit, outside the transaction. If it fails, record it and retry
separately (a queue, a job or a table of pending work), without rolling back or blocking the
main operation.

## Why

An external effect done while the local transaction rolls back leaves two systems in
disagreement, and no tool sees it.

## How it is checked

In review, no external call inside a transaction block.

## Exceptions

None. This is a hard rule.
