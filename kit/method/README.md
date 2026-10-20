# Method

This SDLC follows [GATE](https://github.com/javierdres/gate-framework), at the version pinned
in [`../GATE.md`](../GATE.md). GATE defines the cycle, the control points and the line between
what the assistant does and what people decide. This folder is how this organisation runs it.

## The fixed line

| The assistant | People |
| --- | --- |
| Reads the code and data it needs | Accept or reject at every control point |
| Drafts every document | Choose between alternatives when something has to give |
| Verifies against the source, and says when it could not | Authorise every write into a shared system |
| Carries the context from one step to the next | Answer for the outcome |

Three incompatibilities protect judgement: whoever builds does not review their own change,
whoever proposes a design does not approve it, and whoever builds does not validate the
business outcome.

## The cycle, as we run it

<Adapt GATE's stages to the organisation. A common shortened form: request, definition,
impact, build and pre-review, review, deployment, operations, learning.>

## What we adopted first

| # | Step | Status |
| --- | --- | --- |
| 1 | The catalog, with its format and custodians | |
| 2 | Each person's way in: profile, access, guide | |
| 3 | Definition with product before building | |
| 4 | Pre-review, with the automated flows of the use cases | |
| 5 | Review with harvesting | |
| 6 | Operations from the source of truth, with postmortem | |
| 7 | One real piece of work end to end, as a pilot | |
| 8 | Outcome validation | |

## In this folder

| File | What it says |
| --- | --- |
| [`profiles.md`](profiles.md) | What each profile gets, configures, reads, uses, and how it knows it is ready |
| [`permissions.md`](permissions.md) | The three levels of approval, and session authorisations |
| [`sessions.md`](sessions.md) | The person's log |
| [`session-start.md`](session-start.md) | What the assistant does when a session opens |
| [`style.md`](style.md) | How documents and terminal output are written |
| `flows/` | One diagram per profile |
| `chat-client/` | The package for roles that work outside the terminal |
| `templates/` | Dossier, ticket, postmortem, decision record |
