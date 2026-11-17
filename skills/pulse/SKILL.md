---
skill: pulse
stage: support
name: The team's pulse, for leadership
triggered_by: [person]
triggers: []
gate: none
gate_owner: —
writes_outside: []
consults: []
---

# /pulse — The team's pulse, for leadership

Optional. It belongs to the third phase, once product and building work with real people.

## Purpose

Let whoever leads see the team's work without asking anyone for a report: what each person is
on, what is blocked and who unblocks it, how work flows, what was delivered, whether the team
can carry its work when someone is away, and whether the SDLC changed the work at all. It also
gives any member a private view of their own work.

## Preconditions

Read access to the tracker and the code platform with the leader's own identity. The team's
scope (tracker projects, code platform groups, people) in a local file of the leader's, ignored
by version control. For the health view, the team's critical functions, declared by the leader.

## What it does

- **Reads, never writes.** It comments on nothing, reassigns nothing and moves no ticket. When
  the leader wants to act, it drafts the message or the change and the leader sends or approves
  it, one action at a time.
- **Closed tickets never measure a person.** A bulk close at release time, one ticket per entry
  or a board nobody updates moves that number more than the work does. The tracker shows the
  team's flow. A question about who produces more is answered with the same-yardstick view
  below, never with a ticket count and never with a refusal.
- **One yardstick for everyone**, on four dimensions read from the code platform: what the
  person wrote, on how many days, what they took to production, and what they reviewed for
  others. No single one is enough: whoever integrates or deploys writes little code, and whoever
  reviews a lot closes less. A yardstick that leaves someone out, such as counting change
  requests for a person who pushes directly, is never presented as a verdict.
- **A number says where to look, not who to blame.** Twelve days in review may be an overloaded
  reviewer, a badly defined ticket or a status nobody updated. It says so.
- **Advice is one concrete action tied to a data point.** Few of them, each anchored to what was
  read, never a sermon.
- **Odd numbers are checked at the source** before they reach a report: it opens the ticket or
  the change behind them. A month with twice the usual volume is usually a board clean-up or an
  import, not a great month.
- **Missing data is a gap, not a zero.** What could not be read is reported with the source that
  failed. Someone who barely appears may work on something these sources do not see.
- **Health.** The leader declares the critical functions, each with its holder and its backup.
  The view shows the functions with no backup or a conditional one, the coverage chains (who
  ends up carrying what when a backup steps in, and backups already holding twice the median
  load), and the problems that persist across saved readings, with the first reading and
  today's. Risk is described in the situation, never in the person.
- **The effect of the SDLC**, read month by month against the rules in GATE.md section 11.
  Only shared work, aggregated by domain.
- **Your own view**, for any member who asks how they are doing: their work in progress, what
  waits on someone else, their changes waiting for review, and at most three things to adjust.
  Private, in a colleague's tone, with no comparison with anyone.
- **A version for management** names roles, not people: load and waiting times without names,
  and what has to be decided. Short sentences, no metric cards.
- Saves each team reading locally, so the next one says what changed and the view can
  anticipate a trend instead of only showing the day.

## What it does NOT do

- Never labels a person as a flight, burnout or low-performance risk. That cannot be inferred
  from these data, and such a label works against exactly the person who carries the most. If
  something suggests one person is worn out, it suggests the leader talk to them in private,
  and it stays out of the view.
- Never shows after-hours work by person; only for the team.
- Never records or reads how people use the assistant, and never measures the SDLC's effect by
  person.
- Never stores verdicts or readings about people in a shared repository. Readings stay in the
  leader's personal folder, and the personal view is not saved.
- Does not replace a conversation. It prepares it.

## Gate

None. It reads and advises; the leader decides what to do and whom to talk to.

## Dossier

**Reads:** The tracker and the code platform, the leader's team file and their saved readings,
and the leader's log for the health view.

**Writes:** Nothing shared. Its readings go to the leader's personal folder.
