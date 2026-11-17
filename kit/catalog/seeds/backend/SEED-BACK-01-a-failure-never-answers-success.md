---
seed_id: SEED-BACK-01
kind: lesson
lesson: Several integration services answered success with an empty body, or with the error inside a successful response; callers took it as success and the failure surfaced days later, through user complaints. In another case a hotfix turned a failed check into success and marked every pending payment as paid.
title: A failure never answers success, and no catch swallows it
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [errors, business-defect]
verification: manual
detected_by: review
---

# SEED-BACK-01 · A failure never answers success, and no catch swallows it

## Do not

Answer a success status with the error in the body (`{"status": "error"}`, an error code inside
a 200, `ok: false` in a successful result). Write a catch that logs and carries on as if nothing
happened, or that returns `false`, an empty string, `null`, an empty list or an "error object"
as if it were a result. Store the error text in the field where the data should go.

## Do instead

An operation that failed answers with an error status: 4xx when the caller is at fault, 5xx or
502 when another system is. Every catch does one of three things: handles the case with an
explicit business decision, adds context and rethrows, or translates into a domain error. Each
service has one global error handler and one error format.

## Why

The caller decides with the status. A failure dressed as success triggers no alert and no retry,
and reaches production as bad data that no tool can tell from a legitimate case.

## How it is checked

Linters cover part of it: rules against empty catch blocks, bare or blind excepts and
try-except-pass. Review checks that every error path of a handler ends in an error status. In
production, an alert on successful responses with an empty body.

## Exceptions

A catch that implements an explicit business decision, such as an optional enrichment that
may be missing, is handling, not swallowing. It says so in a comment and logs at the right
level.
