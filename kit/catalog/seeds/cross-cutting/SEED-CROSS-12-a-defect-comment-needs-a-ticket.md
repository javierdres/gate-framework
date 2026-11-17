---
seed_id: SEED-CROSS-12
kind: baseline
lesson: Comments warning in capitals that a function had a global side effect sat in the code with no ticket; the risk passed to the next reader and died there.
title: A comment that reports a defect carries a ticket and a date
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [debt]
verification: auto
detected_by: pipeline
---

# SEED-CROSS-12 · A comment that reports a defect carries a ticket and a date

## Do not

Leave a comment that describes a defect, a risk or a limitation with no ticket.

## Do instead

Write it as `TODO(<ticket>, <YYYY-MM>): <what>`, a form a linter can require.

## Why

A warning in a comment moves the risk to the next reader. A ticket makes it visible, prioritised
and dated.

## How it is checked

A linter rule requiring the ticket pattern in warning comments.
