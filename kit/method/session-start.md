# At the start of a session

The session-start guard hands the assistant the GATE version, the setup stage, the profile and
what is open in the log. Then:

- **A direct request** is handled straight away, without a menu.
- **Setup unfinished**: continue with `/onboard` from the stage the guard reported.
- **No profile**: show the profile menu below, inside a code block.
- **With a profile**: greet with name and profile, and offer the tasks the profile enables.

```
  How do you want to work today?

  ── WITHOUT THE SDLC ─────────────────────────────────────
   1   Plain assistant         free session, no flow

  ── I AM ──────────────────────────────────────────────────
   2   Product                 define and refine requests
   3   Builder                 frontend, backend or fullstack
   4   Operations              production and incidents
   5   Security                audit and review changes
   6   Leadership              see the team and decide
   7   Support                 users' cases

  ── I WANT TO KNOW IT ─────────────────────────────────────
   8   What is it for?         why use the SDLC
   9   A guided tour           five minutes

  Type the number of your option.
```

Only the profiles enabled for the person's verified identity are shown. Before starting any
task, the assistant summarises what it understood and waits for confirmation. If the person
greets without a request, it mentions in one line what is open in their log.
