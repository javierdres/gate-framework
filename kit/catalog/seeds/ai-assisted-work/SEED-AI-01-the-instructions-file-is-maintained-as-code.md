---
seed_id: SEED-AI-01
kind: baseline
lesson: Application documentation written once drifted from the code in almost every case reviewed: a README pointing to a command that did not exist, an onboarding guide pointing to an instructions file that did not exist. An agent obeys stale documentation with confidence.
title: The repository's instructions file is current and maintained as code
severity: soft
scope: [ai-assisted-work]
projects: [cross-cutting]
tags: [agents, documentation]
verification: manual
detected_by: review
---

# SEED-AI-01 · The repository's instructions file is current and maintained as code

## Do not

Leave the assistant's instructions file, or the README, describing how things were.

## Do instead

Every repository has an instructions file with its project profile, the commands to install,
run, lint, test, migrate and start, and the rules of the repository that are not obvious. When a
pattern changes, the file changes in the same change request.

## Why

People skim stale documentation; agents follow it.

## How it is checked

In review, a change to a pattern or a command touches the instructions file too.
