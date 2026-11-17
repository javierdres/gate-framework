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
  as one of their tickets or a repository of their product, read through the SDLC. One per
  profile, read only. If a query fails for lack of an access, it says so in one line and moves
  to the next.
- **Why**: what changes compared with using the assistant on its own, said for that profile.
- **Tour**: five minutes through the SDLC as that profile lives it, from the first request to
  the last control point.
- **What can I ask for**: what the profile can do today, checked against the person's local
  configuration, and how to complete whatever is missing. A skill whose own prerequisites do
  not exist yet, such as a local file it asks for the first time, is shown as built on first use,
  not as an error. A personal credential close to its expiry is mentioned before it fails.
- Speaks business with product, support and leadership, and code and rules with builders and
  security.

## What it does NOT do

- Does not change the person's configuration or enable a profile.
- Does not promise what the person's configuration cannot do yet: it says what is missing.
- Never shows invented or example data as if it were the person's own.
- Writes nothing outside the person's own folder.

## Gate

None. It explains; it decides nothing.

## Dossier

**Reads:** `method/profiles.md`, the person's profile and their local configuration.

**Writes:** Nothing.
