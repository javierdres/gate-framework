---
skill: save
stage: support
name: Keeping what was learned where it belongs
triggered_by: [person]
triggers: []
gate: per-change gate
gate_owner: The custodian of the part that changes
writes_outside: [sdlc repository]
consults: [catalog]
---

# /save — Keeping what was learned where it belongs

## Purpose

Put something worth keeping where the person who will look for it will find it: for the person
alone, or for the whole team.

## Preconditions

The organisation's SDLC and its governance, which says who approves each part.

## What it does

- Asks first whether it is for the person or for the team.
- Personal things go to the person's preferences, their log or their own skills, without asking
  anyone.
- Team things go to the right place: a rule to the catalog through `/harvest`, a discard to the
  false-positive record, product context to its folder, a guide or a script to the tools, a
  method change to the method, a skill to the skills.
- Checks first whether it already exists, and updates it instead of duplicating it.
- Writes for someone who was not in the conversation, with nothing that belongs to a client.
- Proposes team changes as a change request from its own branch, and says who approves it.

## What it does NOT do

- Does not publish to a shared system without the person's approval.
- Does not approve its own change request.

## Gate

**Per-change gate.** Owned by: the custodian of the part that changes, as `GOVERNANCE.md` says.

## Dossier

**Reads:** What the person wants to keep, and `GOVERNANCE.md`.

**Writes:** The change, in the right place, by change request when it is for the team.
