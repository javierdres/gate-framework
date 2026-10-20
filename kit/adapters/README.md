# Adapters

The only part of this SDLC that is specific to an AI assistant. Everything else is neutral:
instructions in `AGENTS.md`, skills in `skills/<name>/SKILL.md`, guards in `tools/guards/`
that read the intended action as JSON on standard input.

An adapter does three things for its assistant:

1. Makes it load `AGENTS.md` (and the person's profile and preferences) in every session.
2. Makes it find the skills in `skills/`.
3. Registers the guards on the right events: `session_start.py` when a session opens,
   `log_reminder.py` on every message, `permissions.py check` before every shell command and
   every connector call that writes.

Each adapter lives in `adapters/<assistant>/` with an `install.sh` that `tools/install.sh`
calls. Record the assistant and the version it was verified against in `sdlc.yml`, and run the
final verification once per adapter.

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
| Claude Code | `CLAUDE.md` importing `@<sdlc>/AGENTS.md` | `.claude/skills/` | `.claude/settings.json`: `SessionStart`, `UserPromptSubmit`, `PreToolUse`. Automated by `claude-code/install.sh`, verified on 2.1.304 |
| Gemini CLI | `GEMINI.md`, or `AGENTS.md` set as the context file name | Its skills folder | `.gemini/settings.json`, before-tool and session events. Hooks may need enabling |
| Kiro | A steering file in `.kiro/steering/` pointing to `AGENTS.md` | `.kiro/skills/` | Kiro CLI hooks on pre-tool use and session start; names differ between major versions |
| Codex CLI | Reads `AGENTS.md` natively | Its skills folder | Its hook configuration, where the installed version supports it |

## When the assistant has no hooks

The SDLC still works, with weaker enforcement, and `PLAN.md` says so:

- The assistant works with credentials that cannot write where it matters.
- The main branch is protected and nobody merges their own change.
- Outward writes go through a script in `tools/` that shows the action and asks.
