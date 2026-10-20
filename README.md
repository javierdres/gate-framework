> **English** · [Español](README.es.md)

# GATE

**Governed, Assisted, Traceable Engineering.** The foundation an orchestrator uses to build
their own organisation's AI-assisted SDLC: the stages of the software life cycle, their inputs
and outputs, the human control points, the actors of each one, and how to turn all of it into
a working SDLC project of your own, on the AI assistant you choose.

Agnostic of company, domain, language, platform and AI assistant.

Assistance that stops where judgement begins.

## What GATE gives you

GATE is the theory and the foundation. Your organisation's SDLC is the house built on it: a
repository with your method, your standards catalog, your products, your skills, your
governance and the way each person gets in.

Someone has to build that house. GATE calls them the **orchestrator**, and gives them
everything needed to do it: the framework, a build guide written for a person and for an AI
assistant at once, a scaffold, neutral guards that enforce the permissions, and the skill
contracts to implement.

It works with Claude Code, Gemini CLI, Kiro, Codex or any assistant that loads persistent
instructions, uses skills and can work in a repository. The orchestrator chooses; the SDLC is
written in neutral formats and a thin adapter wires it to that assistant.

## Getting started: build your SDLC

```
python3 bin/bootstrap.py sdlc ../sdlc-<org> --assistant claude-code --org <org>
```

That writes the skeleton of your organisation's SDLC: the base files, the empty standards
catalog with its validator, the permission, session and log guards, the installer and the
adapter. Open your assistant inside it and run `/establish`: it interviews you, builds every
layer following [BUILDING.md](BUILDING.md), and closes with a verification you can read point
by point.

`--assistant` takes `claude-code`, `gemini-cli`, `kiro`, `codex` or `other`. Claude Code has a
verified adapter and finds `/establish` as soon as it opens the folder. For the rest, ask the
assistant to read `AGENTS.md` and run `skills/establish/SKILL.md`; it writes its own adapter
from its platform's current documentation. Those adapters are not verified yet.

## Where to start reading

**[BUILDING.md](BUILDING.md)** if you are the orchestrator. It says what you will decide, what
you will be asked and what you will end up with.

**[START-HERE.md](START-HERE.md)** once the SDLC exists. It answers the questions that come
next: how to start a new project, a new requirement on an existing one, and how to resolve an
incident.

## The reference

[GATE.md](GATE.md) is the full document. If you have ten minutes, read section 2 (the
orchestrator and how the SDLC gets built), section 3 (the single entry point and the dossier)
and section 7 (the actors, and the line between what the AI does and what people do).

## What is here

```
├── BUILDING.md         How an orchestrator builds the organisation's SDLC, on any assistant
├── START-HERE.md       The three ways into the cycle, and what each one changes
├── GATE.md             The full framework
├── CONTRIBUTING.md     How the framework itself changes
├── CHANGELOG.md        What changed, and why
├── skills/             The 18 skill contracts: 2 foundation, 14 cycle, 2 cross-cutting
├── templates/          SDLC config, instructions, governance, plan, product, use cases,
│                       dossier, decision record, QA script, postmortem, rule, log
├── kit/                What bootstrap.py copies into a new SDLC: guards, installer,
│                       adapters, method
├── adoption/           How to roll it out, step by step
├── bin/
│   ├── bootstrap.py    Scaffolds the organisation's SDLC, a catalog, or a project's config
│   ├── validate.py     Checks the contracts are complete and the chain closes
│   ├── check_config.py Reports what a project's .gate/config.yml is missing
│   └── build_pdf.py    Regenerates the PDF from the Markdown
└── docs/
    └── GATE.pdf        The document as PDF
```

## What is deliberately not here

**Your organisation's rules.** The catalog belongs to each organisation and lives in its own
SDLC. This framework defines how it is fed, not what it says. See
[section 8](GATE.md#8-scopes-one-framework-many-contexts) for how the levels fit together.

**Ceremonies, cadence or estimation.** GATE describes the journey of a piece of work and who
clears each step. Scrum, Kanban or whatever you use to organise the team keeps working on top.

**A dependency on one AI vendor.** Instructions, skills and guards are written once in neutral
formats. What is specific to an assistant lives in its adapter.

## The skills

Two foundation skills, fourteen cycle skills and two cross-cutting ones. Each declares in its
frontmatter who triggers it, what it triggers, which gate it has, who owns that gate, what it
writes outside and what it consults.

```
python3 bin/validate.py
```

Checks that every contract is complete and that the chain closes both ways: if A says it
triggers B, B has to say it is triggered by A.

## The moments of human invocation

Before the cycle, once each: `/establish` when an organisation builds its SDLC, and `/onboard`
when a person joins it. In the cycle: `/init` when the need is born, `/build` when someone sits
down to implement, `/review` when someone reviews, several times, `/verify` when someone tests,
and `/deploy` when someone deploys.

The framework chains everything else. Mechanisms that depend on a person remembering to invoke
them do not happen.

## Where it comes from

GATE is not a literature review. It comes from leading development teams and watching the same
four problems repeat: quality depending on who used the assistant that day, decisions
evaporating between conversations, security arriving late, and nobody able to answer which
standard was applied to a change.

Every rule in this framework answers something that went wrong in practice. The gates exist
because automation once executed more than it should have. The three role incompatibilities
exist because a small team with strong assistance converges fast, and sometimes in the wrong
direction. Stage 12 exists because it is easy to find an empty standards catalog next to a
change carrying a hundred and fifty discussion comments. And section 2 exists because GATE was
put into practice in a real organisation, and building that SDLC taught what a foundation has
to give an orchestrator.

It is a living framework, in use and under continuous improvement.

## Author and licence

Author and rights holder: **Javier Núñez**.

| What | Licence |
|---|---|
| Documentation: `GATE.md`, `BUILDING.md`, `README.md`, `skills/`, `templates/`, `adoption/`, `docs/` | [CC BY 4.0](LICENSE-DOCS) |
| Code: `bin/`, `kit/` | [MIT](LICENSE) |

You may use GATE in your organisation, adapt it and redistribute it, including commercially.
All that is asked is attribution.

### About the name

The licence covers the work, not the name. If you adapt GATE for your organisation, use it
freely. If you publish a derivative with substantial changes to the stages, the gates or the
split between what the AI does and what people do, give it another name and mention where it
came from: that way "GATE" keeps meaning one thing.
