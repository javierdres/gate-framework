---
seed_id: SEED-BACK-08
kind: baseline
lesson: A report with no limit exhausted the connection pool of a database with no replica; dozens of other fixes were paginations calculated wrong or queries with no limit.
title: Every list has a cap
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [performance]
verification: manual
detected_by: review
---

# SEED-BACK-08 · Every list has a cap

## Do not

Return a whole collection from an API or a query.

## Do instead

Every query that returns a list uses the service's common pagination, with a maximum page size and
a default filter.

## Why

A list without a cap works until the data grows, and then takes the database down with it.

## How it is checked

In review, every new list endpoint or query has its limit.
