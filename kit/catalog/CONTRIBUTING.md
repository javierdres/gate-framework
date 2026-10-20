# Contributing a rule

Rules are harvested by `harvest`, not written from scratch. This is the format they have to
meet; `rules/_TEMPLATE.md` is a starting point that already meets it.

## File naming

```
rules/hard/HR-0001-no-secrets-in-the-repository.md
rules/soft/SR-0001-integrations-report-their-failures.md
```

- `HR-` for a hard rule, in `rules/hard/`. `SR-` for a soft one, in `rules/soft/`.
- Four digits, sequential and independent per prefix. An id is never reused, not even once
  deprecated.
- Slug in lowercase with hyphens.

## Frontmatter

The keys stay in English whatever language the rule is written in; the values and the body go
in the organisation's language.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | `HR-NNNN` or `SR-NNNN` | yes | Matches the filename and the directory |
| `title` | text | yes | Names the rule, does not justify it |
| `severity` | `hard` or `soft` | yes | Matches the directory |
| `status` | `candidate`, `in force` or `deprecated` | yes | |
| `scope` | list | yes, not empty | Each one listed in `scopes.md` |
| `projects` | list | yes, not empty | `cross-cutting`, or specific project ids |
| `tags` | list | yes, may be empty | Free: `injection`, `secrets`, `owasp-a03` |
| `origin` | list | yes, not empty | Where it came from, told as a pattern, with a link when there is one |
| `approved_by` | list | yes | Empty while candidate; not empty when in force |
| `created`, `updated` | `YYYY-MM-DD` | yes | `updated` is not earlier than `created` |
| `supersedes` | list of ids | yes, may be empty | |
| `superseded_by` | id or `null` | yes | Required when deprecated |

Lists are written either `[a, b]` or one `  - item` per line under the key.

## Required sections

`## Do not`, `## Do instead`, `## Why` and `## How it is checked`. A hard rule also needs
`## Exceptions`, even if it only says there are none. `## Evidence` and `## History` are
optional.

## Before opening the change request

```
python3 bin/validate.py && python3 bin/generate_catalog.py
```

Both have to come back clean. One change request per scope, to that scope's custodian.
