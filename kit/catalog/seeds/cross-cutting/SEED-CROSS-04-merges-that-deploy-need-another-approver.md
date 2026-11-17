---
seed_id: SEED-CROSS-04
kind: baseline
lesson: No repository required a green pipeline to merge, and about half the changes were merged by their own author.
title: What deploys on merge is approved by someone else, with a green pipeline
severity: hard
scope: [cross-cutting]
projects: [cross-cutting]
tags: [review, branching]
verification: auto
detected_by: pipeline
---

# SEED-CROSS-04 · What deploys on merge is approved by someone else, with a green pipeline

## Do not

Merge into a branch that deploys to a shared environment without another person's approval or
with a failed pipeline. Keep an approval given before the last push.

## Do instead

The code platform requires an approval from someone other than the author and a passing pipeline,
and a push clears the approval.

## Why

It is the difference between a standard that is reviewed and one that is only read.

## How it is checked

The platform's merge settings, audited by a script over the projects.

## Exceptions

None. This is a hard rule.
