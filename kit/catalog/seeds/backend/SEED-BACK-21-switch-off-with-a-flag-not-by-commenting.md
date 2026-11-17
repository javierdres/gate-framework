---
seed_id: SEED-BACK-21
kind: baseline
lesson: A hotfix commented out a validation and marked every pending receipt as paid, with no flag and no date to remove it; elsewhere functions were switched off by commenting code, and flags compared against the string false while their peers compared against true.
title: A function is switched off with a flag, never by commenting code
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [flags, business-defect]
verification: manual
detected_by: review
---

# SEED-BACK-21 · A function is switched off with a flag, never by commenting code

## Do not

Switch off a function or skip a business check by commenting it out or returning early.

## Do instead

Use a configuration flag, off by default, with its owner, ticket and removal date written next to
it. Every flag is read through the same helper with the same convention of values. A flag fully
on in every environment for two quarters is removed together with the branch it protected.

## Why

A commented-out check has no owner and never comes back. A flag with no removal date becomes
permanent dead weight.

## How it is checked

In review, no commented-out logic; every flag has its owner and date.

## Exceptions

None. This is a hard rule.
