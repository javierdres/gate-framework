---
seed_id: SEED-BACK-03
kind: lesson
lesson: Jobs that were re-queued automatically ran twice and bought the same item more than once; elsewhere receipts were marked as paid without being paid. The most expensive fixes in the history of the organisation that learned this were all here, and no tool caught any of them.
title: Anything that charges or buys is idempotent and re-reads state before acting
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [payments, idempotency, business-defect]
verification: manual
detected_by: review
---

# SEED-BACK-03 · Anything that charges or buys is idempotent and re-reads state before acting

## Do not

Charge, pay or buy based on state read earlier in the flow. Do it without an idempotency key.
Write a queue consumer or callback handler that assumes each message arrives once. Claim work
among several instances by reading first and marking afterwards.

## Do instead

Re-read the state of the resource right before acting. Use an idempotency key of its own (the
id of the order, the payment or the purchase) that the provider or a unique constraint enforces.
Claim work atomically, in one statement that changes the state only if it is still pending and
returns what it claimed. Change the state and its counters in the same transaction.

## Why

This is where a mistake costs money directly. Queues deliver at least once, and retries,
replicas and re-queues will run any step twice some day.

## How it is checked

In review, every path that charges, pays or buys: the key, the re-read and the atomic claim. A test
that processing the same message twice leaves the same state as processing it once.

## Exceptions

None. This is a hard rule.
