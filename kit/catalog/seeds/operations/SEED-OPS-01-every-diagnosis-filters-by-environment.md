---
seed_id: SEED-OPS-01
kind: lesson
lesson: Production diagnoses mixed environments because services had the same names in all of them; the figures looked like production's and were not, and decisions were taken on a problem that did not exist.
title: Every diagnostic query filters by environment
severity: soft
scope: [operations]
projects: [cross-cutting]
tags: [observability]
verification: manual
detected_by: review
---

# SEED-OPS-01 · Every diagnostic query filters by environment

## Do not

Query logs or metrics by service, container or pod name alone.

## Do instead

Every query filters by the environment: the log group, account, cluster or whatever separates
them in the tool. The diagnosis shows the filter, and the guides' example queries carry it.

## Why

A diagnosis over mixed environments leads to decisions about a problem that does not exist, or
hides the one that does.

## How it is checked

In the review of a diagnosis or a postmortem, the queries show the environment filter.
