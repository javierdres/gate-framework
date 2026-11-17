---
seed_id: SEED-SEC-01
kind: lesson
lesson: A security audit found keys and credentials committed in more than one repository, and in one of them baked into a container image layer, readable by anyone who could pull the image.
title: No credential in code, versioned configuration or history
severity: hard
scope: [security]
projects: [cross-cutting]
tags: [secrets]
verification: auto
detected_by: pipeline
waivable: false
---

# SEED-SEC-01 · No credential in code, versioned configuration or history

## Do not

Write a credential, token, key, password, connection string with a password or private
certificate in code, in versioned configuration, in pipeline definitions, in comments or
examples, or in an image layer (an environment variable or build argument set at build time).
Treat a committed secret as fixed because the latest commit no longer has it.

## Do instead

Read secrets at runtime, from the environment's secret manager or from variables the platform
injects. Environment files are in the ignore list, the real one included and not only the local
one. A change that takes a secret out of the code also rotates it, and the rotation is recorded
with its owner: the old value is still in the history.

## Why

Whoever can read the repository, today or in a year, has the credential. Version control does
not forget, and images travel further than the code they were built from.

## How it is checked

A secret scanner in the pipeline on every change request, and in pre-review. For example, only
on the commits of the change:

```bash
gitleaks detect --log-opts="origin/main..HEAD"
```

Also look for build-time environment variables or arguments whose names contain `KEY`,
`SECRET`, `TOKEN` or `PASSWORD`. Fixtures with obviously fake values are allowlisted by name in
the scanner's configuration, so the allowlist shows them.

## Exceptions

None. This is a hard rule and no exception covers it.
