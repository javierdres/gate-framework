---
seed_id: SEED-BACK-27
kind: baseline
lesson: Packages sat installed and unused for years, while a monitoring library was configured in the code and missing from the dependencies.
title: A dependency is declared if used, and used if declared
severity: recommended
scope: [backend]
projects: [cross-cutting]
tags: [dependencies]
verification: manual
detected_by: review
---

# SEED-BACK-27 · A dependency is declared if used, and used if declared

## Do not

Keep unused dependencies, or rely on one that is not declared.

## Do instead

The dependency list matches what the code imports.

## Why

Unused dependencies add attack surface and upgrade work; undeclared ones break on a clean install.

## How it is checked

A dependency checker for the language, run now and then or in the pipeline.
