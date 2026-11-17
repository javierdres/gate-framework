---
seed_id: SEED-BACK-09
kind: baseline
lesson: It was the cause with the most fixes in the backend, and the only one that never improved on its own: about one call in eight set a timeout, a timeout added in one change was commented out a month later, and size limits were raised to infinity.
title: Every call to another system has a timeout
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [integrations, resilience]
verification: auto-backlog
detected_by: review
---

# SEED-BACK-09 · Every call to another system has a timeout

## Do not

Call another system over HTTP, SOAP or a vendor SDK without an explicit timeout and a limit on the
size of the response. Comment out a timeout to make something pass.

## Do instead

Set a timeout fitting what is expected of that system, and a response size limit, in the one
client each external system goes through, not call by call. A timeout changes through
configuration.

## Why

A service that waits for ever on a third party that is down takes all its workers and goes down
with it.

## How it is checked

Until a tool enforces it, review: every new call goes through the common client. Tools that can:
a linter rule forbidding direct imports of the HTTP library outside the client, or a rule that
flags requests without a timeout.

## Exceptions

A call known to take minutes gets a long timeout, not none, recorded as an exception with its
reason.
