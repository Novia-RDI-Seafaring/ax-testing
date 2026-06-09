# ax-testing

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

## Two skills

The AX-testing loop, as two [skills.sh](https://skills.sh)-compatible skills
under `skills/`. Each installs independently into any supported harness.

| Skill | Role | What it does |
| --- | --- | --- |
| **`ax-report`** | report | File a finding the moment a tool trips you: the evidence it must carry, how to classify it, the self-describing path it lands at. Includes an optional *evaluation-session* mode for when you set out to AX-test a tool — keep a running log of friction as it happens, then judge the notes cold and file the batch. |
| **`ax-review`** | triage | Read the corpus with filesystem tools, group by session / tool / severity, summarize, and decide what to promote into a tool's issue tracker. |

```
skills/
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

Install with the [`skills`](https://skills.sh) CLI, and **target your harness
explicitly** with `-a`. Auto-detect can pick the wrong path — by default it
installs to `.agents/skills/` (which Cursor, Codex, Amp and others read) but
**Claude Code reads `.claude/skills/`**, so an auto-detected install can leave
Claude Code unable to see the skill.

```bash
# Claude Code, globally (→ ~/.claude/skills/, available in every project)
npx skills add Novia-RDI-Seafaring/ax-testing -a claude-code -g -y

# Cursor / Codex / Amp / … (these share .agents/skills/)
npx skills add Novia-RDI-Seafaring/ax-testing -a cursor -g -y

# just one of the skills
npx skills add Novia-RDI-Seafaring/ax-testing --skill ax-report -a claude-code -g -y
```

Flags: `-a/--agent <harness>` targets where files land, `-g/--global` installs to
the user dir instead of the current project, `-y` skips the prompts.

**Skills load at the agent's startup — restart the agent after installing.**
Verify the files landed: `ls ~/.claude/skills/ax-report/SKILL.md`.

Install `ax-report` wherever agents run; install `ax-review` wherever you
triage.

## Using it

After restarting your agent, put it on a tool and then just work. Tell it once:

> We are evaluating **`<tool>`**. As I ask you to do things with it, use the
> `ax-report` skill to log friction when something trips you. Don't run your own
> tests — just do what I ask and file reports as we go.

The agent confirms the subject, a `session_id`, and where reports will land, then
waits for your tasks and files reactively. If you instead want it to *drive* —
pursue a goal on its own and report what breaks — say "run an AX evaluation of
`<tool>` toward this goal: …". Triage later with the `ax-review` skill.

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
