---
seed_id: SEED-BACK-06
kind: baseline
lesson: Fixes added a null-safe operator at the line that crashed; the same null crashed in another function three months later. In one codebase null-safe operators grew from a handful to over a thousand in four years, with strict null checks switched off.
title: A field is declared once as required, optional or nullable
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [types, contracts]
verification: manual
detected_by: review
---

# SEED-BACK-06 · A field is declared once as required, optional or nullable

## Do not

Fix a null by adding a null-safe operator where it blew up. Add a field or a state to the model
and leave out an input, an enum, a mapper or a transformation that carries it.

## Do instead

Each field declares once whether it is required, optional or nullable, and the input schema, the
storage model and the response type derive from that declaration or are reviewed together. The
code decides explicitly what happens without the field: a clear error or a defined business
value. A new field or state reaches every layer that carries it in the same change.

## Why

A null patched where it surfaced moves to the next place that reads it.

## How it is checked

In review, a new null-safe operator in business code asks why the value may be missing.
