# Changelog

What changed in GATE, and why. An organisation's SDLC pins a commit; this file says what moving
to a newer one brings.

## 2026-10-20 · /establish works from the first minute

The previous release told the orchestrator to scaffold the SDLC and run `/establish`, but a
fresh scaffold had no such skill, nothing registered where an assistant looks for skills, and
no copy of the guide the skill follows. The first step failed.

`bootstrap.py sdlc` now writes executable `establish` and `onboard` skills in the open
`SKILL.md` format, copies GATE, BUILDING and every contract into `gate-reference/`, and for
Claude Code registers both skills inside the SDLC itself. `AGENTS.md` tells any other assistant
to offer `establish` while the SDLC is not built. The adapters for assistants other than Claude
Code are now marked as unverified starting points, and the video script carries the scene the
current video lacks.

## 2026-10-20 · The foundation an orchestrator builds from

GATE was put into practice: a real organisation built its SDLC on it and ran it for six weeks.
That showed what the framework lacked. It described an SDLC that already existed, and said
nothing about who builds it, with which assistant, or how. This release is about that.

**The orchestrator and `/establish`.** A new section 2 and a ninth role. The orchestrator builds
the organisation's SDLC together with the assistant, chooses which assistant, assigns roles and
profiles, and decides when the SDLC is ready. `/establish` is the first skill: an interview with
defaults, a build in layers, a final verification. [BUILDING.md](BUILDING.md), in English and in
Spanish, is the complete guide it follows.

**Any assistant.** The SDLC is written once in neutral formats: `AGENTS.md` for instructions,
the open `SKILL.md` format for skills, guards that read the action as JSON on standard input,
and Model Context Protocol for connectors. A thin adapter wires it to Claude Code, Gemini CLI,
Kiro, Codex or any other. Without hooks, the platform carries the enforcement and the SDLC says
so.

**`bootstrap.py sdlc` and `kit/`.** One command writes the skeleton of the organisation's SDLC:
base files from the templates, the empty catalog with its validator, a working permissions
guard with session-scoped authorisations, the session-start and log guards, an idempotent
installer and the Claude Code adapter.

**The formulation phase.** While the SDLC is being built the incompatibilities cannot hold. GATE
now accepts that on two conditions: the phase is declared and its exit is written before it
starts. Once it ends, the orchestrator is bound like everyone else.

**`/onboard`.** Each person's way in: requirements, installation, profile, access verified one
at a time, and a demonstration on their own data. Roles that work outside the terminal get in
through a chat client with a read-only access of their own.

**Principles.** Approval by scope for the session instead of one by one, with a list that is
never delegated. Controls enforced by the environment rather than by the prompt. Verifying
against what is deployed. Roles, not names, with identity verified. Nobody does another
person's part. Writing for whoever decides. One session, one workspace.

**The person, a fifth level.** Profile, preferences, personal credentials and the log of their
own work, kept by the assistant without being asked. It never leaves the person's machine.

**Use cases and automated flows.** Stage 2 proposes use cases that product validates. Stage 8
turns them into flows the assistant runs on the verifier's machine, never against production,
and the verifier signs. Stage 9 runs the full regression before each release. Pre-review and
review look only at what the change introduced, and a push clears the approval.

**Indicators and anti-patterns.** Judgement at the gates, measured by how often each one rejects
or corrects. The formulation with no exit, the SDLC tied to one assistant, the gate that never
says no, controls written only as instructions, the test that reads the code, the false red
left on, and building more instead of putting it to use.

## 2026-09-11 · First public version

The cycle, the gates, the roles and their incompatibilities, the scopes, the skill contracts,
the catalog and config scaffolds, and the validator.
