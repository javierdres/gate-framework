---
seed_id: SEED-SEC-05
kind: baseline
lesson: Disabled certificate verification turned up in both groups of services, behind half a dozen fixes, and was removed one service at a time.
title: Certificate verification is never disabled
severity: hard
scope: [security]
projects: [cross-cutting]
tags: [tls]
verification: auto
detected_by: pipeline
waivable: false
---

# SEED-SEC-05 · Certificate verification is never disabled

## Do not

Disable TLS verification for a database or a third party anywhere but a developer's machine.

## Do instead

Fix a certificate error in the image's chain of trust, or with the provider's bundle.

## Why

A connection that is not verified can be read and altered by anyone on the path.

## How it is checked

The gate counts the verification-off switches of each language and fails if they rise.

## Exceptions

None. This is a hard rule and no exception covers it.
