# ax-run runner (reference tooling)

A small reference implementation of the [`ax-run`](../skills/ax-run/SKILL.md)
skill. **Optional tooling, not a skill** — the skills themselves stay code-free;
this script just automates the orchestrator's setup and audit so you can press
play on a valid AX test.

It deliberately **does not launch the harness for you**. Setting up an isolated
workspace and printing the exact command is the safe, reproducible part; the
actual headless agent (with tool permissions) should be started deliberately
from your own terminal, not spawned from inside another agent.

## Use

```bash
# 1. Prepare an isolated run. Prints the workspace, the AX_REPORTS_DIR, and the
#    exact next commands (install the wheel into a venv; launch the harness).
runner/ax-run.sh setup anchor "get a datasheet's specs onto a cited canvas"

# 2. (you run) install the RELEASED wheel into the workspace venv, then launch
#    the real harness headless from the clean workspace with the printed command.

# 3. Audit the run for validity, pointing at the subject's transcript:
runner/ax-run.sh audit "<workspace>" anchor "<transcript.jsonl>"
#    -> VALID, or CONTAMINATED (and the run manifest's contaminated flag is set).
```

For **Claude Code**, the subject's transcript lives under
`~/.claude/projects/<encoded-workspace-path>/*.jsonl`.

## What it enforces (and what stays manual)

| Control | How |
| --- | --- |
| Workspace isolation | a throwaway `mktemp` dir with only the installed tool + the ax-report skill; no repo, tests, or internal docs in reach |
| Installed wheel, not a checkout | the printed install line uses `uv pip install <tool>-kb` into a per-run venv, so the package does not resolve into a readable source tree |
| Black-box contract | the printed launch command carries the "you are a user; don't read the source; if you want to, file it" rule |
| Audit + taint | `audit` greps the transcript for reads of the tool's source / package `.py` / tests / `__file__` introspection; any hit marks the run contaminated — and is itself an AX finding |
| Reproducibility | a run manifest (`<reports>/<tool>/sessions/<utc>--<session>.json`) records harness, model, tool version, workspace, and the contaminated flag |
| Harness launch | **manual, by you** — a real headless agent with permissions, not nested inside another agent |

## Validity model

A real user cannot read a tool's implementation, so neither should the test
subject. You cannot make that physically impossible on a normal machine, so the
principle is: **needing the source is the finding**. The contract tells the
subject to file the impulse rather than act on it; the audit catches it if it
acts anyway and taints the run. See the `ax-run` skill and the paper's "Threats
to validity and controls" section.
