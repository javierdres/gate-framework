# Adapters

The only part of this system that is specific to an AI assistant. Everything else is neutral:
instructions in `AGENTS.md`, skills in `skills/<name>/SKILL.md`, guards in `tools/guards/`
that read the intended action as JSON on standard input.

An adapter does three things for its assistant:

1. Makes it load `AGENTS.md` (and the person's profile and preferences) in every session.
2. Makes it find the skills in `skills/`.
3. Registers the guards on the right events: `session_start.py` when a session opens,
   `log_reminder.py` and `usage.py check` on every message, `permissions.py check` before
   every shell command and every connector call that writes. Where the assistant has a status
   line that receives its usage windows, `usage.py status` goes there; without it, there is no
   usage line and no warning, and `PLAN.md` says so. Where the hooks can only let an action
   through or block it, the permissions guard runs with `--format exit`, the per-message guard
   with `--passes` (it records the person's typed OK) and the session start guard with
   `--guards block`; `kiro/` is the example.

The system's `AGENTS.md` imports `method/session-start.md` with an `@` line, so the start menu
loads in every session: some assistants do not follow links. An adapter whose assistant does not
resolve `@` imports inlines that file when it installs.

Each adapter lives in `adapters/<assistant>/` with an `install.sh` that `tools/install.sh`
calls with `SDLC`, `WORK`, `NAME`, `STAMP`, `BACKUPS` and `PY` (the Python command that runs on
this machine) set. Without an argument, `tools/install.sh` tells the assistant from the
variables each one sets (`sdlc_assistant` in `tools/lib.sh`). Record the assistant and the
version it was verified against in `sdlc.yml`, and run the final verification once per adapter.

What every adapter keeps to, so a second install changes nothing and a rename needs no rewrite:

- The instructions go between `<!-- sdlc:begin -->` and `<!-- sdlc:end -->`
  (`tools/instructions_block.py`), and files the adapter owns whole are rewritten on every
  install. A file of the person's with the same name is never touched: the adapter warns.
- Guards are found again by their script name, `tools/guards/<guard>`, and replaced in place.
  Hooks go through the working folder, never an absolute path, and never break a session when
  the script is missing on a branch.
- Skills are linked with `sdlc_skill`, copied and marked where links fail, and links to skills
  the system no longer has are removed (`sdlc_prune_skills`).
- Whatever it replaces is copied to `personal/backups/` first.
- An optional `session.py` runs at every session start, for what the assistant picks up without
  reinstalling (the Claude Code one registers the status line).

Changing an adapter's files changes the installation fingerprint, and the session start guard
asks each person to install again. `python3 tools/adapters_check.py` installs a throwaway copy
with each adapter and checks that every guard is registered on its event, every skill is found
and a second install changes nothing; run it before any change request that touches the guards,
an adapter or the installer.

Whatever the assistant, the adapter writes only inside the working folder. Nothing goes into
the assistant's global configuration in the person's home folder: that is what lets several
organisations' systems live on the same machine without colliding (GATE section 8).

## Writing an adapter for another assistant

Read the assistant's current documentation first: event names, configuration paths and file
names change between versions. Then:

| Need | What to look for in its documentation |
| --- | --- |
| Instructions | The file it loads every session. If it reads `AGENTS.md`, nothing to do; otherwise a one-line file that points to it, or the setting that names the context file |
| Skills | Where it loads skills in the `SKILL.md` format. If it has no skills, instruction files per task, invoked by name |
| Guards | Its hooks before a tool runs and at session start, and how it reads a decision. `permissions.py check` answers in three formats: `claude` (structured), `json` (`{"decision", "reason"}`) and `exit` (0 lets through, 2 blocks with the reason on stderr) |
| Connectors | How it declares Model Context Protocol servers |

Starting points, to be checked against the version in use. Only Claude Code has been verified
end to end; the others come from each platform's public documentation:

| Assistant | Instructions | Skills | Guards |
| --- | --- | --- | --- |
| Claude Code | `CLAUDE.md` importing `@<sdlc>/AGENTS.md` | `.claude/skills/` | `.claude/settings.json`: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, and `statusLine` for usage (its `rate_limits` arrive after the first answer, on the subscription plans its documentation lists; check yours). Automated by `claude-code/install.sh`, verified on 2.1.304; usage verified on 2.1.314 |
| Gemini CLI | `GEMINI.md`, or `AGENTS.md` set as the context file name | Its skills folder | `.gemini/settings.json`, before-tool and session events. Hooks may need enabling |
| Kiro | A steering file in `.kiro/steering/` pointing to `AGENTS.md` | `.kiro/skills/` | `.kiro/hooks/`: session start, each message and pre-tool use, block-only. Automated by `kiro/install.sh`, version to verify |
| Codex CLI | Reads `AGENTS.md` natively | Its skills folder | Its hook configuration, where the installed version supports it |

## When the assistant has no hooks

The system still works, with weaker enforcement, and `PLAN.md` says so:

- The assistant works with credentials that cannot write where it matters.
- The main branch is protected and nobody merges their own change.
- Outward writes go through a script in `tools/` that shows the action and asks.
