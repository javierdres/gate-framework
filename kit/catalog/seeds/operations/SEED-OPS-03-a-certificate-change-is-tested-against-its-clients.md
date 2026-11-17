---
seed_id: SEED-OPS-03
kind: lesson
lesson: A certificate was replaced with one from a different issuer; an old internal client that did not trust the new chain started failing tens of thousands of times a day, and nobody knew until users failed.
title: A certificate change is tested against existing clients first
severity: soft
scope: [operations]
projects: [cross-cutting]
tags: [certificates]
verification: manual
detected_by: review
---

# SEED-OPS-03 · A certificate change is tested against existing clients first

## Do not

Change a certificate's issuer, chain or key type in production without knowing who connects to
it.

## Do instead

List the clients that connect, internal legacy processes and partners included. Test the new
certificate against each of them outside production or behind a canary, plan the rollback and
announce the date.

## Why

A client that stops trusting the chain fails in a way that looks like an outage of the client,
not of the certificate, and the cause takes days to find.

## How it is checked

In the review of the change, the list of clients and the result of the test against each.
