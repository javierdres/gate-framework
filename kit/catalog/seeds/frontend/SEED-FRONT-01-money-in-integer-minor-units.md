---
seed_id: SEED-FRONT-01
kind: baseline
lesson: The front-end standard of the organisation behind these seeds made money arithmetic blocking, because an amount rounded wrong is a business defect no tool detects. Its back-end standard did not adopt the rule, for lack of evidence there: adopt it where money is computed.
title: Money is integer minor units, computed in pure functions, apart from formatting
severity: hard
scope: [frontend]
projects: [cross-cutting]
tags: [money, business-defect]
verification: manual
detected_by: review
---

# SEED-FRONT-01 · Money is integer minor units, computed in pure functions, apart from formatting

## Do not

Accumulate amounts in floating point. Compute amounts inside components. Mix calculation and
formatting.

## Do instead

Represent money in the currency's smallest integer unit. Compute in pure functions, tested with
rounding, zero and negatives. Format in a separate function.

## Why

A rounding error in an amount shown or charged is a defect the user finds, not a tool.

## How it is checked

In review, every arithmetic on amounts goes through the money functions.

## Exceptions

None. This is a hard rule.
