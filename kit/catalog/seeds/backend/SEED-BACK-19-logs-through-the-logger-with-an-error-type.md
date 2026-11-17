---
seed_id: SEED-BACK-19
kind: baseline
lesson: Where the logger was injected as a dependency, raw prints fell by about three quarters with no rule at all; services that did not emit an error type were never separated or alerted by the platform that relied on it.
title: Logs go through the service's logger, and error paths log context with an error type
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [logging, observability]
verification: auto-backlog
detected_by: review
---

# SEED-BACK-19 · Logs go through the service's logger, and error paths log context with an error type

## Do not

Log with the language's raw print or console. Log an error with no context.

## Do instead

Every log goes through the service's logger. Every error path logs what operation failed, on
which resource and what the third party answered, with an error type field (runtime, database,
timeout, integration, validation) the platform can separate and alert on.

## Why

Prints bypass levels, formats and redaction. An error without context or type cannot be found or
alerted on.

## How it is checked

A linter rule against raw prints; review for the context and the type.
