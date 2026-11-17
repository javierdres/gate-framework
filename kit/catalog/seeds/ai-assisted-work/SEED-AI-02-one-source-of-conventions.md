---
seed_id: SEED-AI-02
kind: baseline
lesson: Two convention files in one repository contradicted each other, one recommending a command the other forbade, and assistant-specific steering files described a stack different from the one in the repository.
title: One source of conventions per repository
severity: soft
scope: [ai-assisted-work]
projects: [cross-cutting]
tags: [agents, documentation]
verification: manual
detected_by: review
---

# SEED-AI-02 · One source of conventions per repository

## Do not

Repeat conventions across the README, onboarding notes, contribution guides and each assistant's
own files.

## Do instead

One canonical file holds the conventions and the profile. Every other file links to it.

## Why

Two sources end up saying different things, and the agent obeys the one it read last.

## How it is checked

In review, a convention written outside the canonical file.
