---
seed_id: SEED-AI-05
kind: baseline
lesson: The recurring defects of assisted code in review were always the same few: invented APIs and fields, a new client without a timeout, a decorative catch, a date without a timezone, a helper rewritten because the existing one was not found, an optimisation that changed the shape of a response, and leftover debugging.
title: Review looks where generated code usually fails
severity: recommended
scope: [ai-assisted-work]
projects: [cross-cutting]
tags: [agents, review]
verification: manual
detected_by: review
---

# SEED-AI-05 · Review looks where generated code usually fails

## Do not

Review generated code only for style, where it is usually flawless.

## Do instead

Look first at: endpoints, fields, variables or methods that sound right and do not exist; calls
that bypass the common client; catches that log and carry on; dates without a timezone;
duplicated helpers; optimisations that change what consumers receive; leftover prints, test
queries and local origins in configuration.

## Why

These are the defects that look correct, so they are the ones that get through.

## How it is checked

Review, in that order.
