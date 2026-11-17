---
seed_id: SEED-SEC-02
kind: lesson
lesson: A review of production logs found credentials, personal identifiers and payment data written in full, in logs read by far more people and systems than the code and kept for months.
title: Logs carry no secrets and no full personal or financial data
severity: hard
scope: [security]
projects: [cross-cutting]
tags: [personal-data, logging, business-defect]
verification: manual
detected_by: review
---

# SEED-SEC-02 · Logs carry no secrets and no full personal or financial data

## Do not

Log a request or response object whole. Log tokens, passwords or keys. Log personal identifiers,
names, addresses, email addresses, phone numbers, or card and account numbers in full. Put them
in a URL or query string, where proxies, CDNs and browsers log them too. Send them to the error
tracking or observability tool.

## Do instead

Log internal identifiers (the request, order or case id) instead of identities. Mask what a
diagnosis needs, such as the last four digits. Apply one redaction filter in the logger, so no
call site has to remember it.

## Why

Logs are read by more people and systems than the code, shipped to third parties and kept for
months. A leak through the logs is one nobody notices, and no tool tells a legitimate log line
from one that exposes someone.

## How it is checked

In review, every log line or error report that prints an input or output object. In production,
a periodic search of the logs for secret and identifier patterns. A starting heuristic:

```bash
grep -rnE "(log|logger|print|console)\.?\w*\(.*(body|payload|request|response|headers)" --include="*.*" .
```

It raises many candidates; each is read, not counted.

## Exceptions

None. This is a hard rule.
