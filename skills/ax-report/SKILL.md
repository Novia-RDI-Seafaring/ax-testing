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

## When to file (and when not to)

**File a `friction` report when you hit a real, evidenced problem:**

- A surface lied. The skill/docs listed a tool that does not exist or is named
  differently, or omitted one that does (you almost told the user "no" wrongly).
- A check, probe, or verdict failed when the real operation actually works (or
  passed when it does not).
- Logs, progress bars, or chatter polluted machine output (`stdout`), so a
  strict parser would choke.
- An error was an opaque stack trace with no code or hint.
- A result lacked what you needed to act or cite, forcing a second call.
- The tool did something surprising that contradicted what its surface told you.

**Do not file** for a minor preference, a one-off, or a wish with no observed
friction. A `friction` report you cannot back with *expected / actual /
workaround* is not a report. If you only have a wish, file it as a
`feature_request` (a lower tier), and keep it honest.

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
  `honest_verdicts`, `discoverability`, `self_correcting_errors`, or `other`.
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
dir=~/.claude/ax-reports/anchor/friction/high
mkdir -p "$dir"
name="$(date -u +%Y-%m-%dT%H%M%SZ)--a1b2c3d4--honest_verdicts--$(openssl rand -hex 4).json"
cat > "$dir/$name" <<'JSON'
{ ...the object shown above... }
JSON
```

## Running an evaluation session (optional)

The above is for friction you hit while doing something else: file it on the
spot. When you instead *set out* to AX-test a tool, run it as a session so the
findings batch together and you judge them honestly:

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
