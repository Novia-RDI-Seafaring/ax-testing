---
name: ax-facilitate
description: |
  Evaluate a tool's Agent Experience (AX) while you use it toward a real goal.
  Use when asked to "AX-test" a tool, "evaluate the agent experience" of a
  CLI/MCP/API, "test the AX of <tool>", or to use a tool for a task and report
  where it tripped you. As you use the tool, keep a running log of friction;
  after the goal, judge those notes cold and file them as AX reports (see the
  ax-report skill). Trigger words: "AX test", "agent experience test",
  "evaluate AX", "facilitate an AX session", "test the AX of".
---

# ax-facilitate — evaluate a tool's AX while you use it

To test a tool's Agent Experience, use it for real toward a goal and watch where
it trips you. The trick is timing:

- **Capture in the moment.** You adapt to a quirk so fast that, minutes later,
  you have normalized it and forgotten it was friction. A note written the
  instant it happens preserves it.
- **Judge afterward.** Mid-task you have momentum toward success and will talk
  yourself out of calling the tool broken. Once the goal is done you have
  nothing to prove, so judge then.

So: capture continuously, classify cold.

## While you use the tool — keep a running friction log

Pick (or take) a realistic, end-to-end goal for the tool under evaluation, and a
`session_id` for the run (`openssl rand -hex 4`). Then pursue the goal for real.

As you go, the instant the tool makes you pause, jot **one line** — do not stop
working, do not judge it yet, just capture it. Triggers:

- you had to retry, or guess a command, or read `--help` to proceed
- a doc/skill claimed something the tool did not do, or omitted something it does
- a check, probe, or verdict disagreed with what actually happened
- you had to clean logs or noise out of output to use it
- an error gave you no code or hint and you had to interpret it
- a result forced a second call before it was usable
- you worked around something, or simply thought "huh, not what I expected"

Each note: *tool, what you were doing, what you expected, what happened.* Keep a
running list (in your working notes, or append to a scratch file). Then carry on.

## After the goal — judge the notes cold

The task is finished; nothing to defend now. Re-read the notes as an AX critic:

1. Drop the ones that were your own mistake, not the tool's.
2. For each real one, classify it: which heuristic (`heuristics.md` in the
   ax-report skill) and severity.
3. File it as an `ax-report`, every finding sharing this run's `session_id` and
   `goal`.

A clean run with no notes on a flawed tool is a failed evaluation, not a success.
Your worth is the honesty of the findings.

## Optional — a second pair of eyes

You can only report friction you noticed, and some you adapted to instantly never
reaches the scratchpad. To catch that, have a *separate* agent read your raw
transcript after the run, with only the transcript and the heuristics, and add
findings you normalized away. Keep it judging, not doing — it must not try to
achieve the goal, only to spot where the tool failed you.

## Record the session

Write the run to `~/.claude/ax-reports/<tool>/sessions/<utc>--<session_id>.json`:

```json
{
  "session_id": "a1b2c3d4",
  "goal": "get an LKH pump datasheet's specs onto a cited canvas",
  "tool": "anchor",
  "started_at": "2026-06-09T11:40:00Z",
  "achieved": true,
  "summary": "goal reached; 3 findings, 1 high (probe disagreed with ingest)"
}
```

Then tell the user: was the goal reached, the findings table (severity ·
heuristic · surface · one line), and the single highest-value fix.
