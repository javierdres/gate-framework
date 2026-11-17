---
seed_id: SEED-BACK-04
kind: lesson
lesson: A service ran broken for weeks because of one empty environment variable. It did not fail at startup; it failed on every cycle and filled the logs with the same error, and nobody noticed.
title: Required configuration is validated at startup, naming the key and never the value
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [configuration]
verification: manual
detected_by: review
---

# SEED-BACK-04 · Required configuration is validated at startup, naming the key and never the value

## Do not

Read configuration where it is used, the first time a request needs it. Give a required value a
silent default. Start with configuration missing. Print a configuration value in an error.

## Do instead

One configuration module reads every variable and validates it at startup, with types, using a
schema library. If something is missing or invalid the service stops, with a message that names
the key and never shows its value.

## Why

A half-configured service looks alive, makes noise and hides the real cause. The platform shows a
service that does not start; it does not show one that fails on every request.

## How it is checked

In review, every required variable is in the startup schema. On deployment, a missing variable
shows as a failed start in the pipeline or the orchestrator.
