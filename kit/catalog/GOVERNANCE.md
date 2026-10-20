# Catalog governance

## A rule's life

| Status | What it means | Effect on review |
|---|---|---|
| `candidate` | Drawn from a real decision, not yet approved | Reported as a suggestion, whatever its severity. Never blocks |
| `in force` | Approved by its custodian | Hard blocks, soft suggests |
| `deprecated` | Superseded or dropped | Ignored. The file is not deleted |

A deprecated rule keeps its file and its id: an old review may cite it, and if the id
disappears that comment is orphaned. Mark `status: deprecated` with `superseded_by`, and never
reuse an id.

## Who approves

Each scope has its custodian, named by role in `scopes.md`; who holds each role is in the SDLC's
`GOVERNANCE.md`. A soft rule needs its scope's custodian. A hard rule needs every custodian,
because it blocks everyone's changes.

## What does not belong here

How one project is built: its patterns, its stack, its deliberate exceptions. That lives in the
project's own context in `products/`.

Generic good practice with no decision of our own behind it: the industry baseline already
covers it, and adding it here drowns out the signal.

## False positives

`calibration/false-positives.md` does not follow the life cycle above. It needs no approval and
the validator does not read it; an entry blocks nothing, it only tells review that a finding was
already discussed and rejected.
