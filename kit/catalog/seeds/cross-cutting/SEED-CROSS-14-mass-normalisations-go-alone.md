---
seed_id: SEED-CROSS-14
kind: baseline
lesson: The front-end standard of the organisation behind these seeds required reformatting, global renames and automated migrations to go alone, and kept the list of dedicated changes its codebase needed in order of payoff, so normalising never hid inside functional work.
title: Mass normalisations go in dedicated change requests
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [review, legacy]
verification: manual
detected_by: review
---

# SEED-CROSS-14 · Mass normalisations go in dedicated change requests

## Do not

Mix a reformat, a global rename or an automated migration with a functional change.

## Do instead

Each goes alone, with no functional change, and can be reviewed by checking the tool that made it.

## Why

A functional change hidden in a thousand mechanical lines is not reviewed.

## How it is checked

In review, a mechanical diff carries nothing else.
