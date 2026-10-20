# Standards catalog

The organisation's rules, in Markdown, written to be read by people and checked mechanically by
the review skills. Built with [GATE](https://github.com/javierdres/gate-framework).

## It starts empty on purpose

A rule set written in one sitting, before there are real cases, describes whoever copied it,
not the organisation. Here every rule shows which discussion or incident it came from: the
`origin` field is required and validated.

The catalog fills up through use, from the decisions in reviews and the root causes of
incidents, through `harvest`. Until it does, review leans on the industry baseline and on each
project's own conventions.

## Two severities, any scope

| Severity | Directory | What belongs there | How review reports it |
|---|---|---|---|
| Hard rule | `rules/hard/` | What must never happen: secrets, injection, access control, data exposure | Blocking |
| Soft rule | `rules/soft/` | How we prefer to build: design, readability, conventions | Suggestion |

Every rule also declares its scope, from the list in [`scopes.md`](scopes.md). A rule in
`candidate` status never blocks, whatever its severity.

## How a rule gets in

It is harvested, not written. `harvest` proposes candidates traceable to a real decision, one
change request per scope to its custodian. Promoting a candidate to `in force` is a human
decision. See [GOVERNANCE.md](GOVERNANCE.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Checks

```
python3 bin/validate.py            # names, ids, fields, values and sections
python3 bin/generate_catalog.py    # builds catalog.json for the review skills
python3 tests/test_catalog.py      # the validator and the generator, in both directions
```

`catalog.json` is generated on each machine and ignored by version control, so two change
requests to the catalog never conflict on it.
