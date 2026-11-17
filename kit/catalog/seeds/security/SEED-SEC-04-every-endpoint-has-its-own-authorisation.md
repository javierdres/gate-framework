---
seed_id: SEED-SEC-04
kind: baseline
lesson: A webhook's key also opened every other endpoint of its service. A server-side proxy route that met every other rule let anyone list other users' requests by changing a number in the URL.
title: Every endpoint has its own authorisation, verified on the server
severity: hard
scope: [security]
projects: [cross-cutting]
tags: [access-control, business-defect]
verification: manual
detected_by: review
waivable: false
---

# SEED-SEC-04 · Every endpoint has its own authorisation, verified on the server

## Do not

Add or touch an endpoint, resolver, handler or proxy route without declaring who may call it.
Let a credential meant for one use open others. Trust an identity, role or account id that comes
in the body or the query string. Treat hiding a button in the interface as authorisation.

## Do instead

Every endpoint declares who may call it and checks it on the server, against the identity of the
session. The interface decides what to show; the server decides what is allowed.

## Why

An access that should not exist is detected by no tool, and is found by whoever exploits it.

## How it is checked

In review, every new or touched endpoint names its authorisation and tests a caller who should
be refused.

## Exceptions

None. This is a hard rule and no exception covers it.
