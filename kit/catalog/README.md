# Standards catalog

The organisation's rules, in Markdown, written to be read by people and checked mechanically by
the review skills. Built with [GATE](https://github.com/javierdres/gate-framework).

## It starts empty on purpose, or with the seeds the orchestrator chose

A rule set written in one sitting, before there are real cases, describes whoever copied it,
not the organisation. Here every rule shows which discussion or incident it came from: the
`origin` field is required and validated.

The catalog fills up through use, from the decisions in reviews and the root causes of
incidents, through `harvest`. Until it does, review leans on the industry baseline and on each
project's own conventions.

GATE also ships optional **seeds** in [`seeds/`](seeds/README.md): rules other organisations
learned the hard way, each with the lesson behind it. During `establish` the orchestrator may
pick some. Each one chosen enters `rules/` as a **candidate**, with this organisation's own id,
the lesson and the seed id as its origin, and it waits for its custodian like any other
candidate. A seed nobody chose is never read: the validator, the generator and review ignore
`seeds/`.

```
python3 bin/adopt_seed.py --list
python3 bin/adopt_seed.py SEED-SEC-01 SEED-BACK-02
```

## Three severities, any scope

| Severity | Directory | What belongs there | How review reports it |
|---|---|---|---|
| Hard rule | `rules/hard/` | What must never happen | Blocking |
| Soft rule | `rules/soft/` | How we build here | Required: fixed before merging, or deferred with a linked ticket |
| Recommended | `rules/recommended/` | The expected path | Suggestion: departing from it is commented, never held against the change |

**A rule is hard only in two cases.** Its check is automated, today or with the tool
identified and queued (`verification: auto` or `auto-backlog`), or breaking it causes a
business defect no tool detects: a duplicate charge, a legal date shifted, data lost, a
document issued wrong, an access that should not exist. The second kind carries the
`business-defect` tag, and the validator asks for it. Anything else that only a person would
notice is soft: a manual rule that blocks trains people to argue with the reviewer instead of
fixing the cause.

Every rule also declares its scope, from the list in [`scopes.md`](scopes.md). A rule in
`candidate` status never blocks, whatever its severity, and while a scope's standard is at
version 0.x none of its rules blocks. The catalog may be laid out by severity, as in the table,
or by scope, with each scope's false positives beside its rules: see `scopes.md`.

## What each rule says about itself

| Field | Values | What it is for |
|---|---|---|
| `verification` | `auto`, `auto-backlog`, `manual` | Whether a tool checks it, a tool is queued, or a person or agent does with explicit criteria |
| `detected_by` | `pipeline`, `self-review`, `review` | Who sees it first when it is missing |
| `applies_when` | conditions on the project profile | Rules that only apply to some projects, such as those with a database |
| `waivable` | `true` (default), `false` | Whether a project, change or line exception may cover it |

`bin/generate_catalog.py` exposes all of them in `catalog.json`, along with `reported_as`, how
review reports each rule today. `bin/applicable.py` tells a project which rules apply to it,
from its profile (see [`project-profile.md`](project-profile.md)) and its remote.

## How a rule gets in

It is harvested, not written. `harvest` proposes candidates traceable to a real decision, one
change request per scope to its custodian. Promoting a candidate to `in force` is a human
decision. See [GOVERNANCE.md](GOVERNANCE.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

When following a rule is not possible, the way out is an exception that names the rule, the
reason, who authorised it and when it expires: [exceptions.md](exceptions.md). What the
organisation decided not to adopt at all goes to
[`calibration/not-adopted.md`](calibration/not-adopted.md), which is not the same as a false
positive.

## Checks

```
python3 bin/validate.py            # names, ids, fields, values, sections and links between rules
python3 bin/generate_catalog.py    # builds catalog.json for the review skills
python3 bin/adopt_seed.py --check  # the seeds are well formed
python3 tests/test_catalog.py      # all of the above, in both directions
```

`catalog.json` is generated on each machine and ignored by version control, so two change
requests to the catalog never conflict on it.

The catalog also gives projects a gate for their pipeline, on any CI platform:
[`ci/README.md`](ci/README.md).

## When a scope grows into a standard

A scope with dozens of rules, a custodian of its own and projects that pin which version they
follow is better kept as **one versioned document** than as dozens of loose files. This is the
pattern that held up in practice; adopt it per scope, when the scope asks for it, not before.

- **One source document per scope**, with numbered sections and rule ids that never change.
  People amend it by change request and nobody edits the derived files by hand.
- **Split into references.** A script splits the document into one file per section, so an
  agent loads the section it needs and not the whole standard. Each generated file says it is
  generated and from which version.
- **A generated index of rules** (id, title, severity, verification, section), so an agent can
  resolve an id without loading anything else.
- **An agents block**: the few lines a project pastes into its instructions file, with the
  project profile, telling the agent where the standard lives and which version applies.
- **A CHANGELOG with semantic versions.** Major: a new hard rule, a rule raised to hard, or ids
  or sections changed; projects owe a dated remediation plan. Minor: a new soft or recommended
  rule, a severity lowered, a scope clarified. Patch: wording only. While the version is 0.x,
  every change is minor and nothing blocks; 1.0.0 is the one the scope's custodian approves.
- **A tag per scope**, such as `backend-v1.2.0`, so releasing one scope never publishes another,
  and the scope's pipeline jobs run only when its files change.
- **The rules in this catalog stay the index.** Each rule of the standard keeps its file, or the
  standard's generated index is what `catalog.json` points to; the review skills must be able
  to resolve every id either way.
