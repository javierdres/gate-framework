---
seed_id: SEED-FRONT-02
kind: baseline
lesson: Errors reached users as raw status text, untranslated codes, serialised JSON or a bare message that something went wrong, none of which told them what to do.
title: Every error shown to a user is actionable
severity: soft
scope: [frontend]
projects: [cross-cutting]
tags: [errors, ux]
verification: manual
detected_by: review
---

# SEED-FRONT-02 · Every error shown to a user is actionable

## Do not

Show a raw status, a code, serialised data, a message in another language, or a generic error
with nothing else.

## Do instead

Say what happened and what the user can do. Every catch translates and propagates, reports to
observability, or shows such a message.

## Why

An error the user cannot act on becomes a support request.

## How it is checked

In review, every error message.
