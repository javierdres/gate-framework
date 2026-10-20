---
name: establish
description: Builds this organisation's SDLC on GATE, together with the orchestrator. Interviews them, builds the SDLC layer by layer and closes with a final verification. Use it when the SDLC was just scaffolded and is not built yet, or when someone says "establish", "build our SDLC", "set up the SDLC", "start the SDLC", "construir el SDLC", "armar el SDLC" or "levantar el SDLC".
---

# establish

You build this organisation's SDLC together with its orchestrator. You prepare, the
orchestrator decides. This skill implements the `/establish` contract in
`gate-reference/skills/establish/SKILL.md`.

## Before anything

1. Read `gate-reference/BUILDING.md` from top to bottom, or `gate-reference/BUILDING.es.md` if
   the orchestrator works in Spanish. It is your build specification. Section 2 of
   `gate-reference/GATE.md` explains why it is built this way.
2. Read `sdlc.yml`, `PLAN.md` and `GOVERNANCE.md` to see what is already filled in.
3. Read `personal/establish-progress.md` if it exists: a previous session may have left the
   build halfway. Resume from the first layer not marked done.
4. Tell the orchestrator in three lines what is about to happen: the interview, the build in
   layers, the verification. Then start.

## The interview

Follow BUILDING.md section 5. A few questions at a time, the most important first, each with
its default from section 4 so the orchestrator can simply confirm it. Whatever nobody knows is
written as "to be defined" and the build carries on. Never invent a name, a tool or a role.

Close with a summary inside a code block and wait for the orchestrator to confirm it. Nothing
is built before that confirmation.

## The build

Follow the order in BUILDING.md section 10. For each layer:

1. Say which layer comes next and what it will write.
2. Write it, adapted to the organisation's tools and language, starting from what the scaffold
   already left in place.
3. Show what changed and wait for the orchestrator's OK before the next layer.
4. Record the layer as done in `personal/establish-progress.md`, so the build survives a
   session that gets cut short.

Write everything in neutral formats: instructions in `AGENTS.md`, skills in
`skills/<name>/SKILL.md`, guards in `tools/guards/`. Whatever is specific to your own platform
goes in `adapters/<your id>/`. Before writing your adapter, read your platform's current
documentation: hook names, configuration paths and file names change between versions. Record
the version you verified against in `sdlc.yml`.

Implement each phase one skill against its contract in `gate-reference/skills/<name>/SKILL.md`,
and keep what BUILDING.md section 8 says about it: `onboard`, `guide` and `save` for the entry;
`define` against `define` and `specify`; `self-review`; `e2e` against the automated part of
`verify` and the release regression of `deploy`; `harvest`. `onboard` already has a first
version in `skills/onboard/`: adapt it. Replace the examples in `tools/access-checks.tsv` with
the checks each profile of this organisation needs.

When the code platform has no protected branches or merge requests, set up
`tools/server-hooks/` as its README says, with `identity.method: ssh-signing` in `sdlc.yml`.

As soon as the SDLC repository exists on the code platform, push it once with its upstream
(`git push -u origin main`), with the orchestrator's OK, so every later session can update it.

Fill in `GATE.md` at the root with what implements what and the first departures, each with
its reason.

## The verification

Run the checklist in BUILDING.md section 11, point by point, for real: run the installer twice,
try an outward write with and without authorisation, make a guard fail on purpose. Report each
point with ✓ or ✗ inside a code block, and for every ✗ say what is missing and who it depends
on.

When every point is green or named as pending, write today's date in `built` in `sdlc.yml`, so
the instructions stop offering `establish`. Then hand over to `onboard` for the first person
other than the orchestrator.

## Never

- Never write rules into the catalog. It starts empty, apart from examples marked as such.
- Never choose the assistant, the roles, the profiles or the scope. The orchestrator does.
- Never publish anything to a shared system (push, change request, ticket) without the
  orchestrator's explicit OK.
- Never copy another organisation's rules, products, names or data.
- Never ask for or accept a credential in the chat.
- Never declare formulation over. Only the orchestrator does, against the exit criteria in
  `GOVERNANCE.md`.
