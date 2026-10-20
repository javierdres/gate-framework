---
skill: guide
stage: foundation
name: Explaining the SDLC
triggered_by: [onboard, person]
triggers: []
gate: none
gate_owner: —
writes_outside: []
consults: []
---

# /guide — Explaining the SDLC

## Purpose

Help a person understand what the organisation's SDLC does for them and what they can ask for
today, in the language of their profile.

## Preconditions

The person's profile, and their local configuration readable by the assistant.

## What it does

- **Welcome**, right after `/onboard`: a short live demonstration on the person's own data, such
  as one of their tickets or a repository of their product, read through the SDLC.
- **Why**: what changes compared with using the assistant on its own, said for that profile.
- **Tour**: five minutes through the SDLC as that profile lives it, from the first request to
  the last control point.
- **What can I ask for**: what the profile can do today, checked against the person's local
  configuration, and how to complete whatever is missing.
- Speaks business with product, support and leadership, and code and rules with builders and
  security.

## What it does NOT do

- Does not change the person's configuration or enable a profile.
- Does not promise what the person's configuration cannot do yet: it says what is missing.

## Gate

None. It explains; it decides nothing.

## Dossier

**Reads:** `method/profiles.md`, the person's profile and their local configuration.

**Writes:** Nothing.
