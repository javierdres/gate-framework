# Kiro adapter

Lets the system run in Kiro with the same instructions, skills and guards as any other assistant.
Nothing is copied: everything points at the system's repository, so each update reaches Kiro too.

**Verified against:** to verify. It comes from Kiro's public documentation (steering, hooks and
skills) and has not been run on a real installation yet. Record the version in `sdlc.yml` once
the final verification passes on it.

## What the installer leaves in the working folder

`bash <system>/tools/install.sh kiro`:

| In the working folder | From | What for |
| --- | --- | --- |
| `.kiro/steering/sdlc.md` | `steering.md` | Loads `AGENTS.md`, the profile and the preferences in every session |
| `.kiro/skills/<skill>` | `skills/` | The same skills, linked (copied where links fail) |
| `.kiro/hooks/sdlc.json` | `hooks.json` | Session start, the per-message guard and the permissions guard |

The steering and hooks files are the system's own and are rewritten on every install: the
person's own go in other files. Connectors (Model Context Protocol servers) are not written by
the adapter: the organisation declares its own in `.kiro/settings/mcp.json`.

## What differs from an assistant that can ask

Kiro's hooks can only let an action through or block it. The permissions guard runs with
`--format exit`: what would ask is blocked, and the assistant shows the person what it is about
to do and asks them to answer "ok". The per-message guard (`log_reminder.py --passes`) records
that OK, and the next watched write uses it: one OK, one action, for fifteen minutes. Writing
the authorisations directly, or recording an OK on the person's behalf, is always blocked.

There is no usage status line.

## To verify on a real installation

- The event names `SessionStart`, `UserPromptSubmit` and `PreToolUse`, and that each hook
  receives the session id on standard input.
- That the per-message hook receives the person's message (in its input or in `USER_PROMPT`).
- That Kiro follows the skill links in `.kiro/skills/`.
- How Kiro is recognised from its environment (`sdlc_assistant` in `tools/lib.sh`); if it is
  not, name it: `tools/install.sh kiro`.
- On Windows, that the hooks run in Git Bash.

`tools/adapters_check.py` checks that `hooks.json` registers every guard on its event.
