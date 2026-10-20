---
skill: establish
stage: foundation
name: Build the organisation's SDLC
triggered_by: [person]
triggers: [onboard]
gate: orchestrator gate
gate_owner: Orchestrator
writes_outside: [sdlc repository]
consults: []
---

# /establish — Build the organisation's SDLC

## Purpose

Take an orchestrator from GATE to a working SDLC of their own organisation: a repository with
its method, its empty catalog, its products, its skills, its guards and the way each person
gets in, running on the AI assistant the orchestrator chose. It follows
[BUILDING.md](../../BUILDING.md) from top to bottom.

## Preconditions

A named orchestrator, with authority to assign roles in the organisation.

An AI assistant chosen by the orchestrator that loads persistent instructions every session
and can work in a repository and a shell. Hooks and connectors are preferred; without them the
SDLC uses the platform fallback described in BUILDING.md section 3.

A place to create the SDLC repository on the organisation's code platform.

## What it does

- **Runs the interview first** (BUILDING.md section 5), a few questions at a time, each with
  its default. Whatever nobody knows is marked "to be defined" and never invented. Closes with
  a summary the orchestrator confirms. Nothing is built before that.
- Records the orchestrator's decisions (BUILDING.md section 4) in `sdlc.yml`, `GOVERNANCE.md`
  and `PLAN.md`, including the assistant and the version it will be verified against, and the
  formulation exit criteria with their review date.
- Builds the SDLC **in layers, in the order of BUILDING.md section 10**, and shows each layer
  before starting the next.
- Writes everything in neutral formats: `AGENTS.md` for instructions, `SKILL.md` folders for
  skills, guards that read the action as JSON on standard input, Model Context Protocol for
  connectors.
- Writes the adapter for the assistant it runs on, **after reading that platform's current
  documentation**, and leaves in `adapters/README.md` what another assistant would need.
- Implements the phase one skills against the contracts in this repository, adapted to the
  organisation's tools and language.
- Writes `GATE.md` in the SDLC with the commit of GATE implemented and the first departures,
  each with its reason.
- Runs the final verification (BUILDING.md section 11) and reports every point as passed or
  failed, with what is missing and who it depends on.
- Hands over to `/onboard` for the first person other than the orchestrator.

## What it does NOT do

- Does not write rules into the catalog. It starts empty, apart from examples marked as such.
- Does not choose the assistant, the roles, the profiles or the scope. The orchestrator does.
- Does not publish anything to a shared system without the orchestrator's approval.
- Does not copy another organisation's rules, products, names or data.
- Does not declare formulation over. Only the orchestrator does, against the exit criteria.

## Gate

**Orchestrator gate.** Owned by: Orchestrator. The interview summary, each layer and the final
verification are accepted before the build moves on.

## Dossier

**Reads:** The orchestrator's answers to the interview, and whatever can be read off the
organisation's existing repositories and tools.

**Writes:** The organisation's SDLC repository, with `sdlc.yml`, its governance and its plan,
and the final verification report. There is no work-item dossier yet: this is what makes the
first one possible.
