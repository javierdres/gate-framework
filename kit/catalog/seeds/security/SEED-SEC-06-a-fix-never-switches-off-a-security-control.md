---
seed_id: SEED-SEC-06
kind: baseline
lesson: A change titled as a CSRF fix switched CSRF protection off, and it stayed off in production, where the CORS configuration also accepted local and test origins with credentials.
title: A fix never switches off a security control
severity: hard
scope: [security]
projects: [cross-cutting]
tags: [controls, business-defect]
verification: manual
detected_by: review
waivable: false
---

# SEED-SEC-06 · A fix never switches off a security control

## Do not

Disable or relax CSRF, CORS, CSP, rate limits, input validation or authentication to make
something work. Leave local or test origins in production configuration.

## Do instead

Fix the cause. If a control really has to change, the custodian of security authorises it in
writing, with a closing date.

## Why

A control switched off to fix something else is never switched back on.

## How it is checked

The gate counts the known switches; review reads every change to security configuration.

## Exceptions

None. This is a hard rule and no exception covers it.
