---
seed_id: SEED-BACK-17
kind: baseline
lesson: Dozens of fixes were state transitions spread across the code that contradicted each other.
title: State changes go through a transition table
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [domain]
verification: manual
detected_by: review
---

# SEED-BACK-17 · State changes go through a transition table

## Do not

Assign a business state directly wherever it is needed.

## Do instead

Define the allowed transitions in one table (current state, action, next state, who may) and
change state only through a function that consults it.

## Why

Transitions spread across the code contradict each other, and nobody can say which states are
reachable.

## How it is checked

In review, no direct assignment of a state outside the transition function.
