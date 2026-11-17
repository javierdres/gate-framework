---
seed_id: SEED-BACK-25
kind: baseline
lesson: Over a dozen fixes were a framework or a library upgrade that broke at startup; one upgrade of a parsing library was followed the next day by a fix that returned an empty string.
title: A major version upgrade goes in its own change request
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [dependencies]
verification: manual
detected_by: review
---

# SEED-BACK-25 · A major version upgrade goes in its own change request

## Do not

Mix a major upgrade of a dependency, the framework or the runtime with functional changes.

## Do instead

The upgrade goes in a change request with no features, and the flow that uses it is tested in a
deployed environment before merging.

## Why

When an upgrade and a feature break together, nobody can tell which did it.

## How it is checked

In review, a major version bump arrives alone.
