---
seed_id: SEED-BACK-07
kind: baseline
lesson: Dozens of fixes were a consumer that broke because its producer changed format; a performance optimisation changed the shape of a list response and left the ids empty in the front end.
title: A change another service consumes is coordinated
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [contracts]
verification: manual
detected_by: review
---

# SEED-BACK-07 · A change another service consumes is coordinated

## Do not

Rename or remove a field, change a type, or change the shape of a response, event, message or
table that another service reads, in place.

## Do instead

Publish the change compatibly (new fields optional, nothing renamed or removed) or as a new
version. The change request names the affected consumers and links the change that adapts each.

## Why

The producer's tests pass; the consumer breaks in production.

## How it is checked

In review, any change to a published shape lists its consumers.
