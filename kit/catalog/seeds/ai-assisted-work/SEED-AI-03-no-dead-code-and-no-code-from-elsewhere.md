---
seed_id: SEED-AI-03
kind: baseline
lesson: An agent cannot tell live code from orphaned code and reads both with the same weight; one codebase held hundreds of lines of commented-out code, another a committed virtual environment, and copied services kept the name of the one they were copied from.
title: The repository holds no dead code and no code from other products
severity: soft
scope: [ai-assisted-work]
projects: [cross-cutting]
tags: [agents, dead-code]
verification: manual
detected_by: review
---

# SEED-AI-03 · The repository holds no dead code and no code from other products

## Do not

Comment code out "just in case". Keep abandoned modules, generated artefacts or leftovers from
the template a repository was copied from.

## Do instead

Delete it. Version control keeps the history; the repository is the present.

## Why

Everything in the repository is context for the next change an agent makes.

## How it is checked

Linters for unused code cover part of it; review covers the rest.
