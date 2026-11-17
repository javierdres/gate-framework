---
seed_id: SEED-BACK-18
kind: baseline
lesson: One stack had three different error formats, so a consumer of two services had to know all three; only one service registered a global handler, and another had one written and never registered.
title: A service has one error format and a global error handler
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [errors]
verification: manual
detected_by: review
---

# SEED-BACK-18 · A service has one error format and a global error handler

## Do not

Build error responses by hand in each handler, each in its own shape.

## Do instead

Each service registers a global error handler that translates exceptions into the service's one
error format, a stable code, a message for the user and the status, and logs them with an error
type.

## Why

Consumers cannot handle errors whose shape they cannot predict.

## How it is checked

In review, a new service registers its handler; a new error path raises rather than builds a
response.
