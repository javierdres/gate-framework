---
seed_id: SEED-CROSS-06
kind: baseline
lesson: Migrations that were never run, consumers broken by a changed format and variables missing in one environment were each behind dozens of fixes; the description is where each of them gets named before the merge.
title: The change request says what, why and how it was tested
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [review]
verification: manual
detected_by: review
---

# SEED-CROSS-06 · The change request says what, why and how it was tested

## Do not

Open a change request with an empty or one-line description.

## Do instead

The title carries the ticket. The description says what changes, why, how it was tested, and
lists migrations, affected consumers, new variables and any exception taken.

## Why

A reviewer who has to guess the intent reviews the code against the wrong question.

## How it is checked

A description template, and review.
