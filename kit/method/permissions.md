# Permissions

The base rule does not change: the assistant prepares and the person decides. What changes is
how often the person is asked.

## Never asks here

Local work follows the permission mode the person chose in their assistant: reading, editing,
running tests, building, local commits, and querying the code platform, the tracker or the
production source of truth.

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

Whatever was authorised: production, merges (they need the reviewer's approval in force),
forced pushes or pushes that delete branches, deletions on the code platform or the tracker,
infrastructure tools, generating credentials, and any command that chains an authorised write
with others that are not.

## How it works

`tools/guards/permissions.py` runs before every shell command and every connector call, through
the adapter of the person's assistant. If it fails while deciding, it asks. Authorising does
not exempt anyone from the other rules: check whether something exists before creating it, and
whatever is published remains the responsibility of whoever authorised it.
