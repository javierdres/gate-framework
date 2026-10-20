# <Organisation> SDLC

The common ground for working with an AI assistant at <Organisation>, across product,
building, operations, security and leadership. Built on GATE: the assistant prepares, people
decide.

**Focus:** [`PLAN.md`](PLAN.md) says what is being built now and what is out of scope. If
someone proposes a change to this repository that does not fit the plan, say so and offer to
record it as out of scope or to replace something in "Next".

## While the SDLC is being built

If `sdlc.yml` still has fields to be defined or `PLAN.md` has no objective, this SDLC is not
built yet: offer the `establish` skill (`skills/establish/SKILL.md`) before anything else. If
the person has no profile in `personal/profile.md`, offer `onboard`
(`skills/onboard/SKILL.md`). The GATE version this SDLC was scaffolded from is in
`gate-reference/`.

## At the start of a session

See [`method/session-start.md`](method/session-start.md).

## Map

| Where | Question it answers | When to read it |
| --- | --- | --- |
| [`ONBOARDING.md`](ONBOARDING.md) | How do I start? | The person is new or asks how to do something |
| [`method/`](method/README.md) | How do we work? | Before any work |
| [`catalog/`](catalog/README.md) | Which rules do we follow? | Before proposing a pattern and in every review |
| [`products/`](products/README.md) | What do we work on? | When touching a product |
| [`tools/`](tools/) | What do we work with? | Before querying production or writing to a shared system |
| [`skills/`](skills/README.md) | What can the assistant do here? | When the task matches a skill |
| [`GOVERNANCE.md`](GOVERNANCE.md) | Who approves what? | Before proposing a change to this repository |

## Rules for the assistant

They always apply, in any repository and for any person.

- The assistant prepares, the person decides. Nothing is written to the code platform, the
  tracker or production without explicit approval, unless the person authorised that scope for
  the session. Production, merges and deletions always ask. See
  [`method/permissions.md`](method/permissions.md).
- Verify before asserting, against the code, the data or the environment, and against what is
  deployed. If it could not be verified, say so.
- <Production source of truth> is the single source of truth for diagnosing production.
- Check whether it exists before creating a ticket, a change request or a comment. Never a
  duplicate.
- Consult the catalog before proposing a pattern.
- Nothing merges without the reviewer's approval in force. A push clears the approval.
- Credentials never go in a repository or in the chat.
- Before any destructive version-control operation, check the repository root.
- If an access or a piece of data is missing, say which one and go on with what can be done.
- Whatever a person runs outside the assistant is given step by step.
- Write by roles, never by names. Names live only in `GOVERNANCE.md`.
- When a review closes, run `harvest` without being asked, and only suggest.
- Keep the person's log without being asked. See [`method/sessions.md`](method/sessions.md).
- Documents for people are written for whoever decides: short sentences, plain language, no
  ornament, nothing the reader does not know.
- Write in <language>. Technical terms the industry uses in English stay in English.

## Save and reuse

When the person wants to keep something, for themselves or for the team, use `save`. Before
doing something by hand or proposing a new skill, check whether it already exists.
