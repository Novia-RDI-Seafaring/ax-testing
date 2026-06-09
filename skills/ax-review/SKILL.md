---
name: ax-review
description: |
  Triage Agent Experience (AX) reports: read the filed reports, group them,
  summarize the friction, and decide what to promote into a tool's issue
  tracker. Use when asked to "triage AX reports", "review the ax-reports",
  "what AX issues were filed for <tool>", "summarize agent friction", or "what
  should we fix first". You are the reviewer half of AX reporting — the reports
  are written by the ax-report / ax-facilitate skills. Trigger words: "triage",
  "review AX reports", "AX findings", "what friction was reported".
---

# ax-review — triage the AX report corpus

Reports are JSON files under `~/.claude/ax-reports/` (or `$AX_REPORTS_DIR`). The
path is the index, so you read the corpus with ordinary filesystem tools — there
is no program to run. Your job: turn a pile of reports into a ranked, deduped
summary and a short list of things worth fixing.

## Layout you are reading

```
<tool>/friction/<severity>/<utc>--<session>--<heuristic>--<id>.json
<tool>/feature_request/<utc>--<session>--<id>.json
<tool>/sessions/<utc>--<session>.json        # the goal + outcome for a session
```

Folders and filenames carry tool, kind, severity, heuristic, session, and time,
so you can filter before opening anything.

## Read with filesystem tools

```bash
tree ~/.claude/ax-reports                                      # whole corpus + counts
ls ~/.claude/ax-reports/anchor/friction/critical/             # most urgent first
find ~/.claude/ax-reports -path '*/friction/*honest_verdicts*' # one heuristic, all tools
find ~/.claude/ax-reports -name '*--a1b2c3d4--*'              # every finding from one session/goal
cat ~/.claude/ax-reports/anchor/sessions/*--a1b2c3d4.json     # that session's goal + outcome
cat <report.json>                                             # full detail
```

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
