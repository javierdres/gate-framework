---
seed_id: SEED-BACK-24
kind: baseline
lesson: Several services ran with auto-reload in production because the template they were copied from started that way.
title: Production never runs in development mode
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [runtime]
verification: auto
detected_by: pipeline
---

# SEED-BACK-24 · Production never runs in development mode

## Do not

Start a production process with auto-reload, watch mode, a development server or debug enabled.

## Do instead

The production start command is the production server, with debug off, and the template every
new service is copied from starts that way.

## Why

Development mode is slower, exposes internals and restarts on its own.

## How it is checked

The gate counts reload, watch and debug flags in container definitions and start scripts.

## Exceptions

None. This is a hard rule.
