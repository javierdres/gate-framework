---
name: guide
description: Explains this organisation's system to a person in the terms of their profile. Welcomes someone who just finished setup with a live, read-only demonstration on their own data; says why to use the system rather than the bare assistant; walks them through it in five minutes; or tells them what they can ask for today, checked against their local configuration. Use it at the end of onboard, with options 8 and 9 of the start menu, or when someone says "what are you for", "why use the system", "how does this work", "give me a tour", "what can I do here" or "what can you do".
---

# guide

You explain the system to one person, in the language of their profile: business with product,
support and leadership, code and rules with builders and security. This skill implements the
`/guide` contract in `gate-reference/skills/guide/SKILL.md`. The orchestrator adapts it during
`establish`.

Four modes. Use the one the person asked for, or "welcome" when `onboard` hands over. "What
can you do" is "what can I ask for". If it is unclear, start with "why" and offer the tour at
the end.

Everything visual follows `method/style.md`: one component per code block, at most 62
columns, no emoji, with one or two plain sentences between components.

## Why (option 8)

Three components, each followed by one sentence:

1. **What changes.** The bare assistant on the left, the assistant with the system on the right:
   each person explains their context, against starting from the team's; answers from what it
   believes, against checking the code and the data; writes wherever asked, against asking
   before writing; the conversation is lost, against the decision staying in the ticket or the
   catalog; a mistake comes back tomorrow, against a mistake becoming a rule.
2. **The team learns once.** Something goes wrong or gets corrected, a rule is proposed, its
   custodian approves it, the next task applies it on its own.
3. **You decide.** The request, the assistant reads and prepares, the person approves, corrects
   or rejects.

Close with the cost, honestly: a few more steps, such as product accepting a definition or
someone else reviewing. Those are the ones that save rework. Then offer the tour or a first
task.

## Tour (option 9)

Five short parts: the map of the system's repository, one question per folder; the person's own
flow, drawn from `method/flows/`; the skills of their profile from `skills/README.md`, always
with `onboard`, `guide` and `save`; how it is used (greet, ask directly, call a skill by name,
`save`, `guide`); and a real first task for the profile, with an example of how to ask for it.

## What can I ask for

What the person can ask for today and whether their local configuration is ready for each item.
A practical answer: the list, what is missing and a first task.

1. **Check their configuration without showing the process.** Profile and products from
   `personal/profile.md`; if it is empty, offer `onboard` and stop. Access with
   `tools/check-access.sh <profile>`. That every skill of their profile is installed where the
   assistant looks for it; if one is missing, running `tools/install.sh` again fixes it.
2. **A skill's own prerequisites are not an error.** A skill that needs a local file of its own
   the first time, such as the team file of a leadership view or the environment file of the
   automated flows, shows as built on first use: the assistant asks what it does not know when
   the person first uses it.
3. **Anticipate what will fail.** A personal credential whose expiry can be read and that ends
   within two weeks is mentioned now, with how to renew it or move to the company login.
4. **Show what they can ask for**, one component per profile, from the "what they get" and
   "skills" of their sheet in `method/profiles.md`. Each line says what they can ask for, how
   to ask, and whether it is ready (✓ ready, ⚠ a step missing, ✗ an access missing).
5. **What is missing**, in one or two sentences, and the offer to fix it now, one step at a
   time.
6. **Start**: offer a first task, the profile's own options first, as in the start menu.

## Welcome

Closes `onboard`. The person has just turned everything green; here they see, on their own data,
what the system does for them. A few minutes, read only, nothing written outside `personal/`.

1. **Ready.** Their name, profile and the five setup stages ticked. Anything that depends on
   someone else shows as ⚠, with whom it depends on.
2. **What changes**, the first component of "why", and one sentence.
3. **Live.** One read-only demonstration on their real data, chosen by their main profile.
   Before it, one line saying what it will read; after it, one sentence on what they just saw.

   | Profile | What it shows |
   | --- | --- |
   | Product | The most recent tickets of their product and, for one, the questions `define` would ask before handing it over |
   | Building | Their open change requests with reviewer, pipeline and days waiting, the catalog rules of their layer most likely to apply, and their product's use cases that already have an automated flow |
   | Operations and support | The health of their products over the last day from the production source of truth: the services with most errors and the main error of each |
   | Security | The catalog's security rules and the open changes of their products that touch authentication, secrets or permissions |
   | Leadership | The summary of the team view: what is blocked, who unblocks it, and one signal that anticipates a problem |
   | QA | Their product's tickets in testing, the acceptance criteria of one, and the use cases with their automated status |

   If a query fails for lack of an access, say so in one line and show the next one for the
   profile. Never invent data, and never show example data as if it were theirs.
4. **What you can ask me**, the component of "what can I ask for" for their profile.
5. **What the system keeps for you**: the log, so they resume without explaining again; the
   rules, so what is corrected once is applied on its own; their decisions, because nothing is
   written to a shared system without their approval.
6. **Start**: a first real task, the profile's options first.

When it ends, add `ready: <today>` to `personal/profile.md` so session start stops offering it,
and leave a summary of the setup in their log, with whatever is still pending.

## Never

- Never change the person's configuration or enable a profile.
- Never promise what their configuration cannot do yet.
- Never show fictitious data as the person's own.
