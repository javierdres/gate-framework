> **English** · [Español](BUILDING.es.md)

# Building your organisation's SDLC

This guide takes an orchestrator from GATE to a working SDLC of their own: a repository that
holds the organisation's method, its standards catalog, its products, its skills and the way
each person gets in, running on the AI assistant the organisation chose.

It is written for two readers at once. **If you are the orchestrator**, it tells you what you
will decide, what you will be asked, and what you will end up with. **If you are the
assistant**, it is your build specification: `/establish` follows it from top to bottom.

Read [section 2 of GATE.md](GATE.md#2-before-stage-0-the-orchestrator-builds-the-sdlc) first.
It explains why the SDLC is built this way; this guide says how.

---

## 1. How to use this guide

Instructions for the assistant building the SDLC:

- **Do not build anything before the interview in section 5 is finished** and its summary is
  confirmed. Whatever nobody knows is marked "to be defined" and the build carries on; nothing
  is invented.
- Wherever this guide says "the code platform", "the tracker" or "the production source of
  truth", use whatever the organisation actually has. If it has none of one of them, the part
  that depends on it stays out and goes into the plan as pending.
- **Build in layers, in the order of section 10**, and show each layer before starting the
  next. Every file that reaches a shared system follows the permission rule: nothing is
  published without the orchestrator's approval.
- **Write everything in neutral formats** (section 3) and keep whatever is specific to your own
  platform inside the adapter. Another assistant must be able to run this SDLC tomorrow by
  adding its adapter and nothing else.
- When you wire your own platform, **read its current documentation** rather than relying on
  memory. Hook names, configuration paths and file names change between versions.
- Skill names are short and in English. Everything else is in the organisation's language.
- The catalog starts empty, apart from examples marked as such. It fills with what happens to
  this team.
- At the end, run the verification in section 11 and report what passed, what did not and why.

---

## 2. What you end up with

- A repository, `sdlc-<org>`, that every person clones into their own working folder next to
  the repositories of their products. The assistant is opened in that working folder.
- Persistent instructions every session loads, with the rules that always apply.
- A plan with an objective, a review date and what is out of scope.
- Governance by roles, with one table of who holds each role today and one of which profiles
  each person may use, both tied to verifiable identities.
- The method as the organisation runs it: profiles, permissions, the person's log, session
  start, templates.
- An empty standards catalog, by scope, each scope with its false-positive record.
- A folder per pilot product, with its context, its business rules and its catalog of use
  cases.
- Tools: an installer, an access checker, the guards, small API clients and step-by-step access
  guides.
- The skills of the first phase, implemented in the open `SKILL.md` format.
- An adapter for the chosen assistant, and the instructions to add another.
- A final verification with every point green, or named as pending with who it depends on.

---

## 3. Choosing and wiring the assistant

### What the assistant must be able to do

| Capability | Needed for | Without it |
|---|---|---|
| Persistent instructions loaded every session | The rules that always apply | Not viable |
| On-demand skills | One per skill contract | Task instruction files invoked by name. Viable, worse |
| Repository and shell access | Reading code, running checks and tests | Not viable for building roles |
| Hooks before an action and at session start | Permissions, context at start, the log | The platform carries the load (below). Viable, weaker |
| Connectors (Model Context Protocol) | Tracker and observability | API clients in `tools/`. Viable |

When the assistant has no hooks, the SDLC says so in its plan, and compensates on the platform:
the assistant works with credentials that cannot write where it matters, the main branch is
protected, and outward writes go through a script in `tools/` that shows the action and asks.

### The neutral formats

| Piece | Neutral form | Lives in |
|---|---|---|
| Persistent instructions | `AGENTS.md` | Root of the SDLC repository, plus a small one in the working folder |
| Skills | A folder per skill with a `SKILL.md`: a `name`, a `description` that says when to use it in the words a person would say, and plain instructions | `skills/` in the SDLC repository |
| Guards | Scripts that read the intended action as JSON on standard input and answer allow, ask or deny | `tools/guards/` |
| Connectors | Model Context Protocol servers | Declared per assistant in its adapter |
| Configuration | `sdlc.yml`: the organisation, its assistants, its tools, its scopes and the GATE version | Root of the SDLC repository |

### The guard contract

Every guard follows the same contract, whatever assistant calls it.

- **Input**: a JSON object on standard input with, at least, the tool or action the assistant
  wants to run and its arguments. The adapter passes whatever the platform sends; the guard
  reads the common fields and ignores the rest.
- **Output**: a decision. `allow` lets it through, `ask` puts the action in front of the person,
  `deny` stops it with a reason.
- **Failure**: if the guard cannot decide, it answers `ask`. A guard never fails open.
- Where the platform supports a structured answer, the adapter turns the decision into it.
  Where it only understands exit codes, `allow` is exit 0 and `deny` is exit 2 with the reason
  on standard error. Where it has no way to ask, `ask` becomes `deny` with a reason that tells
  the person how to authorise the action and run it again.

`bin/bootstrap.py sdlc` writes a working reference guard, `tools/guards/permissions.py`, with
session-scoped authorisations and the list of actions that are never delegated. It is
conservative: an authorisation covers only a simple command it reads completely, and a write
inside `sh -c`, `eval`, a subshell or a command substitution always asks. It also watches the
assistant's file tools, so not even the authorisations themselves can be written without the
person's confirmation. Its tests, and those of the session start guard, are in
`tools/guards/tests/`.

### The adapters

An adapter is the only part of the SDLC that is specific to an assistant. It does three things:
makes the assistant load `AGENTS.md`, makes it find the skills, and registers the guards on the
right events. The assistant that runs `/establish` writes its own adapter by reading its
platform's current documentation, and the final verification proves it works.

What follows is a starting point for the assistants most organisations ask about. Hook names
and paths change between versions: check them against the version you run, and record that
version in `sdlc.yml`.

| Assistant | Instructions | Skills | Guards |
|---|---|---|---|
| Claude Code | `CLAUDE.md` in the working folder importing `@sdlc-<org>/AGENTS.md` | Linked or copied into `.claude/skills/` | `.claude/settings.json`: `SessionStart`, `UserPromptSubmit`, `PreToolUse` |
| Gemini CLI | `GEMINI.md`, or `AGENTS.md` set as the context file name in settings | Its skills folder, in the same `SKILL.md` format | `.gemini/settings.json`: the before-tool and session events. Hooks may need enabling |
| Kiro | A steering file in `.kiro/steering/` that points to `AGENTS.md` | `.kiro/skills/` | Kiro CLI hooks on pre-tool use and session start; names differ between major versions |
| Codex CLI | Reads `AGENTS.md` natively | Its skills folder, in the same format | Its hook configuration, where the installed version supports it |
| Any other | Whatever file it loads every session, pointing to `AGENTS.md` | Whatever it loads on demand | Its pre-action mechanism, or the platform fallback above |

Only the Claude Code adapter has been verified end to end, and `bin/bootstrap.py` writes it.
It was verified on Claude Code 2.1.304 in a real session: the instructions load through
`CLAUDE.md`, the session start guard's context arrives, `establish` and `onboard` are found, and
the permissions guard stops a push to the default branch even when the shell tool is allowed.
The other rows are starting points taken from each platform's public documentation, not yet
verified on a real installation. If you verify one, contribute it.

People who do not work in a terminal, product most often, use a **chat client** with a project
or workspace: the instructions for their role, the context files they need and a connector to
the tracker. The SDLC keeps that package in `method/chat-client/` and says what to copy where.

An organisation may run several assistants over the same SDLC. Each gets its own folder under
`adapters/`, and the installer wires whichever the person uses.

---

## 4. Decisions only the orchestrator takes

Each one has a default, so nothing blocks the build. All of them can change later by a change
to the SDLC repository.

| Decision | Default |
|---|---|
| Which assistant, or assistants | The one the building roles already use. Record the version |
| Name of the repository | `sdlc-<org>` |
| Code platform, tracker, production source of truth | What the organisation already uses. One source of truth per question |
| How a person is identified | Their account on the code platform. Without platform accounts, an SSH signing key listed in the SDLC. Declared identity only as a last resort, and said so |
| How the main branch is protected | The platform's protected branches and mandatory approvals. Without them, the server-side hook in `tools/server-hooks/` |
| Who holds each role | The orchestrator covers every custodian role that has nobody yet |
| Profiles enabled per person | Building profiles for everyone; product, operations and leadership by name |
| Pilot products | Two or three, where a product owner is willing to take part |
| Rule scopes | Cross-cutting, product, security, operations, plus one per technical layer the team actually has |
| Formulation exit criteria and review date | The four criteria in GATE.md section 2, reviewed four to six weeks after the build |
| Language and writing standard | The organisation's language. Industry terms stay in English when that is how the team says them |
| Where automated flows live | In the SDLC repository, so no product repository has to change during adoption. Product repositories are read only |
| Out of scope | Whatever the orchestrator names in the interview, plus later phases until the first one works |

---

## 5. The interview

Ask a few questions at a time, the most important first. Show each default so the orchestrator
can just confirm it. Close with a summary to confirm before building anything.

**The organisation**

- Short name, used for the repository and in headings.
- What it builds: own products, internal systems, integrations, services for clients.
- Size of the technical and product teams, and whether they work as one team or several.
- Language and variant for documents, and which technical terms the team keeps in English.
- Regulatory context: personal, health or financial data, and any standard it must answer to.

**The assistant**

- Which assistant the building roles will use, and which version.
- Whether product and other non-technical roles will use a chat client, and which one.
- Which connectors are available: tracker, documentation, observability.

**People and roles**

- Who orchestrates, and who holds each role in GATE.md section 7. Who covers a missing role in
  the meantime.
- For each person: their verifiable identity (account on the code platform or the tracker, or
  the SSH signing key they will use) and the profiles enabled for them.
- Whether the code platform has protected branches and change requests. If it does not, the
  SDLC uses the server-side hook and signed commits instead.

**The tools**

| Piece | What to find out |
|---|---|
| Code platform | Which one, which group or organisation, how each person authenticates (company login, SSH, token), and whether it supports protected branches and code owners |
| Tracker | Which one, which projects, whether a connector exists for the assistant, how the team writes a story and its criteria, sprints or continuous flow |
| Production source of truth | The observability platform, how it is queried by API, which environments exist and how they are told apart in the data |
| Pipeline | Where it runs and what it checks today |
| Documentation | Where it lives today, so it is linked and not duplicated |
| Operating systems | So scripts and guides work for everyone |

**The work**

- Main products or systems, the product owner of each and the repositories that make it up. Two
  or three for the pilot are enough.
- Technical layers that make sense as rule scopes (for example frontend, backend, data, mobile,
  infrastructure).
- Test environments that exist, and whether their external integrations have a test mode.
- What should work first, how everyone will know it works, and the review date.
- What the organisation has already decided not to do.

---

## 6. Repository structure

```
<working folder>/
├── AGENTS.md                 written by the installer; points to the SDLC and to personal/
├── <assistant adapter files> written by the installer for the assistant the person uses
├── sdlc-<org>/               the organisation's SDLC repository
│   ├── AGENTS.md             rules for the assistant and the map of the repository
│   ├── sdlc.yml              organisation, assistants, tools, scopes, GATE version
│   ├── allowed_signers       SSH signing keys per person, when identity uses them
│   ├── README.md             what it is, for people, in one page
│   ├── ONBOARDING.md         how to start
│   ├── PLAN.md               what is built now, what comes next, what is out of scope
│   ├── GOVERNANCE.md         roles, who approves what, who holds each role
│   ├── CODEOWNERS            governance translated to the code platform
│   ├── GATE.md               the GATE version implemented and where this SDLC departs
│   ├── gate-reference/       read-only copy of GATE: framework, this guide, contracts
│   ├── method/               cycle, profiles, permissions, log, session start,
│   │   ├── flows/            writing style, one diagram per profile
│   │   ├── chat-client/      the package for roles that work outside the terminal
│   │   └── templates/        dossier, ticket, postmortem, decision record
│   ├── catalog/              written by bin/bootstrap.py, empty of rules
│   │   ├── README.md         rule format, severities and scopes
│   │   ├── scopes.md         each scope and its custodian
│   │   ├── rules/hard/       blocking rules, each with its scope
│   │   ├── rules/soft/       suggestions, each with its scope
│   │   ├── calibration/      false-positives.md, with no approval needed
│   │   ├── bin/              format validator and catalog generator
│   │   └── tests/            the validator and generator, in both directions
│   ├── products/
│   │   ├── README.md         index of products and of their use-case catalogs
│   │   ├── _template/        README.md · business-rules.md · use-cases.md · incidents/
│   │   └── <product>/        context, rules, use cases and their automated flows
│   ├── e2e/                  shared runner for the automated flows
│   ├── tools/
│   │   ├── install.sh        idempotent installer
│   │   ├── check-access.sh   requirements and access per profile
│   │   ├── access-checks.tsv the checks each profile needs
│   │   ├── guards/           permissions, session start, log reminder, with tests
│   │   ├── server-hooks/     for a git server with no protected branches
│   │   ├── clients/          one small API client per system
│   │   └── guides/           step-by-step access guides
│   ├── skills/               one folder per skill, each with its SKILL.md
│   ├── adapters/             one folder per assistant
│   └── personal/             each person's own; ignored by version control
│       ├── profile.md
│       ├── preferences.md
│       ├── grants/           session authorisations, deleted after a few days
│       └── sessions/         the log, with its README.md index
└── <product repositories>/
```

---

## 7. What each base file holds

The templates in [`templates/`](templates/) give the literal starting point for most of them.

**`AGENTS.md` of the repository.** Loaded every session, so it is short. One line with the
purpose and the principle: the assistant prepares, people decide. A pointer to the plan: when
something proposed does not fit it, the assistant says so and offers to record it as out of
scope. The session start, included or referenced. A one-table map: where each thing is, what
question it answers, when to read it. And the rules that always apply: approval before writing
and its levels; verify before asserting; the single source of truth for production; check
before creating; consult the catalog before proposing a pattern; nothing merges without an
approval in force; credentials never in a repository or in the chat; check the repository root
before any destructive version-control operation; when an access is missing, say which and go
on with what can be done; whatever a person runs outside the assistant is given step by step;
write by roles; run the harvest when a review closes; keep the log without being asked; the
writing standard for documents.

**Session start (`method/session-start.md`).** A direct request is handled without a menu. If
setup is unfinished, the start guard says at which stage, and `/onboard` continues from there.
Without a profile, a numbered profile menu inside a code block, with an option to work without
the flow and two to learn about the SDLC. With a profile, a greeting with name and profile, and
the tasks that profile enables: product, building, review, operations and support, leadership,
other. Before starting, the assistant summarises what it understood and waits. If the person
greets without a request, it mentions in one line what is still open in their log.

**Profiles (`method/profiles.md`).** One sheet per profile, answering five questions: what the
person gets, what they configure (with the least privilege and how to obtain it), what data
they work with, which skills they use, and how they know they are ready. It is the single
source: onboarding, the plan and the access checker read from it.

**Permissions (`method/permissions.md`).** Three levels. Local work never asks for more than the
assistant's own permission mode: reading, editing, running tests, local commits, querying
systems. Outward writes ask until a scope is authorised: push, opening a change request,
creating, editing, commenting on or moving tickets; at the first approval in a repository or a
tracker project, the assistant asks whether to authorise it for the rest of the session. Some
actions always ask, whatever was authorised: production, merges, forced pushes or pushes that
delete branches, deletions, generating credentials, and any command that chains an authorised
write with others that are not. The authorisation lives in `personal/grants/`, is registered
through a command that passes the assistant's own confirmation, so it cannot authorise itself,
and expires with the session.

**The log (`method/sessions.md`).** When the assistant writes: a decision, a closed step, a
discard, something critical, a pending item, a pause. One file per topic and start date. A
summary template. An index with "Open" and "By topic". What to do when resuming. What does not
belong there: rules go to the catalog, product context to its folder, whatever changes a task
to its ticket.

**Writing style (`method/style.md`).** For documents meant for people: short sentences, plain
language, written for whoever decides, nothing the reader does not know. For the terminal:
anything visual inside a code block, at most 62 columns, box-drawing characters and simple
symbols (✓ ✗ ⚠ ↺ ▸), no emoji, one component per idea.

**Method (`method/README.md`) and flows.** The fixed line between the assistant and people, the
three incompatibilities, the cycle as the organisation runs it, the three ways in, the dossier,
and the adoption steps with their status. One diagram per profile in `flows/`.

**Governance (`GOVERNANCE.md` and `CODEOWNERS`).** The current phase, formulation or operation,
with its exit criteria. The roles. Which part anyone may change by change request and who
approves it: method and governance by the orchestrator and every custodian; cross-cutting rules
by every custodian; each scope by its custodian; each product by its product owner and the
custodian of the affected layer; tools by operations; skills by the profile they serve; false
positives with no approval at all. How a rule is born and the monthly harvest. The table of who
holds each role today and the table of profiles per person, with their verifiable identity:
the only two tables in the repository with names.

**Catalog (`catalog/`).** Written whole by `bin/bootstrap.py`: the rule format, two severities
(hard rules block, soft rules suggest), the validator, the generated `catalog.json` and the
false-positive record, empty of rules on purpose. Every rule declares its `scope`
(cross-cutting, product, security, operations, or a technical layer) and `scopes.md` names the
custodian of each. A rule starts as a candidate and is reported as a recommendation until its
custodian approves it; a deprecated rule is never deleted and its id is never reused.

**Products (`products/`).** An index of products, the status of their use-case catalogs and
whom to ask per domain. A template with three files: the product's context (what it is, where
the work is, active repositories, whom to ask, by role); its business rules in force, each
validated or pending validation; and its catalog of use cases. A product's folder is created
when someone works on it, not before.

**Plan (`PLAN.md`).** The objective in two sentences, the vision by profile and phase, how
everyone will know it works and the review date, what is done, what comes next in order with an
owner and a closing condition, what is out of scope, and the pending decisions with who decides.

**`GATE.md` of the SDLC.** The GATE commit it implements, and a short map of which stage or
principle each part implements and where it departs from the framework, each departure with its
reason.

**`ONBOARDING.md` and `README.md`.** For people. The README says what it is in one page. The
onboarding says how to start: clone, open the assistant in the repository the first time and
let `/onboard` do the rest. It includes a table of the available skills.

---

## 8. The skills of the SDLC

Each skill is a folder in `skills/` with a `SKILL.md` that implements one contract from
[`skills/`](skills/) in this repository. The description says what it does and when to use it,
in the words a person would say, because that is what the assistant uses to decide whether to
load it. A skill enters the shared SDLC when a whole role uses it in any product, it does not
depend on one person's data or access, and it carries its own documentation.

### Entry skills

**`onboard`** implements the `/onboard` contract in stages, shown as a map: requirements,
installation, profile, access and welcome. Requirements: run the checker and give the exact
command for the person's system for anything missing. Installation: check that the repository
sits inside a working folder, explain what the installer does, run it with approval, and ask to
reopen the assistant in the working folder. Profile: name, profiles (only those enabled for the
verified identity) and products, saved in `personal/profile.md`. Access: explain what the
profile needs and why, then set up each missing access one at a time with its guide, and verify
only that one; prefer company login and connectors over hand-made tokens. Welcome: a live
demonstration on the person's own data, and mark setup as done. Never ask for or accept a
credential in the chat; if one is pasted, ask the person to revoke it.

**`guide`** explains the SDLC: why use it rather than the bare assistant, a five-minute walk
through it for the person's profile, and what that profile can ask for today, checked against
their local configuration.

**`save`** stores something where it belongs. Personal things go to preferences, the log or the
person's own skills. Team things go to the right folder (a rule to the catalog, a discard to its
record, context to its product, a guide or script to tools, a method change to `method/`, a
skill to `skills/`) as a change request from its own branch, saying who approves it. It checks
first whether it already exists.

### Phase one: product and building

**`define`** implements `/define` and `/specify` for a product owner. It does not write the
ticket until the definition is ready; it defines the problem, not the solution. It questions the
request a few points at a time (who asks and why, problem, success criterion with a number,
scope, out of scope, users and permissions, business rules it touches, edge cases, sensitive
data, dependencies, priority), and shows both readings when there are two. It checks what exists:
business rules in force, similar tickets, and the code if there is access. It writes acceptance
criteria as Given, When, Then, one per behaviour. It proposes the use cases the requirement adds
or changes and asks the product owner to validate each one. It shows a "ready for development"
checklist, drafts the ticket in the team's format, creates it only on confirmation, and prepares
the handover. It must also work from a chat client with a tracker connector. When the product
owner works only there, the validated cases live in the ticket, and whoever builds the change
adds them to the product's catalog with that ticket as their origin. In phase one the ticket
also carries the dossier: `method/templates/ticket.md` has a section per stage.

**`self-review`** implements `/self-review`. It never publishes, reviews only what the change
introduced, and gives every finding a file, a line, a rule and a reason; what was discarded is
not raised again. It reads the diff against the base, the layer, the product, the ticket and its
dossier; applies the cross-cutting, layer, security and product rules with their discards
(candidates as recommendations); runs lint, tests and the automated flows the change touches;
sweeps for secrets, personal data in logs and unvalidated input; checks each criterion of the
ticket. "What the change introduced" means the lines it adds or modifies, including an old
problem on a line it modifies; something serious seen in passing on an untouched line, such as a
secret, goes privately to the security custodian instead. It reports in order: what would block,
recommendations, questions for product, and what
has no rule but deserves a look. It offers to fix one at a time and hands rule-less patterns to
`harvest`.

**`e2e`** implements the automated part of `/verify` and the release regression of `/deploy`.
Five modes: gather a product's use cases (proposed until the product owner validates them),
automate a case, run the cases a change touches, add the cases validated in a ticket, and run
every case before a release. It enforces the rules in GATE.md stage 8: an allowlist of hosts
checked before the browser opens, real-world effects cut in the runner unless authorised, the
configuration per person outside the repository, keys never in the chat, local evidence of every
run.

**`harvest`** implements `/harvest`. It runs on its own when the threads of a change request are
resolved, when the reviewer finishes or approves, when the pre-review leaves something without a
rule, and when a postmortem closes. In phase one, when review happens outside the assistant, the
instructions remind whoever closes the review to run it. A candidate drawn from a private
pre-review is raised only if its author chooses, with its origin told as a pattern. It filters
for patterns that will repeat, that do not exist
yet and that were not discarded; drafts each candidate in the catalog format with its origin
told as a pattern; lets the person choose which ones to raise; and publishes one change request
per scope to its custodian. It also prepares the monthly harvest.

### Later phases

`review`, `operate`, `postmortem`, `refine`, `design` and `validate-outcome` are recorded in the
plan as pending and built when phase one works with real people. Until `postmortem` exists,
every incident still closes with a postmortem written from `method/templates/postmortem.md`,
kept in `products/<product>/incidents/`, with its root cause handed to `harvest`. A leadership
view of the team,
reading the tracker and the code platform, is optional and belongs to the third phase; it reads
only, measures everyone with the same yardstick, and treats a number as a place to look, never
as a verdict on a person.

---

## 9. Guards and scripts

| Piece | What it does |
|---|---|
| Installer | Idempotent, with a backup. Creates `personal/` with profile, preferences and log; writes the working folder's `AGENTS.md` without touching what it already has; links the skills where the assistant looks for them, or copies them where links do not work; writes the adapter for the person's assistant. Stops if the repository sits loose in the home folder |
| Session start guard | Brings the main branch up to date, reports the pending setup stage, verifies the identity and hands over the enabled profiles, checks access, detects an outdated installation, and hands over the log path with what is open |
| Per-message guard | A short reminder to update the log when the message moved something forward |
| Permissions guard | Before every watched write, reads the session's authorisations and answers allow or ask. Production, merges and deletions always ask. On any error, asks |
| Access checker | Checks requirements and access for the person's profile and shows them with the status component |
| API clients | One per system (code platform, tracker, observability), without dependencies, reading the credential from the person's home |
| Access guides | One per system, step by step: how to create the credential with the least privilege and an expiry, where to keep it, how to check it works |

Scripts must run on every operating system the team uses. Prefer POSIX shell and the Python
standard library, with no dependencies.

---

## 10. Build order

1. The interview, with its summary confirmed.
2. The skeleton of the repository, with `personal/` ignored by version control. `python3
   bin/bootstrap.py sdlc <path> --assistant <id> --org <short name>` writes it: the structure,
   the base files from the templates, the empty catalog with its validator, the three guards,
   the installer, a copy of GATE in `gate-reference/`, first versions of the `establish` and
   `onboard` skills and, for Claude Code, its adapter with both skills already registered.
   `/establish` fills in and writes the rest.
3. `sdlc.yml`, `GOVERNANCE.md`, `CODEOWNERS` and `PLAN.md`, from the interview.
4. The method: README, profiles, permissions, log, style, session start, flows, templates, and
   the chat-client package if a role needs it.
5. The empty catalog, with its format, its scopes and its false-positive record.
6. The product template and the folders of the pilot products.
7. `AGENTS.md` of the repository, and `GATE.md` with the version and the first departures.
   Create the SDLC repository on the code platform and push it once with its upstream
   (`git push -u origin main`), with the orchestrator's OK.
8. Installer, guards, access checker, API clients and access guides.
9. The adapter for the chosen assistant.
10. The entry skills: `onboard`, `guide` and `save`.
11. The phase one skills: `define`, `self-review`, `harvest`, and `e2e` with its runner.
12. README and ONBOARDING.
13. The final verification. When it closes, write today's date in `built` in `sdlc.yml`.

---

## 11. Final verification

```
  SDLC VERIFICATION
  ──────────────────────────────────────────────────────────
  ○  No file carries credentials or client data
  ○  Only GOVERNANCE.md has names (CODEOWNERS, accounts only)
  ○  personal/ is ignored by version control
  ○  The installer runs twice without duplicating anything
  ○  The assistant loads AGENTS.md in a fresh session
  ○  Opening the assistant in the working folder shows the menu
  ○  The skills are found by the assistant
  ○  onboard leaves the pilot profile's access green
  ○  An outward write asks; after authorising, it does not
  ○  Production and merges ask even when authorised
  ○  A failing guard asks instead of letting through
  ○  The guard and catalog tests pass
  ○  Session start reports identity, profiles and access
  ○  define produces a test ticket ready for development
  ○  self-review reviews a test change against the catalog
  ○  harvest proposes a candidate from a correction
  ○  e2e refuses to run against a host not allowed
  ○  The log writes itself after a decision
  ○  GATE.md names the commit implemented
```

Report each point with ✓ or ✗ and, for every ✗, what is missing and who it depends on. When the
assistant has no hooks, the guard points are replaced by the platform fallback and reported as
such.

---

## 12. Questions that always come up

**Do we need all of this to start?** No. Phase one is product and building: a product owner who
defines and hands over with quality, and a builder who takes it and builds with the team's
rules. Everything else is in the plan and waits.

**Can we use more than one assistant?** Yes. The method, the catalog and the products are
neutral; each assistant gets its adapter. Each person uses whichever the orchestrator enabled,
and the verification runs once per adapter.

**What if our assistant has no hooks?** The SDLC still works, with weaker enforcement. The
assistant gets credentials that cannot write where it matters, the main branch is protected and
outward writes go through a script that asks. The plan says so, so nobody assumes otherwise.

**What if the tracker or the observability platform has no connector?** The API clients in
`tools/clients/` read each person's own credential. They are small on purpose.

**Our git server has no protected branches or merge requests.** Use `tools/server-hooks/`: it
keeps the main branch fast-forward only, requires every commit to be signed by a key listed in
`allowed_signers`, and requires changes to arrive as a merge reviewed by someone else. The same
keys give the SDLC a verifiable identity per person.

**Can we write the formats in our own language?** The documents, yes. The keys the guards and
validators read (the rule frontmatter, `sdlc.yml`, the `<!-- sdlc:open -->` marker of the log)
stay in English, because translating them makes a check fail in silence.

**Can product work without the code platform?** Yes. Through a chat client with the role's
package and a tracker connector, plus a read-only access to the code of their own if the
organisation wants the assistant to read it on their behalf.

**Why do the automated flows live in the SDLC and not in each product?** So that adoption
requires no change in any product repository, and so that the flows describe what product
defined rather than what the code does. An organisation that prefers them in each product can
move them; record it as a departure.

**Why does each person run the flows on their own machine?** Because the configuration of each
environment, users and keys included, belongs to the person and never travels. A shared pipeline
would need it stored there.

**We are three people. Does this still work?** Yes. Three is the viable minimum: one in product
and two builders who alternate review. Roles concentrate; the incompatibilities still hold once
formulation ends.

**Some roles have nobody.** The orchestrator covers them during formulation, and governance says
so. When someone takes a role, one row changes.

**Where do credentials go?** In each person's home, with restricted permissions and an expiry.
Never in a repository, never in the chat, never one shared token.

**How do we move to a new version of GATE?** By a change request to `GATE.md` in the SDLC that
updates the pinned commit and reviews the map of departures. Nothing updates on its own.

**How do we give back what we learned?** Propose it to GATE as a candidate, told as a pattern,
with nothing that belongs to the organisation. See [CONTRIBUTING.md](CONTRIBUTING.md).

**How do we know it is working?** By the formulation exit criteria on their review date. If none
is met, review the approach before building more.
