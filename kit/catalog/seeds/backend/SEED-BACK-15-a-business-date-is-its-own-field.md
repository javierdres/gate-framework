---
seed_id: SEED-BACK-15
kind: baseline
lesson: A contract's printed date came from the record's last-updated timestamp, formatted in the server's timezone: generated in the evening it carried the next day's date, and any later edit of the record moved it.
title: A legal or business date is a field of its own
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [time, business-defect]
verification: manual
detected_by: review
---

# SEED-BACK-15 · A legal or business date is a field of its own

## Do not

Take a date with legal or business effect from a creation or update timestamp.

## Do instead

Store the date of the contract, the signature, the payment or the registration as a field of its
own, at the moment the fact happens.

## Why

Technical timestamps change for technical reasons. A legal date that moves is a defect no tool
detects.

## How it is checked

In review, every document or record with a legal date reads it from its own field.

## Exceptions

None. This is a hard rule.
