# Contributing to GATE

GATE is in use and under continuous improvement. The most valuable contributions come from
having applied it, not from having read it.

## What helps most

**Lessons from an organisation's system.** Every system built on GATE keeps a map of where it
departs from the framework. A departure that turned out to be right in practice is the best
contribution there is. Propose it as a candidate: the pattern, what it solved, and what it cost.
Never the organisation's names, products, tickets, incidents or data; GATE never links to an
organisation's system, which is private by nature.

**Adoption experience.** Which stage was hardest to roll out, which one you skipped and what
happened, at what team size, on which assistant. That is worth more than a wording fix.

**Adapters.** If you wired a system to an assistant that has no adapter in `kit/adapters/` yet,
contribute it, with the version you verified it against.

**Sharpened skill contracts.** If implementing a skill showed it is missing a limit, or doing
something it should not, change it and explain the case that prompted it.

**New anti-patterns.** That section grew out of real mistakes. If you have seen one that is
missing, add it with what it cost.

## What does not belong here

Specific standard rules, except as seeds. The catalog belongs to each organisation and lives in
its own system: this framework defines how it is fed, not what it says. What GATE does accept is a
seed in `kit/catalog/seeds/`: an optional rule an organisation can choose to adopt as a
candidate, carrying a lesson someone can trace, such as an incident, an audit or a measured
pattern of fixes, told as a pattern without the organisation's names or data. A seed with no
traceable lesson does not get in, however sensible it sounds. Run
`python3 kit/catalog/bin/adopt_seed.py --check` before proposing one.

Ceremonies, cadence or estimation. GATE describes the journey of a piece of work and who clears
each step; how you organise the team sits outside.

Anything that ties the framework to one AI vendor outside an adapter.

Generic good practice with no decision behind it. If you cannot trace it to something that
happened, it is not material for this framework yet.

## Before opening a pull request

Run the validator. It checks the contracts are complete and the trigger chain closes both ways.

```
python3 bin/validate.py
```

If you touched `kit/` or `bin/bootstrap.py`, run the kit's tests, then scaffold a throwaway system
and check that its catalog validates and that its installer runs twice without duplicating
anything.

```
python3 kit/tools/guards/tests/test_permissions.py
python3 kit/tools/guards/tests/test_session_start.py
python3 kit/tools/guards/tests/test_usage.py
python3 kit/catalog/tests/test_catalog.py
python3 kit/tools/tests/test_use_cases_index.py
python3 kit/tools/adapters_check.py
bash kit/tools/server-hooks/tests/test_update.sh
bash kit/tools/tests/test_rename.sh
bash kit/tools/tests/test_install.sh
bash kit/tools/tests/test_older_names.sh
bash bin/tests/test_scaffold.sh
sh kit/e2e/run-unit-tests.sh
```

Run them in a terminal, not inside an assistant session: some scripts refuse to run there, and
the assistant's environment variables change what the installer detects.

```
python3 bin/bootstrap.py system /tmp/deskmate-test --assistant claude-code --org test
python3 /tmp/deskmate-test/catalog/bin/validate.py
```

If you touched `GATE.md`, regenerate the PDF.

```
python3 bin/build_pdf.py GATE.md
```

Record what changed and why in `CHANGELOG.md`.

## Deprecations

Systems built on GATE move to a new version when their orchestrator decides, so a name the kit
reads (a file, a marker, an environment variable, a function) never changes from one day to the
next. The new name is written from the change that introduces it, and the old one is still read
for at least three months and two dated entries of `CHANGELOG.md`. Removing it is announced in
an entry of its own, with its "What to do". The shell names an organisation's own scripts call,
`$SDLC` and the `sdlc_*` functions of `tools/lib.sh`, stay as aliases with no end date.

## Licence of contributions

By submitting a contribution you agree it is published under the repository's licences: CC BY
4.0 for documentation and MIT for code. Nothing to sign.
