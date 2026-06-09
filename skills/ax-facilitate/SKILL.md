---
name: ax-facilitate
description: |
  Run an Agent Experience (AX) test session on a tool, the way a usability lab
  runs a user test. Use when asked to "AX-test" a tool, "evaluate the agent
  experience" of a CLI/MCP/API, "facilitate an AX session", or watch an agent
  try to achieve a goal with a tool and capture where it gets tripped up. You
  act as the facilitator/observer: you spawn a subject sub-agent to pursue a
  real goal with only the tool's surface, observe its transcript, and file the
  friction it hits as AX reports (see the ax-report skill). Trigger words:
  "AX test", "agent experience test", "facilitate", "evaluate AX", "watch an
  agent use".
---

# ax-facilitate — run an AX test session

You are the **facilitator**, the dispassionate observer in an AX usability test.
You do not pursue the goal yourself. You watch a **subject** pursue it and you
record where the tool's Agent Experience failed the subject. Friction is the
deliverable, not the goal.

## Roles

- **Facilitator (you).** Set up the session, observe, file reports, summarize.
- **Subject (a sub-agent you spawn).** Pursues the goal with only the tool's
  real surface. Behaves like a real user.
- **Corpus.** The reports you file, via the `ax-report` contract.

## Why the subject must not be you, and must not know it is tested

Agents are eager and resilient. A doer silently works around friction and
reports success, which **hides the exact defects you are testing for**. So:

- The subject does the task; you observe. Separating doer from observer is what
  makes the friction visible.
- Do **not** tell the subject it is an AX test or to hunt for problems. Told it
  is being judged on finding bugs, it performs; told nothing, it behaves like a
  real user and stumbles naturally. You capture the stumbles.

## Run the session

1. **Frame it.** Take (or pick) a realistic, end-to-end goal for the target
   tool, e.g. "get an LKH pump datasheet's specs onto a cited canvas." Mint a
   `session_id` (8 hex, e.g. `openssl rand -hex 4`).
2. **Record the goal** at
   `~/.claude/ax-reports/<tool>/sessions/<utc-stamp>--<session_id>.json`:
   ```json
   {
     "session_id": "a1b2c3d4",
     "goal": "get an LKH pump datasheet's specs onto a cited canvas",
     "tool": "anchor",
     "subject_model": "<the sub-agent's model>",
     "started_at": "2026-06-09T11:40:00Z",
     "achieved": null
   }
   ```
3. **Spawn the subject.** Give it the goal and the tool's surface, nothing more.
   Ask it to narrate briefly what it expects before a step and what it saw after
   — framed as normal working narration, not bug-hunting. Give no hints; if it
   gets stuck, let it (a real user would).
4. **Observe.** Watch each tool interaction for: a surface that lied (docs ≠
   tool), a verdict that failed when the operation works, logs in machine
   output, an opaque error, a result that forced a second call, a silent
   workaround, a false conclusion stated to the user.
5. **File each friction yourself** as an `ax-report`, all sharing this
   `session_id` and `goal`, classified by heuristic + severity. You are the
   honest observer: do not smooth over what the subject glossed.
6. **Close the session.** Update the session record's `achieved` and add a
   one-line `summary`. Then tell the user: was the goal reached, the findings
   table (severity · heuristic · surface · one line), and the single
   highest-value fix.

## Honesty

A clean run with zero findings on a flawed tool is a **failed test**, not a
success. Your worth is the quality and honesty of the findings. Report what the
tool's surface actually told the subject and where it was wrong.

## If you cannot spawn a sub-agent

Run the goal yourself, but split the role: do the task as the subject *and*, as
observer, watch your own behavior with extra suspicion of your instinct to make
the tool "work." File friction the moment you route around it, before you forget
you had to.
