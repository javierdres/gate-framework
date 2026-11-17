---
seed_id: SEED-SEC-03
kind: lesson
lesson: Functions received every variable of their service without using them, and roles kept permissions on secrets the application no longer read.
title: Every variable, secret and permission has a use
severity: soft
scope: [security]
projects: [cross-cutting]
tags: [least-privilege]
verification: manual
detected_by: self-review
---

# SEED-SEC-03 · Every variable, secret and permission has a use

## Do not

Hand a process every variable and secret of the service. Grant a role permissions on resources it
does not use. Leave a variable, secret or permission behind when the code that used it goes.

## Do instead

Each process receives only the variables and secrets it reads, and each role only the
permissions it uses. What stops being used leaves in the same change that left it unused.

## Why

Spare variables and permissions widen what leaks when something fails, and mislead whoever
maintains the service about what it depends on.

## How it is checked

Self-review crosses the variables the infrastructure hands the process with those the code reads
(the language's environment accessor or configuration object), and the role's permissions with
the resources the code touches.
