---
seed_id: SEED-OPS-04
kind: lesson
lesson: A dead-letter queue collected failed messages for two weeks with no alarm and no consumer, and the work was lost without anyone noticing. In another service three error paths reached the dead-letter queue without telling anyone, and users saw their payment in progress for ever.
title: Every dead-letter queue has an alarm or a consumer, and an owner
severity: soft
scope: [operations]
projects: [cross-cutting]
tags: [queues, alerting]
verification: manual
detected_by: review
---

# SEED-OPS-04 · Every dead-letter queue has an alarm or a consumer, and an owner

## Do not

Create a dead-letter queue nobody watches. Let a message reach it without the operation it belongs
to finding out.

## Do instead

Every dead-letter queue has an alarm on its visible messages, or a process that consumes it, and
the service's documentation says who receives the alert and how messages are reprocessed. A
message's terminal state (processed with an error, or its last retry) updates the state of the
operation it belongs to and logs with an error type.

## Why

Without an alarm, a dead-letter queue only hides failures: the work is lost and nobody knows.

## How it is checked

In review, every dead-letter queue in the infrastructure has its alarm or its consumer, and every
terminal state of a consumer updates the operation.
