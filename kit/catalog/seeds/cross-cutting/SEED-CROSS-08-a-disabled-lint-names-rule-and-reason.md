---
seed_id: SEED-CROSS-08
kind: baseline
lesson: Dozens of unexplained disable directives turned up in one codebase, most of them added to get past the gate the day it was switched on.
title: Every directive that disables the linter names its rule and its reason
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [lint]
verification: auto
detected_by: pipeline
---

# SEED-CROSS-08 · Every directive that disables the linter names its rule and its reason

## Do not

Disable the linter for a file, or for a line without naming the rule and the reason.

## Do instead

Disable only by line, naming the rule, with the reason on the same line.

## Why

An unexplained directive is indistinguishable from a shortcut, and an agent copies it.

## How it is checked

The linter's own rule that requires a description on disable directives.
