# Catalog governance

## A rule's life

| Status | What it means | Effect on review |
|---|---|---|
| `candidate` | Drawn from a real decision, or adopted from a GATE seed, not yet approved | Reported as a suggestion, whatever its severity. Never blocks |
| `in force` | Approved by its custodian | Hard blocks, soft is required, recommended suggests |
| `deprecated` | Superseded or repealed | Ignored. The file is not deleted |

A deprecated rule keeps its file and its id: an old review may cite it, and if the id
disappears that comment is orphaned. Mark `status: deprecated` with `superseded_by` set to the
rule that replaces it, which lists it back in `supersedes`, or to `repealed` when nothing
replaces it. A repealed rule also gets a row in the derogated table of
[`calibration/not-adopted.md`](calibration/not-adopted.md), with the version, the reason and
what to do instead. The validator checks both directions.

## Who approves

Each scope has its custodian, named by role in `scopes.md`; who holds each role is in the system's
`GOVERNANCE.md`. A soft or recommended rule needs its scope's custodian. A hard rule needs every
custodian, because it blocks everyone's changes. A seed adopted during `establish` follows the
same path: it enters as a candidate and the same custodian decides.

## Obligations of the catalog

These bind the catalog and whoever runs it, not the authors of a change. None of them blocks a
change request.

**A named owner.** Each scope, and each versioned standard, has one custodian who approves its
changes. A rule set with no owner stops being updated and starts being ignored.

**A quarterly review with metrics.** Every quarter the custodians look at numbers a script
produced, not impressions: adherence per rule, findings per rule, false positives per rule,
candidates waiting and their age, and which fixes in the quarter had no rule behind them.
Mechanical changes, such as releases and mirrors between branches, are left out, and the same
fix applied to several branches counts once.

**The 50% rule.** A rule whose adherence stays under 50% for two quarters is automated or
repealed. A rule left written and broken teaches that rules are optional, including the ones
that matter.

**Ids are never reused.** A repealed id stays repealed. Reusing it makes every old review that
cites it say something it never said.

**No evidence, no entry.** Every rule cites what it came from: a review thread, an incident, a
measured fix, a metric. A rule with no evidence behind it is an opinion, and it does not get in,
however sensible it sounds. A seed's evidence is the lesson it carries, and its custodian decides
whether that lesson holds here too.

**A question that will become a rule does not live in a diff thread.** When a review uncovers a
gap in the catalog, the question goes to the catalog's repository as an issue or a candidate,
to the scope's custodian. The change merges with the behaviour the catalog already allows.
Settled inside a thread, the answer applies to one change and is lost for the rest.

**Every project declares the version it follows**, when a scope is kept as a versioned
standard. The gate warns when a project is behind by a minor and fails when it is behind by a
major. See [`ci/README.md`](ci/README.md).

## When the practice and the catalog disagree

In this order:

1. If the rule can be automated, automate it and fix the code.
2. If the code breaks it everywhere, it applies only to new code, with today's count recorded as
   the project's baseline and frozen by the gate.
3. If adherence stays under 50% for two quarters, automate it or repeal it.
4. If the team's practice contradicts the catalog, the practice wins, or the catalog explains
   in writing why not.

## The monthly harvest

Thirty minutes a month with the custodians. `harvest` prepares it: the candidates by scope,
with their age and origin; the false positives recorded since the last one; the candidates that
already applied in a second place, which may become cross-cutting; and the rules in force that
nobody cited, which may be repealed. What gets decided stays in the repository, one change
request per scope.

## What does not belong here

How one project is built: its patterns, its stack, its deliberate exceptions. That lives in the
project's own context in `products/`.

Generic good practice with no decision of our own behind it: the industry baseline already
covers it, and adding it here drowns out the signal.

## False positives and rejections

`calibration/false-positives.md`, or the `false-positives.md` beside each scope in the layout by
scope, does not follow the life cycle above. It needs no approval and the validator does not
read it; an entry blocks nothing, it only tells review that a finding was already discussed and
rejected. `calibration/not-adopted.md` is different: it records what the organisation decided,
as a standard, not to adopt, and that decision belongs to the scope's custodian.
