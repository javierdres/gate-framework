# Seeds

Optional rules GATE offers to an organisation starting its catalog. Each one was learned by an
organisation that applied GATE, and carries the lesson behind it, told without that
organisation's names, products, people or data.

Nothing here applies on its own. The validator, the generator and the review skills never read
this folder. A seed becomes a rule only when the orchestrator chooses it during `establish`, or
a custodian chooses it later, and even then it enters as a candidate that its custodian has to
approve.

## Two kinds

**Lesson** seeds come from an incident or an audit: something broke, cost money or exposed
data, and the rule is what stopped it from happening again. They are the strongest: if the
same risk exists in your systems, the lesson probably holds.

**Baseline** seeds come from a standard that organisation built by measuring its own fixes and
review comments. Each was traced to a pattern of fixes, but to theirs, not to yours. Adopt the
ones whose risk you recognise; the quarterly review and the 50% rule will tell you within months
whether they hold here.

```
python3 bin/adopt_seed.py --list
```

## How a seed is adopted

```
python3 bin/adopt_seed.py SEED-SEC-01 SEED-BACK-02 SEED-OPS-04
python3 bin/adopt_seed.py SEED-AI-01 --scope cross-cutting   # into a scope you do have
python3 bin/validate.py
```

Each seed is copied into `rules/` with the next free id of its folder, `status: candidate`,
`approved_by` empty, its lesson and its seed id as its `origin`, and `seeded_from` pointing back
here. The seed's scope has to exist in `scopes.md`; when it does not, either add the scope or
adopt the seed into one you have with `--scope`. A seed already adopted is skipped, so the
command can be run again safely.

After that the rule is the organisation's: its custodian may reword it, change its severity or
reject it, and none of that comes back here.

## Format

The rule format of `rules/_TEMPLATE.md`, with three differences: no `id`, `status`, `origin`,
`approved_by` or dates, which adoption writes; a `seed_id` (`SEED-<SCOPE>-NN`) that names the
file; and `kind` and `lesson`. The seeds sit in a folder per scope. `python3 bin/adopt_seed.py
--check` validates them, and the catalog's tests adopt every seed into a throwaway catalog and
validate the result.

## What is not seeded, because GATE's method already says it

- No agent writes to a change request, a ticket or production without explicit authorisation,
  and the authorisation does not carry over between change requests or sessions: the principle
  "Nothing runs unattended into shared systems" and `method/permissions.md`.
- The specification, design and tasks of a feature are part of what is delivered: the dossier.
- A session starts by declaring what it will touch and reading the project's context: the
  dossier and `method/session-start.md`.
- Whoever builds a change does not review it: the three incompatibilities.

## Contributing a seed

A seed needs a lesson someone can trace: an incident, an audit, a measured pattern of fixes.
Generic good practice with nothing behind it does not get in. Write the lesson as a pattern,
never with an organisation's names or data, and see GATE's `CONTRIBUTING.md`.
