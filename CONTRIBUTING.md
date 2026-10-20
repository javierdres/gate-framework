# Contributing to GATE

GATE is in use and under continuous improvement. The most valuable contributions come from
having applied it, not from having read it.

## What helps most

**Lessons from an organisation's SDLC.** Every SDLC built on GATE keeps a map of where it
departs from the framework. A departure that turned out to be right in practice is the best
contribution there is. Propose it as a candidate: the pattern, what it solved, and what it cost.
Never the organisation's names, products, tickets, incidents or data; GATE never links to an
organisation's SDLC, which is private by nature.

**Adoption experience.** Which stage was hardest to roll out, which one you skipped and what
happened, at what team size, on which assistant. That is worth more than a wording fix.

**Adapters.** If you wired an SDLC to an assistant that has no adapter in `kit/adapters/` yet,
contribute it, with the version you verified it against.

**Sharpened skill contracts.** If implementing a skill showed it is missing a limit, or doing
something it should not, change it and explain the case that prompted it.

**New anti-patterns.** That section grew out of real mistakes. If you have seen one that is
missing, add it with what it cost.

## What does not belong here

Specific standard rules. The catalog belongs to each organisation and lives in its own SDLC:
this framework defines how it is fed, not what it says.

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

If you touched `kit/` or `bin/bootstrap.py`, run the kit's tests, then scaffold a throwaway SDLC
and check that its catalog validates and that its installer runs twice without duplicating
anything.

```
python3 kit/tools/guards/tests/test_permissions.py
python3 kit/tools/guards/tests/test_session_start.py
python3 kit/catalog/tests/test_catalog.py
bash kit/tools/server-hooks/tests/test_update.sh
```

```
python3 bin/bootstrap.py sdlc /tmp/sdlc-test --assistant claude-code --org test
python3 /tmp/sdlc-test/catalog/bin/validate.py
```

If you touched `GATE.md`, regenerate the PDF.

```
python3 bin/build_pdf.py GATE.md
```

Record what changed and why in `CHANGELOG.md`.

## Licence of contributions

By submitting a contribution you agree it is published under the repository's licences: CC BY
4.0 for documentation and MIT for code. Nothing to sign.
