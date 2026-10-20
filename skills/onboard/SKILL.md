---
skill: onboard
stage: foundation
name: A person's way in
triggered_by: [establish, person]
triggers: []
gate: none
gate_owner: —
writes_outside: []
consults: []
---

# /onboard — A person's way in

## Purpose

Leave a person ready to work in the organisation's SDLC: requirements met, the SDLC installed,
their profile recorded, every access their profile needs verified, and a first demonstration on
their own data.

## Preconditions

The organisation's SDLC, built by `/establish`. The person's verifiable identity, as an account
on the code platform or the tracker, and their row in the profiles table of `GOVERNANCE.md`.

## What it does

- Shows the stages as a map with what is done marked: requirements, installation, profile,
  access, welcome. Picks up wherever the session-start guard says it stopped.
- **Requirements**: runs the checker and gives the exact command for the person's system for
  anything missing.
- **Installation**: checks the SDLC repository sits inside a working folder and not loose in the
  home folder, explains what the installer does, runs it with approval, and asks the person to
  reopen the assistant in the working folder.
- **Profile**: name, profiles and products, saved in `personal/profile.md`. Offers only the
  profiles enabled for the person's verified identity.
- **Access**: explains what the profile needs and why, then sets up each missing access one at
  a time with its guide, and verifies only that one before the next. Prefers company login and
  connectors over hand-made tokens, with the least privilege that works and an expiry. When an
  access depends on someone else, says who to ask and carries on.
- **Welcome**: a live demonstration on the person's own data, such as one of their tickets or a
  repository of their product, and marks setup as done.
- For a role that works outside the terminal, sets up the chat-client package instead of the
  installation.
- Whatever the person has to run outside the assistant is given step by step: how to open the
  terminal, what to paste, what they will see, how to know it worked, and what to do if it fails.

## What it does NOT do

- Never asks for or accepts a credential in the chat. If one is pasted, it asks the person to
  revoke it.
- Does not enable a profile. The orchestrator does, in `GOVERNANCE.md`.
- Does not share one token among people.

## Gate

None. Every access is verified, and nothing else runs for a profile whose access is not green.

## Dossier

**Reads:** `GOVERNANCE.md`, `method/profiles.md` and the access guides in `tools/guides/`.

**Writes:** The person's `personal/profile.md`, and the state of their setup. Nothing shared.
