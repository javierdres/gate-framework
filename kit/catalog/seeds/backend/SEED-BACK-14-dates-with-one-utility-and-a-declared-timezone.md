---
seed_id: SEED-BACK-14
kind: baseline
lesson: Shifted dates were behind about ninety fixes across three groups of services, and the pattern kept growing: date construction without a timezone everywhere, no timezone declared in any container, two date libraries in one codebase.
title: Dates are handled with one utility and a declared timezone
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [time, business-defect]
verification: auto-backlog
detected_by: review
---

# SEED-BACK-14 · Dates are handled with one utility and a declared timezone

## Do not

Build, parse or format a date that depends on the day without a timezone. Rely on the server's or
container's timezone.

## Do instead

Parse, calculate and format dates with one utility of the service, with the business timezone
declared in every operation that depends on the day (a "today" filter, a schedule, a printed
date). The container may declare the timezone too, but the code does not depend on it. In
transport and storage, dates are UTC or carry their offset.

## Why

A date shifted by a day is a business defect: a deadline, a contract, a payment on the wrong day.

## How it is checked

Linters that flag naive datetimes cover part of it in some languages. Review covers the rest.

## Exceptions

None. This is a hard rule.
