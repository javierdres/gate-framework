---
seed_id: SEED-BACK-10
kind: baseline
lesson: A provider's error was stored as the text ERROR in the field where the data should go; after a library upgrade, a parser failure ended in an empty string returned as a result.
title: The response of another system is validated before use
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [integrations]
verification: manual
detected_by: review
---

# SEED-BACK-10 · The response of another system is validated before use

## Do not

Use a third party's response without checking its status and shape. Return `null`, an empty
string or `false` when the third party failed.

## Do instead

The common client checks the status and the shape of the response before returning it. If the
third party failed, it raises an error that carries the provider's status.

## Why

A malformed response used as if it were good is stored, and spreads.

## How it is checked

In review, every client method validates before returning.
