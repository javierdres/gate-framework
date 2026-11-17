---
seed_id: SEED-CROSS-02
kind: baseline
lesson: Fixes merged into production brought unreleased features with them and were reverted the same day; hundreds of change requests were the same fix applied by hand to each branch.
title: A hotfix starts from what runs in production and carries only the fix
severity: hard
scope: [cross-cutting]
projects: [cross-cutting]
tags: [branching, business-defect]
verification: manual
detected_by: review
---

# SEED-CROSS-02 · A hotfix starts from what runs in production and carries only the fix

## Do not

Start a hotfix from the integration branch. Merge into the production branch anything besides the
fix.

## Do instead

Start the hotfix from the branch that runs in production today, as the project profile declares
it. It carries only the fix, and reaches the other branches by cherry-pick, in change requests
linked from the first.

## Why

A hotfix that brings other work releases what nobody approved, at the worst possible moment.

## How it is checked

In review of a change to the production branch: every commit belongs to the fix.

## Exceptions

None. This is a hard rule.
