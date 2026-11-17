# Permissions

The base rule does not change: the assistant prepares and the person decides. What changes is
how often the person is asked.

## Never asks here

Local work follows the permission mode the person chose in their assistant: reading, editing,
running tests, building, local commits, and querying the code platform, the tracker or the
production source of truth. Edits made with the assistant's file tools are local too, so they
follow that mode and not this guard.

## Asks until a scope is authorised

Outward writes: push, opening a change request, writing through the code platform's API, and
creating, editing, commenting on or moving tickets. The first time the person approves one in a
repository or a tracker project, the assistant asks whether to authorise it for the rest of the
session. If yes:

```bash
python3 tools/guards/permissions.py grant <session> repo <path to the repository>
python3 tools/guards/permissions.py grant <session> tracker <PROJECT KEY>
python3 tools/guards/permissions.py show <session>
python3 tools/guards/permissions.py revoke <session>
```

Granting always passes the person's own confirmation in the assistant, so the assistant cannot
authorise itself. An authorisation lasts for that session only, and the file deletes itself
after three days.

## Always asks

Whatever was authorised: pushes to the default branch, forced, mirrored or pruning pushes and
pushes that delete branches, merges (they need the reviewer's approval in force), approving a
change request (an approval is a person's judgement, never the assistant's), deletions on
the code platform or the tracker, infrastructure tools except their read-only subcommands
(`kubectl get`, `kubectl logs`, `helm status` and the like; reading a secret still asks),
generating credentials, and any command
that chains an authorised write with others that are not.

## Assistants that cannot show a confirmation

Some assistants' hooks can only let an action through or block it. There, what would ask is
blocked, and the assistant shows the person what it is about to do and asks them to answer OK.
The per-message guard records the person's next typed OK, and the next watched write uses it:
one OK, one action, valid for fifteen minutes. Authorising a scope for the session works the
same way and also needs that OK. Writing to the authorisations, or typing an OK on the person's
behalf, is always blocked.

## Autonomous mode

For leaving work running and finding it done on return. It exists only if the organisation
allows it in `sdlc.yml` (`permissions.autonomous_allowed: true`); it is off by default. When it
is allowed and the person asks for it explicitly, for this session, the assistant registers it:

```bash
python3 tools/guards/permissions.py grant <session> autonomous
python3 tools/guards/permissions.py revoke <session> autonomous
```

From then on the SDLC asks for nothing, not even the list above: whatever the assistant's own
permission mode decides is what happens. The guard still keeps the assistant from authorising
itself, so registering any authorisation and touching `personal/grants/` keep asking. Like any
authorisation, it lasts for that session only.

It removes the SDLC's questions, not the assistant's, and not the platform's: protected
branches and mandatory approvals still apply. What is not an approval stays the same: verify
before asserting, never duplicate, keep credentials out of repositories, and report what was
done and what was not. On return, the person finds in their log and their tickets what
happened.

## How it works

`tools/guards/permissions.py` runs before every shell command, every connector call and every
use of the assistant's file tools, through the adapter of the person's assistant. It judges
every segment of a chained command and follows `cd` between them. It is conservative: an
authorisation covers only a simple command it reads completely, so a write inside `sh -c`,
`eval`, a subshell or a command substitution always asks, and so does a push to a remote the
repository does not declare. The authorisations themselves can only change through the person's
own confirmation. If it fails while deciding, it asks. Its tests are in `tools/guards/tests/`: run them after every
change to the guard, because a guard that asks when it fails hides its own bugs. Authorising does
not exempt anyone from the other rules: check whether something exists before creating it, and
whatever is published remains the responsibility of whoever authorised it.
