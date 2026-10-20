# Adoption

In this order. Each step works without the ones after it, and none requires the previous one to
be perfect.

## 0. The orchestrator builds the SDLC

Everything else runs inside the organisation's own SDLC, so it comes first. The orchestrator
chooses the assistant, scaffolds the SDLC and lets `/establish` build it with them, following
[BUILDING.md](../BUILDING.md).

```
python3 bin/bootstrap.py sdlc ../sdlc-<org> --assistant <id> --org <org>
```

That writes the skeleton: base files, the empty catalog with its validator, the guards, the
installer and the adapter. `/establish` then interviews the orchestrator and fills in every
layer.

- [ ] Orchestrator named, assistant chosen and its version recorded in `sdlc.yml`
- [ ] Interview summary confirmed by the orchestrator
- [ ] Formulation phase declared in `GOVERNANCE.md`, with exit criteria and a review date
- [ ] Final verification run, every point green or named as pending with who it depends on
- [ ] The SDLC repository created on the code platform, main branch protected

## 1. The standards catalog, empty

Empty on purpose: a set copied from an industry guide describes whoever copied it, not your
organisation. What matters now is that it exists and that rules can only enter through
`/harvest`, traceable to a real decision.

- [ ] Catalog validator clean
- [ ] Custodians named per scope, before the first hard rule rather than during the argument
- [ ] Everyone knows rules are harvested, not written

## 2. Each person's way in

Nothing else runs for someone whose access is not green.

- [ ] Profiles enabled per person in `GOVERNANCE.md`, against a verifiable identity
- [ ] `/onboard` implemented, with a step-by-step access guide per system
- [ ] A person other than the orchestrator installed the SDLC alone, access green
- [ ] Roles that work outside the terminal have their chat-client package and a read-only access
- [ ] Personal credentials per person, never shared, with an expiry

## 3. The pre-review

It returns the most for what it costs and forces nobody else to change how they work.

- [ ] `/self-review` implemented
- [ ] Linters and static analysis reachable from the skill
- [ ] A branch convention that links to the ticket

## 4. The change review, with harvesting inside it

Both together. An assisted review that does not harvest leaves the cycle open.

- [ ] `/review` implemented, designed to run several times
- [ ] `/harvest` triggered by `/review`, never by a person
- [ ] Confirmed that whoever builds does not review their own change

## 5. Functional verification

The product's use cases, validated by product, become automated flows. The manual script covers
the rest. It draws a clear line between review and QA.

- [ ] A use-case catalog for each pilot product, validated by its product owner
- [ ] The flow runner with its allowlist of hosts, and real-world effects cut by default
- [ ] `/verify` implemented, and the full regression before each release
- [ ] Script template adopted for what cannot be automated

## 6. Refinement and design

Once the catalog holds rules worth consulting before settling an architecture.

- [ ] `/refine` and `/design` implemented
- [ ] `/catalog` available to both
- [ ] Confirmed that whoever proposes a design does not accept it

## 7. Operations and SRE

Requires the data sources to exist and be trustworthy, usually the longest work of all.

- [ ] Correlation id propagated end to end
- [ ] One source of truth per question
- [ ] Declared, sufficient retention
- [ ] A rollback procedure exercised, not merely documented
- [ ] `/operate` and `/postmortem` implemented

## 8. Stage 0, definition and requirements

They depend on product picking up the habit, and that cannot be decreed.

- [ ] `/init`, `/define` and `/specify` implemented
- [ ] The dossier adopted as the only source of context

## 9. Outcome validation

Last, because it needs trustworthy business data and the willingness to record that a
hypothesis failed.

- [ ] `/validate-outcome` implemented
- [ ] A validation window set in stage 2 of every piece of work

## When formulation ends

On the review date, check the exit criteria in `GOVERNANCE.md`. If they are met, the orchestrator
announces the end of formulation, custodians start approving and the incompatibilities hold for
everyone, the orchestrator included. If none is met, review the approach before building more.
