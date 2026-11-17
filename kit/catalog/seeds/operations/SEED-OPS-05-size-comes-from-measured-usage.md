---
seed_id: SEED-OPS-05
kind: lesson
lesson: Functions and services were given memory and compute by guess, several times what they used, and the oversizing was paid every month.
title: Size comes from measured usage
severity: soft
scope: [operations]
projects: [cross-cutting]
tags: [cost]
verification: manual
detected_by: review
---

# SEED-OPS-05 · Size comes from measured usage

## Do not

Choose memory, CPU or instance size without a measurement behind it.

## Do instead

Choose the size from metrics: maximum memory used, CPU percentiles, the platform's own
recommendation. With no data yet, start with the smallest size that runs and review it after
the first real use. The number carries a note saying where it came from.

## Why

Oversizing is paid every month and never shows up as a failure, so nobody revisits it.

## How it is checked

In review, every size has its source next to it.
