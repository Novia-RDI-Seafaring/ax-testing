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

### Two sub-dimensions: agent-friendly and agent-accessible

UX always carried two concerns: usability (is it pleasant and low-friction) and
accessibility (can every class of user reach the functionality at all). AX
inherits both.

- **Agent-friendly** — the experience quality. The surface is intuitive for an
  agent, the contract tells the truth, the output is clean, and the agent can
  turn a user's request into tool actions without contortion. This is what the
  heuristics measure.
- **Agent-accessible** — the coverage. The agent can do what a human user can,
  instead of being a second-class user locked out of half the product. The
  mechanism is **adapter parity**: every operation reachable on the CLI, the MCP
  server, and the HTTP API, never only through the GUI.

"Accessible" is literal here, not a metaphor. The end user increasingly drives an
app *through* their own agent. The agent is the user's proxy, the same way a
screen reader is a proxy for a blind user. Deny the screen reader and you deny
its user; deny the agent half the product and you deny the human who works
through it. Agent-accessibility is the same anti-discrimination principle applied
to a new kind of intermediary.

A tool is **fully usable by an agent** when it is both: agent-accessible (the
agent is admitted to the whole feature set) and agent-friendly (it can use that
set without friction). Accessibility is the precondition; friendliness is what
this skill set measures and reports on.

The defining property, and the one this skill is built around: **an agent trusts
the contract.** A human cross-checks a tool against the world and shrugs off a
wrong label. An agent reads the skill, the tool list, and the output, and acts on
them as truth. So the cardinal AX defect is a surface that *lies* — a doc that
omits a real tool, a check that fails when the operation works, logs mixed into
machine output. Contract truth matters more than features.

See [`heuristics.md`](./skills/ax-report/heuristics.md) for the working heuristic
set (the agent analog of Nielsen's usability heuristics).

## Three skills

The AX-testing loop, as three [skills.sh](https://skills.sh)-compatible skills
under `skills/`. Each installs independently into any supported harness.

| Skill | Role | What it does |
| --- | --- | --- |
| **`ax-run`** | orchestrate | Run a *valid* AX test: drive a real harness as a fresh, unbiased subject in an isolated workspace so it cannot cheat by reading the tool's source — and treat "needing the source" as a finding rather than a shortcut. For whoever drives the test. |
| **`ax-report`** | report | File a finding the moment a tool trips you: the evidence it must carry, how to classify it, the self-describing path it lands at. Includes an optional *evaluation-session* mode for when you set out to AX-test a tool — keep a running log of friction as it happens, then judge the notes cold and file the batch. For the subject. |
| **`ax-review`** | triage | Read the corpus with filesystem tools, group by session / tool / severity, summarize, and decide what to promote into a tool's issue tracker. For the reviewer. |

```
skills/
├── ax-run/SKILL.md
├── ax-report/
│   ├── SKILL.md
│   ├── heuristics.md
│   ├── schema/ax-report.schema.json
│   └── examples/probe-cried-wolf.json
└── ax-review/SKILL.md
```

The three are deliberately separate roles: **`ax-run`** sets up and audits the
test, **`ax-report`** is what the subject files into, **`ax-review`** is for the
reviewer. Keeping the orchestrator out of the subject seat is what keeps the test
unbiased.

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

The skill carries the contract, so you don't have to. After restarting the
agent, in a fresh session, say one line:

> I want to AX-test **`<tool>`**.

That triggers the skill's handshake: it fixes the subject, mints a session, tells
you where reports will land, and then waits — and from there it stays on the
tool's surface (no reading the source), files friction the moment something trips
it, and does **not** run its own test battery. Just give it real tasks.

If you want it to *drive itself* — pursue a goal and report what breaks — say
"run an AX evaluation of `<tool>` toward this goal: …". Triage later with the
`ax-review` skill.

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

## Citing

If you use these skills or the AX testing method, please cite the paper
(GitHub also renders a "Cite this repository" button from `CITATION.cff`):

> Björkskog, C., Jatta, L., Westö, J., & Manggård, M. (2026).
> *AX: Agent Experience as the Dual of User Experience.* Preprint, in preparation.

```bibtex
@article{bjorkskog2026ax,
  title  = {{AX}: Agent Experience as the Dual of User Experience},
  author = {Bj\"orkskog, Christoffer and Jatta, Lamin and West\"o, Johan
            and Mangg\aa{}rd, Mikael},
  year   = {2026},
  note   = {Preprint, in preparation}
}
```

## License

MIT. See [`LICENSE`](./LICENSE).
