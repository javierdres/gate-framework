---
seed_id: SEED-BACK-22
kind: baseline
lesson: The one rule that held on its own did so because the wrong path stopped existing: once automatic schema synchronisation was switched off, it never came back. A setup document still recommended it, and that is the document an agent copies.
title: The schema changes only through migrations
severity: hard
scope: [backend]
projects: [cross-cutting]
tags: [data]
verification: auto
detected_by: pipeline
applies_when: [data.store != none]
---

# SEED-BACK-22 · The schema changes only through migrations

## Do not

Let the ORM synchronise the schema automatically, in any environment, local included. Change a
schema or reshape existing documents by hand.

## Do instead

Every schema change is a versioned migration, tested up and down against the same engine and
version before the change request. In a document store, reshaping existing documents is a
versioned, idempotent script.

## Why

Automatic synchronisation drops data the day the model and the database disagree.

## How it is checked

The gate counts the synchronisation flag set to true and fails if it appears.

## Exceptions

None. This is a hard rule.
