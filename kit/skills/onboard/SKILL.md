---
name: onboard
description: Leaves a person ready to work in this organisation's SDLC: requirements, installation, profile, access verified one at a time, and a short demonstration on their own data. Use it the first time someone opens the assistant in the SDLC, when the session start says setup is unfinished, or when someone says "onboard", "set me up", "configure", "install", "my access does not work", "configurar", "instalar" or "no me funciona".
---

# onboard

You leave one person ready to work. This skill implements the `/onboard` contract in
`gate-reference/contracts/onboard.md`. The orchestrator adapts it during `establish`.

## The map

Show the stages inside a code block, with what is done marked, and pick up wherever the
session-start guard said setup stopped:

```
  SETUP
  ──────────────────────────────────────────────────────────
  ○  1  Requirements
  ○  2  Installation
  ○  3  Profile
  ○  4  Access
  ○  5  Welcome
```

## 1. Requirements

Check what the SDLC needs on this machine: git, Python 3, and whatever `tools/` and the person's
profile use. For each thing missing, give the exact command for their operating system, step by
step.

## 2. Installation

Check that this repository sits inside a working folder, not loose in the home folder. Explain
in two lines what `tools/install.sh` does, run it with the person's OK, passing the assistant
they use (`claude-code`, `gemini-cli`, `kiro`, `codex` or `other`), and ask them to reopen the
assistant in the working folder, not inside this repository.

## 3. Profile

Identify the person by their verified account on the code platform or the tracker, never by the
name they type. Read their row in the profiles table of `GOVERNANCE.md` and offer only the
profiles enabled there. Save name, profiles and products in `personal/profile.md`, following
`method/templates/profile.md`.

## 4. Access

Read in `method/profiles.md` what their profile needs and explain why. Then, for each access
missing, one at a time: give the steps of its guide in `tools/guides/`, wait, and verify only
that one before the next. Prefer company login and connectors over hand-made tokens, with the
least privilege that works and an expiry. When an access depends on someone else, say who to
ask and carry on with the rest.

Whatever the person has to run outside the assistant is given step by step: how to open the
terminal, what to paste, what they will see, how to know it worked and what to do if it fails.

## 5. Welcome

A short live demonstration on the person's own data: one of their tickets, or a repository of
their product, read through the SDLC. Then add `ready: <today>` to `personal/profile.md`.

## Never

- Never ask for or accept a credential in the chat. If one is pasted, ask the person to revoke
  it and create a new one.
- Never enable a profile. The orchestrator does, in `GOVERNANCE.md`.
- Never share one token among people.
