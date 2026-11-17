---
seed_id: SEED-BACK-13
kind: baseline
lesson: Dozens of fixes came from fan-outs with no limit over whole lists, a pattern that grew from zero to dozens of uses in two codebases, and from asynchronous loops that awaited nothing.
title: A bulk process works in bounded batches with limited concurrency
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [performance, concurrency]
verification: manual
detected_by: review
---

# SEED-BACK-13 · A bulk process works in bounded batches with limited concurrency

## Do not

Run every item of a list at once with no concurrency limit. Use a loop construct that fires
asynchronous work without awaiting it.

## Do instead

Process lists in batches of bounded size, with a concurrency limiter.

## Why

Unbounded fan-out works with ten items and exhausts connections, memory or a third party's rate
limit with ten thousand.

## How it is checked

Review, helped by the gate counting the unbounded patterns of each language.
