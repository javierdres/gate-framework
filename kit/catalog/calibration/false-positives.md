# Known false positives

Findings that review raised and the team rejected, with the reason. The review skills read this
file before raising anything, so they do not raise the same thing again. Recording one needs no
approval: whoever rejects a finding writes the reason.

The rejection usually happens in a product repository and this record lives in the SDLC, so the
entry goes as its own small change to the SDLC, linked from the review thread where the finding
was rejected.

## Format

Each entry is a level-two heading with the next free id, followed by five lines. The next free
id is the highest `FP-` number below, plus one:

```bash
grep -Eo '^## FP-[0-9]{4}' calibration/false-positives.md | sort | tail -1
```

Example, with letters instead of digits so it never counts as an entry:

```markdown
## FP-NNNN · Short title

- What review raises: the claim the assistant makes.
- Why it does not apply: the reason, in one sentence that will still serve next time.
- How to avoid it: what to check before raising it.
- Origin: a link to the review thread where it was rejected.
- Recorded: YYYY-MM-DD
```

Numbers are never reused. Newest entries go first, right below this line.

---
