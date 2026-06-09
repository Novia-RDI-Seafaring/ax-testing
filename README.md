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

See [`heuristics.md`](./skills/ax-report/heuristics.md) for the working heuristic
set (the agent analog of Nielsen's usability heuristics).

## Three skills, one loop

The full AX-testing loop, as three [skills.sh](https://skills.sh)-compatible
skills under `skills/`. Each installs independently into any supported harness.

| Skill | Role | What it does |
| --- | --- | --- |
| **`ax-facilitate`** | run the test | Spawns a *subject* sub-agent to pursue a real goal with only the tool's surface, observes it, and files the friction it hits. The doer and the observer are separate on purpose. |
| **`ax-report`** | the contract | Defines a single finding: the evidence it must carry, how to classify it, and the self-describing path it is written to. |
| **`ax-review`** | triage | Reads the corpus with filesystem tools, groups by session / tool / severity, summarizes, and decides what to promote into a tool's issue tracker. |

```
skills/
├── ax-facilitate/SKILL.md
├── ax-report/
│   ├── SKILL.md
│   ├── heuristics.md
│   ├── schema/ax-report.schema.json
│   └── examples/probe-cried-wolf.json
└── ax-review/SKILL.md
```

## No code, on purpose

These skills ship **no program to run**. A skill that bundles an executable
trades the agent's existing trust boundary for the repo author's supply chain,
which is a bad trade for tasks an agent already does natively. So:

- **Filing** is "write a JSON file to a self-describing path." The agent already
  knows how to write a file.
- **Reading** is `tree` / `ls` / `find` / `cat`. The path encodes tool, kind,
  severity, heuristic, session, and time, so the filesystem *is* the index.

A skill should be **data, not code**, whenever the task is something the agent
can already do. Enforcement belongs on the trusted reader's side (triage), not in
a gate the agent runs on itself.

## Install

```bash
npx skills add Novia-RDI-Seafaring/ax-reporting-skill                 # interactive: pick skills
npx skills add Novia-RDI-Seafaring/ax-reporting-skill --skill ax-report
```

Install `ax-report` (and `ax-facilitate`) wherever agents run; install
`ax-review` wherever you triage.

## Where reports live

Under `~/.claude/ax-reports/` (override with `AX_REPORTS_DIR`), one JSON file per
finding, append-only, at a path that carries its facts:

```
<tool>/friction/<severity>/<utc>--<session>--<heuristic>--<id>.json
<tool>/feature_request/<utc>--<session>--<id>.json
<tool>/sessions/<utc>--<session>.json        # a goal + its outcome
```

A `friction` report must carry evidence (`task`, `expected`, `actual`) plus a
`heuristic` and `severity`. A wish with no observed friction is a
`feature_request`, a clear tier below friction. That constraint keeps the corpus
high-signal rather than a suggestion box. The corpus also doubles as AX research
data: every report is a findings-table row, classified by heuristic and severity.

## License

MIT. See [`LICENSE`](./LICENSE).
