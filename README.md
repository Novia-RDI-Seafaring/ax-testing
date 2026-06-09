# ax-reporting-skill

A global agent skill for filing **Agent Experience (AX)** reports. When a tool
trips an agent up, the agent files structured, evidenced friction so the tool's
maintainers can fix it. The same way usability testing turns a confused user
into a bug report, this turns a stuck agent into an AX report.

## What is AX?

**AX (Agent Experience)** is the agent-facing counterpart of UX. UX asks how
easy a tool is for a *person* to use. AX asks the same question for an *agent*:
how discoverable, legible, truthful, and composable a software surface is for a
non-human user driving it through a CLI, an MCP server, or an API.

The shift behind the term: software is no longer used only by people. Agents are
first-class users now, and they deserve the same deliberate design and study
that UX gives humans. AX names that dimension so we can talk about "how good is
this tool for an agent" with the same precision UX gives us for humans.

AX is not the same as API design. API design is the technical surface area. AX
is the agent's *cognitive experience* of that surface: can it discover the
capability, does the output mean what it says, does an error explain itself, does
a result carry what's needed to act without a second call.

The defining property, and the one this skill is built around: **an agent trusts
the contract.** A human cross-checks a tool against the world and shrugs off a
wrong label. An agent reads the skill, the tool list, and the output, and acts on
them as truth. So the cardinal AX defect is a surface that *lies* — a doc that
omits a real tool, a check that fails when the operation works, logs mixed into
machine output. Contract truth matters more than features.

See [`heuristics.md`](./heuristics.md) for the working heuristic set (the agent
analog of Nielsen's usability heuristics).

## What this repo is

A skill (`SKILL.md`) plus a dependency-free CLI (`ax_report.py`) that together
let any agent file an AX report from inside a session, and let a human triage the
results.

- **`SKILL.md`** — the agent-facing instructions: when to file, the evidence a
  report must carry, how to classify it, how to file it.
- **`ax_report.py`** — `file`, `list`, `show`, `validate`. No dependencies.
- **`schema/ax-report.schema.json`** — the report shape (JSON Schema draft-07).
- **`heuristics.md`** — the AX heuristics and severity scale.
- **`examples/`** — a real report.

## Install the skill

Copy or symlink the skill where your harness discovers skills. For Claude Code:

```bash
mkdir -p ~/.claude/skills/ax-report
cp SKILL.md ~/.claude/skills/ax-report/SKILL.md
# Put the CLI on PATH so the skill's preferred path works:
install -m 0755 ax_report.py ~/.local/bin/ax-report
```

An agent that hits friction can then file a report; if the CLI is absent it
writes the JSON file directly, per the schema.

## File a report

```bash
ax-report file \
  --tool anchor --surface "anchor check --probe" \
  --kind friction --heuristic honest_verdicts --severity high \
  --task "verify setup before ingesting" \
  --expected "probe passes iff a real ingest would work" \
  --actual "probe failed on a max_tokens param the model rejected; ingest worked" \
  --workaround "ignored the probe and ran ingest, which succeeded"
```

Reports land under `~/.claude/ax-reports/<tool>/` (override with
`AX_REPORTS_DIR`). One JSON file per report, append-only.

A `friction` report must carry evidence (`task`, `expected`, `actual`) and a
`heuristic` + `severity`. A wish with no observed friction is a `feature_request`
instead, kept a clear tier below friction. That constraint is the whole point: it
keeps the corpus high-signal rather than a suggestion box.

## Triage (the other half of the loop)

Reporting only pays off if someone reads it. A write-only dump trains agents that
reporting is pointless.

```bash
ax-report list --severity high        # what needs attention
ax-report show 1a2b3c4d               # full report by id prefix
```

Review reports, then promote the real ones into the relevant tool's issue
tracker. The corpus also doubles as AX research data: each report is a row in a
findings table, classified by heuristic and severity.

## License

MIT. See [`LICENSE`](./LICENSE).
