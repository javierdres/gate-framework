> **English** · [Español](START-HERE.es.md)

# Start here

Three ways into GATE, one per situation. Each one says what you do, where it stops, what you
get, and **what it changes compared with how you do it today**.

If you only read one thing about GATE, read this.

**Before any of these, the organisation's SDLC has to exist.** If it does not yet, you are the
orchestrator and you start in [BUILDING.md](BUILDING.md): `python3 bin/bootstrap.py sdlc`, then
`/establish` on the assistant you chose. Each person then joins with `/onboard`. Everything below
assumes that is done.

---

## A. A new project

### What you do

```
/init
```

Hand over whatever you have: a transcribed voice note, a forwarded email, a conversation with
a stakeholder. The only thing that cannot be missing is **who is asking and what for**.

The first thing `/init` does is read `.gate/config.yml`. On a new project it does not exist, so
it creates it from the template, fills in what it can detect from the repository, and asks for
the eight fields required to start: the organisation, its catalog, where false positives are
recorded, the project id, its repositories, the branch convention, the tracker and where
dossiers live. Nothing else happens until those are answered.

The rest of the config stays empty and that is fine: each field is tagged with the stage that
needs it, and an empty one declares that stage is not in use yet.

Then `/init` classifies it as a new project and opens the dossier. From there the chain runs the
long way, stages 1 to 12.

### Where it stops

Three gates before a single line of code.

**Product gate**, after `/define`. Someone accepts the problem statement. Nothing advances
without a data classification, which decides how deep every later stage goes.

**Requirements gate**, after `/specify`. The acceptance criteria are accepted, and every
non-functional one carries a number. No number, it goes back.

**Engineering and design gates**, after `/refine` and `/design`. Risks get owners. Two
architecture alternatives are contrasted, and someone who did not write the proposal picks one.

### What you get

A dossier that already holds the problem, the criteria, the affected components, the risks with
owners, the test plan, the observability plan, and a decision record naming what was ruled out
and why.

### What changes versus today

Today the need is described in a meeting, a team estimates, work starts, and the context lives
in people's heads. Decisions get taken in chat threads and are gone a month later.

Three concrete gains. **Data classification exists from day one**, so compliance is not
retrofitted when the system already handles personal data. **Non-functional criteria carry
numbers**, so QA has something to verify in stage 8 and production has something to watch in
stage 10; "make it fast" verifies nothing. And **the architecture decision is recorded with its
alternatives**, so in a year nobody has to reconstruct why it was built this way.

What it costs: three approvals before the first line of code.

---

## B. A new requirement on an existing project

### What you do

```
/init
```

Same entry, different classification. `/init` recognises it as a change to something that
exists and takes the **short chain**: it enters at stage 2 or 3 with the system's dossier
already loaded, skipping definition when the problem is already understood.

### Where it stops

One gate before building: the engineering gate, after `/refine`.

If the change carries an architecture decision, the design gate as well. If it does not, stage
4 is skipped.

Then the usual: `/build`, `/self-review` in private, `/review` with another person, `/verify`,
`/deploy`.

### What you get

An impact map drawn by reading the actual code, the risks that change introduces, and the
catalog rules that apply to what you are about to touch.

### What changes versus today

Today a ticket appears in the backlog, someone picks it up, greps around to work out what it
affects, and builds. Impact is guessed from memory of the system.

Three gains. **The impact map is read, not remembered**, and a map drawn from memory is wrong
precisely about the systems that changed most. **The catalog is consulted before choosing a
pattern**, so you stop rediscovering rules the team already agreed on and re-arguing them in
review. And **the pre-review catches in private** what would otherwise be caught by a colleague
in public, which is faster and costs less socially.

What it costs: one approval before building, and writing down an impact map you were carrying
in your head anyway.

---

## C. An incident on an existing project

### What you do

```
/init
```

`/init` classifies it as an incident and takes the operations chain, entering at stage 10.

`/operate` correlates the data sources from the symptom, separates cause from noise, and
grounds every claim in the source that can prove it. If it cannot prove something, it says so
instead of guessing.

### Where it stops

The operations gate: nothing is touched in production, including silencing an alert, without a
person confirming it. Rollback is proposed, never decided, by the assistant.

The fix itself goes through path B, because a fix is a change.

When the incident closes, `/postmortem` rebuilds the timeline **from the sources**, not from
the memory of whoever was on call, and separates the root cause from the contributing factors.

Before an organisation has `/operate` and `/postmortem`, which come in its second phase, the
path is the same by hand: diagnose from the source of truth, filtered by environment, and close
with a postmortem written from the template, kept next to the affected product, with its root
cause handed to `/harvest`.

### What you get

A diagnosis backed by evidence, a postmortem with a traceable timeline, and the root cause fed
into `/harvest`, which turns it into a candidate rule.

### What changes versus today

Today someone notices, several people pile in, it gets fixed, and if there is a postmortem it
is written from memory and nobody rereads it. The same class of failure comes back six months
later.

Two gains, and the second is the whole point. **The timeline is rebuilt from sources**, so the
root cause is the real one and not the most plausible story told the next morning. And **the
root cause becomes a rule that applies to future changes**: that is the only path by which an
incident actually stops repeating, instead of being remembered by whoever was there.

What it costs: the postmortem is not optional, and the harvest runs whether or not anyone feels
like it.

---

## What GATE gains you, in one table

| | How it usually goes | With GATE |
|---|---|---|
| Context between stages | Rebuilt in each handover meeting | Travels in the dossier |
| Impact of a change | Guessed from memory of the system | Read from the code |
| Acceptance criteria | Prose, unverifiable | With numbers, verifiable in QA and in production |
| Architecture decisions | In a chat thread, gone in a month | Recorded with the alternatives ruled out |
| Review | Depends on who reviewed and their day | Two distinct passes, one private and one public |
| A rejected finding | Argued again next month | Recorded with its reason, never raised again |
| An incident | Fixed, and it returns | Root cause becomes a rule that blocks the class |
| Compliance | Retrofitted when it is already expensive | Data classified at stage 1 |
| "Did this work?" | Nobody asks | Stage 11 asks, with data |
| Audit | Nobody can answer | The dossier answers |

---

## What it costs, honestly

**Approvals that were not there.** Three for a new project, one for a change. Each one is a
person reading something already drafted, but it is time that did not exist before.

**Writing down what used to live in heads.** The impact map, the design decision, the risks
with owners. It pays off from the second time you touch the same system, not the first.

**Discipline in the loop.** If `/harvest` does not run, the catalog stays empty and GATE
becomes bureaucracy with no payback. That is why review triggers it instead of a person
remembering to.

---

## The minimum to start tomorrow

You do not need the whole framework. The floor is lower than it looks:

- An orchestrator, and an AI assistant they chose that loads persistent instructions and skills
- Three people who satisfy the [three role incompatibilities](GATE.md#the-three-incompatibilities)
- Personal credentials per person
- A branch convention that links to the ticket
- An empty standards catalog with its format validator, which `bootstrap.py sdlc` writes

With that you can build the SDLC and reach step 3 of [adoption](adoption/README.md), which is
the pre-review, and you are already getting value. Data sources, an exercised rollback and business indicators come
with the later steps.
