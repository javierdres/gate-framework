---
seed_id: SEED-CROSS-10
kind: baseline
lesson: Testing was a new practice; minimum coverage targets per architectural layer turned out to be something no tool measures, and aspirational thresholds were switched off within a week. A threshold set at the current coverage turned the growing habit into a gate without stopping anyone.
title: Test coverage has a baseline that only goes up
severity: hard
scope: [cross-cutting]
projects: [cross-cutting]
tags: [tests, ratchet]
verification: auto
detected_by: pipeline
---

# SEED-CROSS-10 · Test coverage has a baseline that only goes up

## Do not

Set the threshold at an aspiration and switch it off. Lower it. Let a test job pass with zero
tests.

## Do instead

Set the threshold at the project's current coverage, in the test runner and the pipeline, and
raise it as coverage rises. Targets per kind of code are a direction, not the gate.

## Why

A green test job with no tests reports the opposite of the truth. A threshold that only goes up
turns momentum into a gate.

## How it is checked

The runner's threshold and the pipeline. A project with no tests has a baseline of zero, and its
first goal is that it rises.

## Exceptions

None. This is a hard rule.
