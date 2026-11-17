---
seed_id: SEED-OPS-07
kind: lesson
lesson: Tasks would not start because of file ownership, or were replaced in a loop because the image lacked the tool its health check called, and successful health checks filled the logs; two thirds of the images ran as root, and some built from a floating base tag. None of it showed until the task was dead.
title: Containers run as non-root, from a pinned base, with a health check and structured error logs
severity: soft
scope: [operations]
projects: [cross-cutting]
tags: [containers]
verification: auto
detected_by: pipeline
---

# SEED-OPS-07 · Containers run as non-root, from a pinned base, with a health check and structured error logs

## Do not

Run the image as root. Build from a floating tag such as `latest`. Write outside a declared
writable directory. Log every successful health check. Log errors as free text.

## Do instead

The image declares an unprivileged user, starts from a base pinned to a version (a digest is
better), writes only to a directory that user owns, answers a health endpoint with 200 and
carries whatever the platform uses to call it. Successful health checks are not logged, and
errors are logged as structured records with an error type and a message.

## Why

None of these fail when the image is built. They fail with the task dead, or with logs full of
noise that is also paid for.

## How it is checked

A container linter on every changed image definition, for example:

```bash
hadolint --only DL3002 --only DL3007 Dockerfile
```

plus a check that a `USER` line exists. Review reads the logger configuration.
