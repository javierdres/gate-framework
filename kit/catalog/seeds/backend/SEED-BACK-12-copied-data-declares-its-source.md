---
seed_id: SEED-BACK-12
kind: baseline
lesson: Dozens of fixes were copies of another system's data that drifted and were never resynchronised.
title: Data copied from another system declares its source of truth
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [integrations, data]
verification: manual
detected_by: review
---

# SEED-BACK-12 · Data copied from another system declares its source of truth

## Do not

Copy data from another system without a way to know where it came from or when.

## Do instead

Every copy keeps the external identifier and the date of the copy, and has an explicit path to
resynchronise it when the source changes.

## Why

A copy with no source and no date cannot be repaired when it drifts.

## How it is checked

In review, a new copied field brings its external id, its date and its resync path.
