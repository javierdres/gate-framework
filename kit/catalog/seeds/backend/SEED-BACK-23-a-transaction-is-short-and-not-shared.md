---
seed_id: SEED-BACK-23
kind: baseline
lesson: Five change requests in three days moved from one transaction per row in parallel, to one transaction shared by parallel work, to no transaction at all; data was lost halfway in between.
title: A transaction is neither shared nor waits on another system
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [data, transactions, business-defect]
verification: manual
detected_by: review
applies_when: [data.store != none]
---

# SEED-BACK-23 · A transaction is neither shared nor waits on another system

## Do not

Share one transaction among operations running in parallel. Call another system inside a
transaction.

## Do instead

A transaction is short: it reads, decides, writes and ends.

## Why

Half-written data is not detected by any tool, and is found by a user.

## How it is checked

In review, no parallel work over one transaction handle, and no external call inside one.

## Exceptions

None. This is a hard rule.
