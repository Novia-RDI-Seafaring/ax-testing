---
name: ax-review
description: |
  Triage Agent Experience (AX) reports: read the filed reports, group them,
  summarize the friction, and decide what to promote into a tool's issue
  tracker. Use when asked to "triage AX reports", "review the ax-reports",
  "what AX issues were filed for <tool>", "summarize agent friction", or "what
  should we fix first". You are the reviewer half of AX reporting — the reports
  are written by the ax-report skill. Trigger words: "triage", "read the AX
  reports", "review AX reports", "AX findings", "what friction was reported".
---

# ax-review — triage the AX report corpus

Reports are JSON files in the reports directory: `$AX_REPORTS_DIR`, or
`~/.claude/ax-reports/` if that is unset. **Resolve it once and reuse it**, since
it may not be the default:

```bash
R="${AX_REPORTS_DIR:-$HOME/.claude/ax-reports}"
```

The path is the index, so you read the corpus with ordinary filesystem tools —
there is no program to run. Your job: turn a pile of reports into a ranked,
deduped summary and a short list of things worth fixing.

**The corpus is global.** Reports from every tool and project accumulate under
`$R`, one folder per tool. So **start by seeing what is there and focus on the
tool you were asked about**:

```bash
ls "$R"        # the tools that have reports (e.g. anchor, ax-report, saari, …)
```

If the tool you care about has no folder, there are no reports for it yet — say
so plainly rather than triaging some other tool's reports.

## Layout you are reading

```
<tool>/friction/<severity>/<utc>--<session>--<heuristic>--<id>.json
<tool>/feature_request/<utc>--<session>--<id>.json
<tool>/sessions/<utc>--<session>.json        # the goal + outcome for a session
```

Folders and filenames carry tool, kind, severity, heuristic, session, and time,
so you can filter before opening anything.

## Read with filesystem tools

With `R` resolved as above (substitute your tool for `anchor` and the real
session id for `a1b2c3d4`):

```bash
find "$R" -type f -name '*.json' | sort           # every report (portable; no deps)
tree "$R"                                          # nicer overview, only if `tree` is installed
ls "$R"/anchor/friction/critical/ "$R"/anchor/friction/high/ 2>/dev/null  # most urgent first
find "$R" -path '*/friction/*honest_verdicts*'    # one heuristic, across tools
find "$R" -name '*--a1b2c3d4--*'                   # every finding from one session/goal
cat "$R"/anchor/sessions/*--a1b2c3d4.json          # that session's goal + outcome
cat <report.json>                                  # full detail
```

Prefer `find` for listing; `tree` is a convenience that may be absent. Each
report is plain JSON — read it with `cat` and parse it however you like.

## Produce a triage

1. **Sort by severity.** `critical` and `high` first — these are surfaces that
   lied or produced a wrong result the agent could not detect.
2. **Group by session.** Read the session record for each `session_id` so a
   batch of findings has its goal as context. Five findings from one goal tell a
   story; read them together.
3. **Cluster duplicates.** Collapse reports that share a `surface` + `heuristic`
   into one finding with a count. Recurring heuristics across tools are a
   pattern worth naming.
4. **Output a findings table.** Columns: severity · tool · heuristic · surface ·
   one-line summary · count. `feature_request`s go in a separate, lower section.

## Decide what to promote

Promote the real ones into the relevant tool's issue tracker, **contract-truth
violations first** (a surface that lies costs more than a missing feature).
Wishes (`feature_request`) rank below every confirmed friction. State plainly
what you would *not* promote and why, so the corpus stays trusted.

## Stay read-mostly

Default to summarizing and promoting. Do not mutate or delete reports unless the
user asks. If you mark something triaged, do it non-destructively (write a
summary file, or move handled reports into a `triaged/` subtree), never by
editing the originals.
