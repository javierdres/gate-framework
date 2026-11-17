# Contributing a rule

Rules are harvested by `harvest`, or adopted from a GATE seed by `bin/adopt_seed.py`, not
written from scratch. This is the format they have to meet; `rules/_TEMPLATE.md` is a starting
point that already meets it.

## File naming

In the layout by severity:

```
rules/hard/HR-0001-no-secrets-in-the-repository.md
rules/soft/SR-0001-integrations-report-their-failures.md
rules/recommended/RC-0001-one-client-per-external-system.md
```

- `HR-` for a hard rule, in `rules/hard/`. `SR-` for a soft one, in `rules/soft/`. `RC-` for a
  recommended one, in `rules/recommended/`.

In the layout by scope (see `scopes.md`):

```
rules/security/SEC-0001-no-secrets-in-the-repository.md
rules/groups/<group>/<PREFIX>-0001-....md
```

- The prefix is the one `scopes.md` declares for the folder's scope or group, and the folder's
  key is listed in the rule's `scope`.

In both:

- Four digits, sequential and independent per prefix. An id is never reused, not even once
  deprecated or repealed.
- Slug in lowercase with hyphens.

## Frontmatter

The keys stay in English whatever language the rule is written in; the values and the body go
in the organisation's language.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | `PREFIX-NNNN` | yes | Matches the filename and the folder |
| `title` | text | yes | Names the rule, does not justify it |
| `severity` | `hard`, `soft` or `recommended` | yes | Matches the directory in the layout by severity |
| `status` | `candidate`, `in force` or `deprecated` | yes | |
| `scope` | list | yes, not empty | Each one listed in `scopes.md` |
| `projects` | list | yes, not empty | `cross-cutting`, or specific project ids |
| `tags` | list | yes, may be empty | Free: `injection`, `secrets`, `owasp-a03`. `business-defect` has a meaning: see below |
| `origin` | list | yes, not empty | Where it came from, told as a pattern, with a link when there is one |
| `approved_by` | list | yes | Empty while candidate; not empty when in force |
| `created`, `updated` | `YYYY-MM-DD` | yes | `updated` is not earlier than `created` |
| `supersedes` | list of ids | yes, may be empty | Each one exists and points back with `superseded_by` |
| `superseded_by` | id, `repealed` or `null` | yes | Required when deprecated. `repealed` needs a row in `calibration/not-adopted.md` |
| `verification` | `auto`, `auto-backlog` or `manual` | no | Recommended. A tool checks it, a tool is queued, or a person does |
| `detected_by` | `pipeline`, `self-review` or `review` | no | Recommended. `pipeline` needs `verification: auto` |
| `applies_when` | list of conditions | no | `key = value`, `key != value`, `key ~ value`, read from the project profile |
| `waivable` | `true` or `false` | no | `false` when no exception may cover it. Default `true` |
| `seeded_from` | seed id | no | Written by `adopt_seed.py`; never edit it |

Lists are written either `[a, b]` or one `  - item` per line under the key.

A hard rule whose `verification` is `manual` carries the `business-defect` tag: it blocks only
because breaking it causes a business defect no tool detects. Without that, automate its check
or make it soft.

## Required sections

`## Do not`, `## Do instead`, `## Why` and `## How it is checked`. A hard rule also needs
`## Exceptions`, even if it only says there are none. `## Evidence` and `## History` are
optional.

A rule may cite another by its id. The validator checks that every id cited exists in the
catalog, so a citation never points at nothing.

## Before opening the change request

```
python3 bin/validate.py && python3 bin/generate_catalog.py
```

Both have to come back clean. One change request per scope, to that scope's custodian.
