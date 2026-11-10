# Changelog

What changed in GATE, and why. An organisation's SDLC pins a commit; this file says what moving
to a newer one brings.

## 2026-11-10 · A company that writes in Spanish and tracks in Linear

A fourth simulation rebuilt an SDLC from scratch with the previous release: a company working in
Spanish, on a self-managed GitLab, with Linear as its tracker and Grafana in production. It came
out clean on the first try, every point of the final verification green or skipped on purpose,
and the sixteen earlier fixes held. It also found what would still have hurt a company like
that, fixed here.

**Spanish no longer breaks the guards silently.** The session start guard reads the profiles
heading of `GOVERNANCE.md` and the keys of `personal/profile.md` in Spanish as well, and the
guide says which keys stay as GATE writes them.

**Any tracker can be authorised, not only Jira.** The permissions guard reads Linear's team and
issue identifiers, and a write through an API client that names a ticket key falls under that
tracker's authorisation. A connector verb the guard does not recognise now asks instead of
passing. GraphQL clients, where every call is a POST, take `QUERY` or `MUTATION` as their intent.

**Moving the working folder no longer breaks the guards.** The installer points the hooks at
the guards through the project folder, and replaces the absolute entries an older installer
wrote instead of duplicating them.

**Smaller fixes.** A person with no profile sees the profile menu again; the permissions
method no longer contradicts the infrastructure reads; `/onboard` reports a check that depends
on someone else, such as an SDLC not pushed yet, as pending rather than as the person's
problem; the identity example names the host of a self-managed platform and quotes cleanly;
the enabled profiles come without stray backticks; and the establish contract knows about
skipped steps.

## 2026-11-10 · A first build that comes out clean

A third simulation built the SDLC of an invented company end to end with GATE alone, and
checked it in real assistant sessions. The method held: the skills behaved as their contracts
say and every guard and catalog test passed. It also found sixteen places where the guide, the
kit and the scaffold disagreed or left the orchestrator to guess. They are all fixed, so the
next organisation does not trip on them.

**The guards are whole from the first minute.** The scaffold registered only the session start
and permissions guards until the installer ran; it now registers the log reminder and the usage
check too. The guide counted three guards where the kit ships four.

**The permissions guard reads more, and sees more.** Infrastructure tools no longer ask for
every command: read-only subcommands such as `kubectl get`, `kubectl logs` or `helm status`
pass, while anything else, a secret read included, still asks, wherever the tool sits in the
command. An organisation's own API clients in `tools/clients/` now take the HTTP method first,
so GET and HEAD pass and any other call asks; before, a write through them went unseen. Both
come with tests.

**Where the SDLC lives is no longer a guess.** The examples scaffold into
`~/Projects/<org>/sdlc-<org>` instead of next to GATE, the scaffold warns when the folder the
installer would wire is the home folder or another repository, and `/establish` checks it
before starting. The skeleton is step one of the build order and the interview step two, which
is what actually happens. Skill links are relative, so moving the working folder does not break
them.

**Names, profiles and access, one way each.** `--name` gives the organisation a display name
apart from its short name. `method/profiles.md` opens with the list of profile ids every other
file uses. The access checks separate `requirements`, what the machine needs before installing,
from `all`, the access everyone needs, so the first check no longer fails before there is
anything to grant.

**Smaller fixes.** The pilot products get their folders during the build and any other product
on first use; the catalog has one false-positive record, as the kit always had; the names check
leaves licence notices aside; where the code platform accepts any single code owner, the change
request template carries one line per custodian; commit signing is configured per working
folder, never globally; and the final verification can mark a step skipped on purpose, with its
reason, instead of only pass or fail.

## 2026-11-04 · Nobody runs out of the assistant without being told

Subscription plans meter use in windows that reset at a fixed time. Whoever is focused on the
work does not watch them, and finds out the window is spent when the assistant stops
answering, often in the middle of something that matters.

**A new principle and a new guard.** Section 4 adds the principle, and section 2 adds usage data
to the capabilities an assistant may offer. The kit gains `tools/guards/usage.py` with its
tests. In the status line it shows the model, the context used and each window with its reset
time, and flags a window that will run out before it resets at the current pace. On every
message it reads what the status line recorded and, once per session, has the assistant warn
the person and suggest a lighter model, running its own subagents on one until the reset. When
the window resets, it suggests the most capable model again. The person always chooses the
session's model.

**Claude Code wires it on its own.** Its adapter registers the status line, unless the person
already has one, and the per-message check. Verified on Claude Code 2.1.314, which hands the
five-hour and weekly windows to the status line. An assistant that does not expose its usage
has no warning, and its SDLC says so in `PLAN.md`.

Learned in an organisation's SDLC, where the status line also shows the balance of a paid
provider the team shares. That part stays there: a status line is a good place for whatever an
organisation must not run out of, but which ones are its own business.

## 2026-11-03 · Several SDLCs on one machine

A person often carries more than one SDLC on the same computer, and an SDLC built on GATE had
installed its skills in the assistant's global configuration. They showed up in every folder,
including unrelated work, and two SDLCs with a skill of the same name competed for it. GATE's
own adapter already installed in the working folder, but the rule was never written down, so
nothing stopped an SDLC from drifting away from it.

**The rule is now explicit.** Everything an organisation's SDLC installs lives in its working
folder, never in the assistant's global configuration. Section 8 of GATE explains why, the
building guide lists it among the instructions for the assistant, the adapters guide repeats it
for any new adapter, and the final verification checks it.

**Where the assistant is opened matters, and now it says why.** Verified on Claude Code
2.1.314: project skills are found walking up from where the assistant is opened, up to the
root of the enclosing repository. Opened inside a product repository, the working folder's
skills are not found. And when the working folder itself sits inside another repository, as
with a home folder under version control, the assistant's automatic memory is shared across
everything below it. The installer now warns about that case.

**Credentials carry the organisation in their name**, so two SDLCs on the same machine never
read each other's keys.

## 2026-10-20 · The guard and the review cannot be talked around

An independent check of the previous release, on a clean clone, confirmed 28 of the 33 fixes
working and found that the two controls that matter most could still be bypassed. This release
closes them, with a test for every bypass found.

**The permissions guard is conservative now.** A session authorisation covers only a simple
command the guard reads completely. A write inside `sh -c`, `eval`, a subshell, a command
substitution, `env` or `xargs` always asks; so does a push through a full path to git, a push
after a `cd` into another repository, and a push to a remote the repository does not declare.
Quotes can no longer hide a self-authorisation, the authorisations file cannot be written by any
command or file tool, a lowercase `delete` is still a deletion, and connector calls are judged
by what they do: merges and deletions always ask, other writes ask unless authorised, reads pass.
The Claude Code adapter now sends the file tools to the guard too, and a freshly scaffolded SDLC
has its guards active from the very first session, before anything is installed. Verified in a
real Claude Code session, where `sh -c 'git push origin main'` was stopped.

**The server hook trusts signatures, not text.** A merge reaching the default branch must be
signed by the person its `Reviewed-by` trailer names, and that person must not have signed any
of the commits being merged. Writing someone else's name in the trailer, or in the author field,
no longer passes. The hook ships with its own test, eight cases on a throwaway server.

**Identity is proved, not configured.** With SSH signing keys, the session start guard signs a
fresh challenge with the person's key and verifies it against `allowed_signers`, so pointing git
at someone else's public key gets nobody their profiles. The guard reads quoted values with
escapes correctly, and has tests of its own.

**Smaller fixes.** The false-positive example no longer counts as an entry; the project config
template passes its own check; `--help` works in every script; only the chosen assistant's
adapter is copied; onboarding runs the shared checks before the profile exists; products carry an
`incidents/` folder; the moments of human invocation are described consistently.

## 2026-10-20 · Everything the simulation found, fixed

A second test built the SDLC of an invented health software company from scratch with GATE
alone, and used it across the whole cycle. The method held and the SDLC added real value, but
the test found 33 problems in the kit and the documents. This release fixes all of them.

**The permissions guard.** Rewritten. It judges every segment of a chained command, always asks
for pushes to the default branch and for forced, mirrored, pruning, deleting and all-branch
pushes, sees implicit API writes, and can no longer fail open: an empty input, a broken input or
a malformed option all end in asking. It ships with tests that check the reason as well as the
decision.

**The catalog.** Moved from strings inside `bootstrap.py` to real files in `kit/catalog/`, with a
shared parser. The validator now rejects an empty origin, unknown scopes, a severity that does
not match its folder, unknown statuses, invalid dates and a hard rule without exceptions, and
accepts multi-line lists and quoted values. The generator strips quotes and counts by folder.
`catalog.json` is generated locally and ignored, so two change requests never conflict on it. The
rule template passes its own validator. Tests cover both directions.

**The session start guard.** It now detects a missing or outdated installation, reports a missing
upstream instead of failing to pull, identifies the person by platform account, SSH signing key
or declared email, hands over the profiles enabled for them, runs the access check, and finds the
open items of the log in any language through a marker.

**Identity and platforms without protection.** An SSH signing key listed in the SDLC is now a
verifiable identity. `kit/tools/server-hooks/update` gives a plain git server what a code
platform would: no rewrites of the main branch, signed commits, and merges reviewed by someone
other than their author, lifted only during formulation.

**Missing pieces.** Contracts for `guide` and `save`; `tools/check-access.sh` with its
per-profile checks; a ticket template that carries the dossier in phase one; a copy of GATE in
`gate-reference/` with its own paths, so no link inside it breaks; `built` in `sdlc.yml`, so the
instructions stop offering `establish` once the SDLC is verified; the push with upstream as a
build step.

**Clarified rules.** "What the change introduced" now has a border: the lines it adds or
modifies, including an old problem on a line it modifies, and a private channel to security for
something serious seen in passing. Harvest has two primary and two secondary sources, and in
phase one the person who closes a review runs it. Incidents close with a postmortem even before
`/operate` and `/postmortem` exist. Machine keys stay in English. Templates name roles, never
people.

**The installer and the adapter.** The adapter backs up a settings file only when it changes,
quotes every path, and the installer stamps the version it installed. The Claude Code adapter
was verified in a real session on Claude Code 2.1.304.

## 2026-10-20 · /establish works from the first minute

The previous release told the orchestrator to scaffold the SDLC and run `/establish`, but a
fresh scaffold had no such skill, nothing registered where an assistant looks for skills, and
no copy of the guide the skill follows. The first step failed.

`bootstrap.py sdlc` now writes executable `establish` and `onboard` skills in the open
`SKILL.md` format, copies GATE, BUILDING and every contract into `gate-reference/`, and for
Claude Code registers both skills inside the SDLC itself. `AGENTS.md` tells any other assistant
to offer `establish` while the SDLC is not built. The adapters for assistants other than Claude
Code are now marked as unverified starting points. The explainer video, its script and its
poster are gone: they described an older GATE and added nothing the documents do not say.

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
