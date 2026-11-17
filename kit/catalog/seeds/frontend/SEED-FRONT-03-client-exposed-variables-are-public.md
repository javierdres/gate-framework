---
seed_id: SEED-FRONT-03
kind: baseline
lesson: Any variable with the framework's public prefix is compiled into the bundle the browser downloads; keys placed there were visible to anyone who opened the developer tools.
title: Variables exposed to the client are public
severity: hard
scope: [frontend]
projects: [cross-cutting]
tags: [secrets]
verification: auto
detected_by: pipeline
waivable: false
---

# SEED-FRONT-03 · Variables exposed to the client are public

## Do not

Put a key, token, secret, credential or connection string in a variable the build exposes to the
browser, for any service or environment.

## Do instead

Call the service from a server route that holds the key, and expose only what is public by
nature.

## Why

Everything in the bundle is published.

## How it is checked

A linter rule that rejects public-prefixed variables whose names contain KEY, SECRET, TOKEN,
PASSWORD or CREDENTIAL, plus the secret scanner.

## Exceptions

None. This is a hard rule and no exception covers it.
