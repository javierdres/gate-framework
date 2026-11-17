---
seed_id: SEED-BACK-05
kind: baseline
lesson: It was the most requested topic in reviews across three stacks and the cause of dozens of fixes: spreadsheets loaded without normalising them, and new fields the API accepted and silently dropped.
title: Input is validated and normalised once, at the edge
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [validation]
verification: manual
detected_by: review
---

# SEED-BACK-05 · Input is validated and normalised once, at the edge

## Do not

Let data from an API, a file, a spreadsheet or a queue message travel inward unchecked. Treat a
blank string as a value. Ignore fields the schema does not know.

## Do instead

Validate and normalise every input once, where it enters, with a schema. Empty and whitespace-only
count as missing, and unknown fields are rejected. From there inward, the shape of the data is
guaranteed. The response of another system has its own rule.

## Why

Unvalidated input fails far from where it entered, and each layer adds its own partial check.

## How it is checked

In review, every new entry point has its schema, with unknown fields rejected.
