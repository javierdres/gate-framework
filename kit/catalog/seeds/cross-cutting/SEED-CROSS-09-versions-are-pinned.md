---
seed_id: SEED-CROSS-09
kind: baseline
lesson: A shared infrastructure template was included from its default branch in fifteen repositories, so a change there reached all of them with no version and without anyone deciding it; runtimes varied widely with only a few repositories pinning them, and one language had no lockfiles at all.
title: Runtime, dependencies, shared templates and build images are pinned
severity: soft
scope: [cross-cutting]
projects: [cross-cutting]
tags: [reproducibility, dependencies]
verification: auto
detected_by: pipeline
---

# SEED-CROSS-09 · Runtime, dependencies, shared templates and build images are pinned

## Do not

Install an internal package or include a shared template from a branch. Build from a floating
image tag. Leave the runtime version implicit. Install without a lockfile.

## Do instead

Pin the runtime in one file, commit the lockfile and install from it, pin images and build tools
to a version, and include internal packages and shared templates by tag.

## Why

What is not pinned changes under you without a change request.

## How it is checked

The gate counts references to branches and floating tags.
