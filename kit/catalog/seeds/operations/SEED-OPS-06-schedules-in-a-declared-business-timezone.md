---
seed_id: SEED-OPS-06
kind: lesson
lesson: A scheduled job written in UTC ran an hour early or late for half the year, because the business timezone moves with daylight saving and UTC does not.
title: Schedules are written in a declared business timezone
severity: soft
scope: [operations]
projects: [cross-cutting]
tags: [scheduling, time]
verification: manual
detected_by: review
---

# SEED-OPS-06 · Schedules are written in a declared business timezone

## Do not

Write a schedule in UTC with nothing next to it.

## Do instead

Define the schedule with the business timezone when the scheduler supports one. When it does
not, the UTC expression carries next to it the local time it means in summer and in winter.

## Why

An unexplained UTC schedule runs at the wrong local time half the year, and nobody reading it can
tell what was intended.

## How it is checked

In review, every schedule expression carries a timezone or the conversion written out.
