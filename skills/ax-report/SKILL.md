---
name: ax-report
description: |
  File a structured Agent Experience (AX) friction report when a tool you are
  using trips you up. Use this the moment a tool's contract does not match
  reality — its docs/skill claim a capability that is missing or named
  differently, a command mixes logs into machine output, a check or probe
  reports failure when the real operation works, an error is an opaque
  traceback instead of a structured message, or a result forces a needless
  second call. Report observed friction with evidence (what you expected, what
  happened, what you did instead), not wishes. Also files lower-priority feature
  requests, kept clearly separate. Reports are written locally for a human to
  triage. Default to filing the moment friction happens; for a deliberate
  evaluation of a tool, see "Running an evaluation session" below. Trigger
  words: "AX", "agent experience", "this tool tripped me up", "the docs were
  wrong", "report friction", "file an AX report", "AX-test this tool",
  "evaluate the agent experience".
---

# ax-report — report Agent Experience friction

You are often the *user* of a tool, not its author. When a tool makes your job
harder than it should, that is an AX defect, and it is worth capturing the same
way a usability tester captures a confused click. This skill files a structured
report so the tool's maintainers can fix the contract.

## Getting started — when a user puts you on a tool to evaluate

The user should only have to say something short, like *"I want to AX-test
`<tool>`"* or *"we're testing `<tool>`, log friction as we go"*. The rest is your
job, from this skill — do not make them recite a contract. Set up once, then
**let them drive**:

1. **Do not run your own test suite.** The user gives the tasks; you do them with
   the tool and file a report only when something actually trips you. Reporting
   is a side-channel to the real work, not a reason to go probe the tool.
2. **Stay on the user surface.** Use only what a user has — the tool's CLI and
   `--help`, its MCP tools, its skill, its public docs. **Do not read the tool's
   source code, its installed package files, or its tests.** A real user cannot,
   and it hides the very friction you are testing for. If you find yourself
   wanting to read the implementation to make progress, that wanting is itself a
   finding (a missing affordance or unclear contract) — file it and continue from
   the surface.
3. **Fix the subject.** `<tool>` is what every report's `tool` field says, no
   matter which command, flag, or MCP tool you happen to touch.
4. **Mint a `session_id`** (`openssl rand -hex 4`) so the run's findings batch
   together.
5. **Tell the user, in one line, where things will go** — the `session_id` and
   the reports directory `~/.claude/ax-reports/<tool>/` (or `$AX_REPORTS_DIR`) —
   so they know it is set up.
6. **Then stop and wait for their first task.** File reactively as friction
   arises (see below). Only pursue a goal yourself, keeping a running log, if the
   user explicitly asks you to *run the evaluation* — that is the optional
   session mode at the end of this file.

That is the whole handshake, and it is yours to carry: the user says one line,
you do steps 1–6 and then work. The default is reactive — do what you are asked,
stay on the surface, and file the moment the tool fails you.

## When to file (and when not to)

**The bar is low, and the check is constant.** This is the part agents get
wrong: heads-down on the task, you adapt to friction and sail past it. After
each thing you do with the tool, ask one question — *did that surface behave the
way its docs, help, or output implied?* If you had to clean noise out of output,
retry, guess a command or flag, work around something, or reverse-engineer how
the tool works, that is friction. **File it before you move on**, while you still
remember what you expected. The moment you finish the workaround it starts to
feel "solved" and you forget it was ever a problem — that reflex is the enemy.
**Under-reporting is the failure mode, not over-reporting.** When unsure whether
something counts, file it at low severity; the triager drops noise.

**The single most diagnostic tell: you wrote glue code.** If you had to write
`curl`, `grep`, a script, or otherwise probe, scrape, or reverse-engineer to get
something the tool should expose directly, **that workaround IS the evidence** —
file friction immediately. This is the case agents miss most, because there was
no failed call to react to; there was an *absent* call you compensated for. The
absence is the defect. Do not downgrade it to a "feature request" just because a
capability is missing: a missing affordance that forced a real, evidenced
workaround has an expected, an actual, and a workaround — that is a friction
report, by definition.

Another tell: if you catch yourself thinking "that was a bit annoying but I got
it working" or "I'll just use the other command instead" — stop and file. That
sentence *is* a friction report waiting to be written.

**File a `friction` report when you hit a real, evidenced problem:**

- You wrote code, probed, scraped, or reverse-engineered to do something the tool
  should expose directly (a URL/route, a flag, where a file goes, which process
  serves what). The glue code is the evidence.

- A surface lied. The skill/docs listed a tool that does not exist or is named
  differently, or omitted one that does (you almost told the user "no" wrongly).
- A check, probe, or verdict failed when the real operation actually works (or
  passed when it does not).
- Logs, warnings, progress bars, or chatter rode along in the output, so you
  had to read past noise or a strict parser would choke (you parsing it anyway
  does not make it fine).
- An error was an opaque stack trace with no code or hint.
- A result lacked what you needed to act or cite, forcing a second call.
- You had to reverse-engineer how to do something the tool should have told you
  — a URL or route, a flag, where a file goes, which process serves what.
- The tool did something surprising that contradicted what its surface told you.

**Do not file** for a minor preference or a one-off. A `friction` report you
cannot back with *expected / actual / workaround* is not a report.

**Wish vs. friction — do not confuse them** (this is the line that wrongly talks
agents out of filing): a *wish* is something you'd like that cost you nothing —
no workaround, no lost time, no glue code. That is a `feature_request`, the lower
tier. A *missing affordance you actually had to work around* is **friction**: the
workaround is your evidence, and you have an expected, an actual, and a
workaround. "The tool can't do X" is only a wish when you did **not** have to
compensate for it. The moment you wrote code to fill the gap, it is friction —
file it as friction, not a feature_request.

## The report — evidence, not opinion

Every `friction` report must answer four things:

- **task** — what you were trying to do.
- **expected** — what the tool's own surface led you to expect.
- **actual** — what happened.
- **workaround** — what you did instead (or `null` if you were blocked).

Then classify it:

- **kind** — `friction` or `feature_request`.
- **heuristic** — which AX heuristic it violates (see `heuristics.md`):
  `contract_truth`, `pure_machine_output`, `single_round_trip`,
  `honest_verdicts`, `discoverability`, `self_correcting_errors`,
  `affordance_completeness`, or `other`.
- **severity** — `low` | `medium` | `high` | `critical`. A *silently false*
  signal outranks a dead-end, which outranks an extra round-trip.

## How to file — write one JSON file

Filing is just writing a file. You already know how. There is no program to run:
this skill is a method and a contract, nothing to execute. Write one JSON object
to a path whose folders and name carry the report's key facts, so the next agent
finds it with `ls` and `find` instead of opening every file.

**Path** (under `$AX_REPORTS_DIR`, default `~/.claude/ax-reports/`):

```
<tool>/friction/<severity>/<utc-stamp>--<session>--<heuristic>--<id>.json
<tool>/feature_request/<utc-stamp>--<session>--<id>.json
```

`<utc-stamp>` is a sortable UTC time with no colons — get an exact one from
`date -u +%Y-%m-%dT%H%M%SZ` (a universal shell command, not bundled code).
`<session>` is the session id you were given (8 chars), shared by every finding
from this goal so the batch is greppable; use `nosession` if you were not given
one. `<id>` is any 8 hex characters, for uniqueness. So a high-severity
honest-verdicts report about `anchor` from session `a1b2c3d4` lands at:

```
~/.claude/ax-reports/anchor/friction/high/2026-06-09T114015Z--a1b2c3d4--honest_verdicts--8c2f1d44.json
```

The folders and filename now answer *which tool, friction or wish, how urgent,
which heuristic, when* before anyone opens the file.

**Contents** (full shape in `schema/ax-report.schema.json`):

```json
{
  "schema_version": "0.1",
  "id": "8c2f1d44",
  "session_id": "a1b2c3d4",
  "goal": "get an LKH pump datasheet's specs onto a cited canvas",
  "created_at": "2026-06-09T11:40:15Z",
  "tool": "anchor",
  "surface": "anchor check --probe",
  "kind": "friction",
  "heuristic": "honest_verdicts",
  "severity": "high",
  "task": "verify the setup before ingesting",
  "expected": "the probe passes iff a real ingest would work",
  "actual": "probe failed on a max_tokens param the model rejected; ingest worked",
  "workaround": "ignored the probe and ran ingest, which succeeded",
  "agent": "claude-opus-4-8"
}
```

A `friction` report MUST include `task`, `expected`, `actual`, `heuristic`, and
`severity`. If you cannot fill `expected` and `actual`, you have a wish, not a
report: file it as `feature_request` with a `suggestion`, or do not file. The
path mirrors fields in the file on purpose — the path is the index, the file is
the detail.

You are the writer, not the reviewer. You do not need to read other reports to
file yours, and you should not — leave the corpus to the triager. To avoid a
same-issue duplicate you can *list* (not read) the target folder; the path
already encodes tool, kind, severity, and heuristic, so a filename scan is
enough: `ls <tool>/friction/<severity>/ | grep <heuristic>`.

One shell idiom files the whole thing with universal tools:

```bash
dir="${AX_REPORTS_DIR:-$HOME/.claude/ax-reports}/anchor/friction/high"
mkdir -p "$dir"
name="$(date -u +%Y-%m-%dT%H%M%SZ)--a1b2c3d4--honest_verdicts--$(openssl rand -hex 4).json"
cat > "$dir/$name" <<'JSON'
{ ...the object shown above... }
JSON
```

## Running an evaluation session (optional, only if asked to drive)

Everything above is reactive: the user drives, you file when the tool trips you.
This section is the other mode, and you use it **only when the user asks you to
run the evaluation yourself** — to go pursue a goal and report what breaks. Do
not start this on your own; an unasked-for self-driven test is exactly the
over-eager behavior to avoid. When asked, run it as a session so the findings
batch together and you judge them honestly:

1. Pick a realistic, end-to-end goal and a `session_id` (`openssl rand -hex 4`).
2. Pursue the goal for real. As you go, the instant the tool makes you pause —
   a retry, a doc that did not match, a verdict that disagreed with reality,
   output you had to clean, an opaque error, a forced second call, a plain
   "huh" — jot **one line** (tool, what you were doing, expected, happened). Do
   not stop, do not judge yet. Capturing now beats normalizing the quirk away.
3. After the goal, judge the notes **cold** — the task is done, nothing to
   prove, so the urge to call a broken tool fine is gone. Drop your own
   mistakes, classify the rest (heuristic + severity), and file each as a report
   sharing this `session_id` and `goal`.
4. Record the run at `<tool>/sessions/<utc>--<session_id>.json` (`session_id`,
   `goal`, `tool`, `started_at`, `achieved`, `summary`), then give the user the
   findings table and the single highest-value fix.

Optional: have a *separate* agent read your transcript afterward to catch
friction you adapted to so fast you never noticed it. Keep it judging, not doing.

## Triage

Reading and triaging the corpus is a separate role — see the `ax-review` skill,
or just use filesystem tools (`tree` / `ls` / `find` / `cat`), since the path is
the index. Promote real findings into the tool's issue tracker. Do not file
duplicates for the same issue in one session; tell the user what you filed.
