---
seed_id: SEED-OPS-02
kind: lesson
lesson: A third-party account was suspended and took about ten services down at once. Nobody knew until users failed.
title: Every external production dependency has an alert and an owner
severity: soft
scope: [operations]
projects: [cross-cutting]
tags: [dependencies, alerting]
verification: manual
detected_by: review
---

# SEED-OPS-02 · Every external production dependency has an alert and an owner

## Do not

Depend in production on an account with a balance, a quota, a proxy, a certificate or a
third-party API without an alert on what makes it fail.

## Do instead

Keep a list of the external dependencies of production. Each one has an alert on its status,
balance, quota, expiry or error rate, and an owner who answers it. A change that adds a
dependency adds its entry.

## Why

An external dependency that fails without warning turns a provider's problem into an outage of
several products at once.

## How it is checked

In the operations review, every entry has its alert and its owner. In review, a new external
dependency comes with its entry.
