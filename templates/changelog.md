# Changes to <system>

What each version of <system> brings, why it was made and what someone who already has it
installed has to do. Newest first. Every change request that changes <system> adds its entry
here, under a new version.

The format is read by the session start guard, so keep it: each version is a `## X.Y.Z · date`
heading, and each entry ends with **What to do.** When an update brings new versions, the
assistant reads their entries and tells each person, in one or two lines, what changed and what
they have to do. "Nothing" is a valid answer; "run the installer again" is the usual one when a
version adds a skill, a guard or an adapter change, and the session start guard offers it too.

Versions: a new rule, guide or wording is a patch (1.0.1); a new skill, guard or flow is a minor
version (1.1.0); a change that asks every person to do something different is a major one.

## 0.1.0 · <YYYY-MM-DD>

### <system> is scaffolded for <Organisation>

Scaffolded from GATE `<gate version>`, with the guards, the installer and the first versions of
the `establish` and `onboard` skills. The orchestrator builds the rest with `/establish`.

**What to do.** Nothing yet: the orchestrator tells everyone when <system> is ready to install.
