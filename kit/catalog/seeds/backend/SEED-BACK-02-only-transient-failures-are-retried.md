---
seed_id: SEED-BACK-02
kind: lesson
lesson: A purchasing service retried a legitimate rejection from an external system in a loop; it clogged its queue, held up every other order and ended up buying the same thing twice. Elsewhere a retry option was misspelled, so the queue never retried anything and nothing said so.
title: Only transient failures are retried, with a cap and backoff
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [integrations, retries, business-defect]
verification: manual
detected_by: review
---

# SEED-BACK-02 · Only transient failures are retried, with a cap and backoff

## Do not

Retry a business rejection: a 4xx, "not applicable", "already exists", "insufficient funds".
Retry with no cap, or immediately in a loop. Trust a retry setting nobody has seen work.

## Do instead

Retry only transient failures (timeout, network error, 502, 503, 504), with a cap and a growing
wait with jitter. A business rejection is recorded and reported to whoever started the
operation. The retry configuration is verified by a test or observed in an environment, because
a misspelled option raises no error.

## Why

Retrying a rejection does not change the answer. It spends money, clogs the queue for everyone
else, and can duplicate a charge or a purchase.

## How it is checked

In review, every retry: does it tell a transient failure from a rejection, does it have a cap and
a backoff. A test that a rejection is not retried.

## Exceptions

None. This is a hard rule.
