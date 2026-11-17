# At the start of a session

`AGENTS.md` imports this file rather than linking to it, so it loads in every session. Some
assistants do not follow links, so a linked menu is a menu nobody sees. Skills and
the style guide point here; this is the only copy of the menu.

The session-start guard hands the assistant the GATE version, the setup stage, the verified
identity with its enabled profiles, and what is open in the log. Then:

- **Setup unfinished at requirements or installation**: continue with `/onboard` from there as
  soon as the person writes, even if they bring another request. Without those two stages the
  SDLC does not work, so a request handled first would run without the guards.
- **Setup unfinished from the profile stage on**: follow the rest of this page and offer to
  complete what is pending.
- **Opened inside the SDLC repository** instead of the working folder: ask the person to reopen
  the assistant at the working folder, where their profile, log and guards load.
- **A direct request** is handled straight away, without a menu. The profile still sets the
  language.
- **No profile**: show the profile menu below, inside a code block. Choosing a profile hands
  over to `/onboard`, which saves it and goes on with access.
- **With a profile**: greet with name and profile, and offer the tasks the profile enables.

## Enabled profiles

A person can only use the profiles in their row of `GOVERNANCE.md`. The guard verifies who they
are through their account and tells the assistant which profiles those are. If the guard could
not verify the person, the assistant verifies them through the tracker connector, with the
person's own identity, before showing any menu.

- Menus show only the enabled profiles and tasks. The options that remain keep their numbers,
  so the same number always means the same thing for everyone.
- A profile or task that is not enabled is refused in one line: the orchestrator assigns
  profiles. It is not done.
- If `personal/profile.md` declares a profile that is not enabled, the assistant works with the
  enabled ones only and offers to fix the file with `/onboard`.

## Without a profile

```
  How do you want to work today?

  ── WITHOUT THE SDLC ─────────────────────────────────────
   1   Plain assistant         free session, no flow

  ── I AM ──────────────────────────────────────────────────
   2   Product                 define and refine requests
   3   Builder                 frontend, backend, fullstack or qa
   4   Operations              production and incidents
   5   Security                audit and review changes
   6   Leadership              see the team and decide
   7   Support                 users' cases

  ── I WANT TO KNOW IT ─────────────────────────────────────
   8   What is it for?         why use the SDLC
   9   A guided tour           five minutes

  Type the number of your option.
```

Option 1 is a free session without the flow or a saved profile; the permission rules still
apply. Options 8 and 9 run `/guide`.

## With a profile

Greet the person by name, with their profile, and offer the tasks: product, building, review,
operations and support, leadership, and other, which is always there. Where the assistant has
a question tool that admits four options and adds "other" on its own, show the four tasks that
best fit the profile, the person's own first; with more than one profile, one per profile first.
Whatever is left out is asked for through "other". Without such a tool, a numbered list.

If the person asks what they can do, answer with `/guide` in its "what can I ask for" mode.

## Before starting

The assistant summarises what it understood and waits for confirmation. If an access is missing
for what the person chose, it offers to complete it with `/onboard`. If the request resumes a
topic, it reads the latest summary in the log first. If the person greets without a request,
it mentions in one line what is open in their log, before the menu.
