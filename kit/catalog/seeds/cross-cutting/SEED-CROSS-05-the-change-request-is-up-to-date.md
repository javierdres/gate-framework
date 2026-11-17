---
seed_id: SEED-CROSS-05
kind: baseline
lesson: Changes reached review behind their target branch, so what was reviewed was not what would merge; the organisation made the divergence check, read from the code platform, the first step of every review.
title: The change request is up to date with its target
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [review]
verification: auto
detected_by: review
---

# SEED-CROSS-05 · The change request is up to date with its target

## Do not

Ask for review with conflicts, or with commits of the target branch missing.

## Do instead

Rebase or merge the target first, then ask for review.

## Why

A review of a stale branch approves code that will not exist after the merge.

## How it is checked

The code platform's API reports diverged commits; review reads it before anything else.
