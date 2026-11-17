---
seed_id: SEED-BACK-20
kind: baseline
lesson: About fifty fixes came from configuration: keys named differently in each environment, resources that did not exist in development, debug values that reached production.
title: Every environment declares the same configuration keys
severity: soft
scope: [backend]
projects: [cross-cutting]
tags: [configuration]
verification: auto-backlog
detected_by: review
---

# SEED-BACK-20 · Every environment declares the same configuration keys

## Do not

Add a variable to one environment only. Default a key to its development value.

## Do instead

Every environment declares the same keys. A key's default, if it has one, is production's. A new
variable enters in the same change to the configuration schema, to the example environment file
(with no real values) and to each environment's configuration. The shape of each secret is
written next to the code that reads it.

## Why

A key missing in one environment fails only there, usually the one nobody tested in.

## How it is checked

A script that compares the keys of every environment's configuration.
