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
  triage. Trigger words: "AX", "agent experience", "this tool tripped me up",
  "the docs were wrong", "report friction", "file an AX report".
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

## How to file

Prefer the bundled CLI (`ax_report.py`, in this skill's folder; it validates and
stores consistently). Run it as `ax-report` if it is on PATH, otherwise
`python3 <this-skill-dir>/ax_report.py`:

```bash
ax-report file \
  --tool anchor --surface "anchor check --probe" \
  --kind friction --heuristic honest_verdicts --severity high \
  --task "verify setup before ingesting" \
  --expected "probe passes iff a real ingest would work" \
  --actual "probe failed on a max_tokens param the model rejected; ingest worked" \
  --workaround "ignored the probe and ran ingest, which succeeded"
```

Or pipe a JSON object on stdin: `ax-report file --json -`.

If the CLI is not available, write the same object yourself as a JSON file under
the reports directory (default `~/.claude/ax-reports/<tool>/`), using the schema
in `schema/ax-report.schema.json`. Working even when a surface is missing is
itself good AX.

## After filing

Tell the user you filed a report and where. Do not file duplicates for the same
issue in one session. Reports are for a human (or a triage agent) to review and,
if real, promote into the tool's issue tracker. Filing into a void trains
everyone that reporting is pointless, so reporting is only half the loop:
triage (`ax-report list`) is the other half.
