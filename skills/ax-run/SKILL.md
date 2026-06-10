---
name: ax-run
description: |
  Run a valid, hard-to-cheat Agent Experience (AX) test by driving a REAL
  harness as an unbiased test subject. Use when you (the orchestrator) want to
  evaluate a tool's AX with a fresh agent, without that agent cheating by reading
  the tool's source, and without your own context biasing it. Sets up an isolated
  workspace, launches a real harness, keeps the run valid, then hands the reports
  to ax-review. Trigger words: "run an AX test", "validate the AX", "AX-test a
  tool with a clean harness", "set up an AX evaluation", "test the agent
  experience without cheating".
---

# ax-run — run a valid AX test against a real harness

You are the **orchestrator**, never the subject. Your job is to set up a test
that measures what a *real harness* experiences using a tool, with a fresh agent
that uses the tool the way a user would — through its surface, never its source.
A test is only worth its findings if it is **valid**: the subject must be (1) a
real harness, (2) fresh, (3) unbiased by you, and (4) unable to cheat by reading
the implementation.

## The threats, and why each control exists

- **Fidelity.** AX is harness-specific — the harness's system prompt and
  tool-loading are part of the experience. A sub-agent or a stripped
  "mini-harness" measures a *different* subject whose findings do not transfer.
  Use a real harness (Claude Code, Cursor, Codex, …), launched headless.
- **Cheating.** An agent that can read the tool's source discovers undocumented
  behavior and so never hits the discoverability / contract friction you are
  testing for. A real user has the *installed* tool, not its code.
- **Bias.** You already know the tool; that knowledge must not leak to the
  subject. Give it the goal and nothing else.

## The key principle: needing the source is the finding

You cannot make an agent physically unable to read source on a normal machine.
So do not rely on prevention alone — **convert the impulse into a signal**. A
real user cannot read the implementation; if the subject *wants* to, that wanting
*is* the discoverability / affordance-completeness defect. Measure it.

## Set up an isolated run

1. **Clean workspace.** A throwaway directory holding only what a user has — the
   user's own documents and any config the tool needs. No tool repo, no test
   suite, no internal design docs in the working directory or reachable by `..`.
2. **Installed tool, not a checkout.** Install the released wheel, not an
   editable source checkout, so `which <tool>` and the package do not resolve
   into a readable source tree.
3. **Fresh session, no memory.** No `CLAUDE.md` / project memory about the tool,
   a clean agent config, so no prior knowledge leaks in.
4. **Pin and record** the harness, harness version, model, and tool version in a
   run manifest (below).

Concretely, with your own shell — this needs no bundled program:

```bash
tool=anchor; goal="get a datasheet's specs onto a cited canvas"
session=$(openssl rand -hex 4); utc=$(date -u +%Y-%m-%dT%H%M%SZ)
ws=$(mktemp -d "${TMPDIR:-/tmp}/ax-run-$session.XXXXXX")
reports="$ws/ax-reports"; mkdir -p "$ws/.claude/skills" "$reports/$tool/sessions"

# the subject needs the ax-report skill; a global install is inherited by the
# workspace harness (npx skills add ... -a claude-code -g -y), so nothing to copy.
# install the RELEASED wheel into a per-run venv so the package is not a checkout:
uv venv "$ws/.venv" && uv pip install --python "$ws/.venv/bin/python" "${tool}-kb"

# write the run manifest
cat > "$reports/$tool/sessions/$utc--$session.json" <<JSON
{"session_id":"$session","tool":"$tool","goal":"$goal","harness":"claude-code",
 "model":"<fill>","tool_version":"$("$ws/.venv/bin/$tool" version 2>/dev/null)",
 "workspace":"$ws","contaminated":false,"started_at":"$utc"}
JSON
```

## The black-box contract (give this to the subject verbatim)

Give the subject only a realistic, end-to-end goal — nothing about how the tool
works internally — plus this rule:

> You are a user of `<tool>`. Use only its user-facing surface: its CLI and
> `--help`, its MCP tools, its skill, its public docs. Do NOT read the tool's
> source code, its installed package files, or its tests — a real user cannot,
> and doing so invalidates this test. If you find yourself wanting to read the
> implementation to make progress, stop: that wanting is itself an AX finding (a
> missing affordance or an unclear contract). File it with `ax-report` and carry
> on from the user surface.

Launch the real harness headless, from the clean workspace, with that contract.
**Do this from your own terminal, not nested inside another agent** — a real
agent with tool permissions should be started deliberately:

```bash
cd "$ws" && AX_REPORTS_DIR="$reports" PATH="$ws/.venv/bin:$PATH" \
  claude -p "Goal: $goal

You are a user of $tool. Use only its user-facing surface (CLI/--help, MCP, its
skill, public docs). Do NOT read its source, installed package files, or tests;
if you find yourself wanting to, that wanting is an AX finding — file it with
ax-report and continue from the user surface."
```

## Audit the run for validity

Before you trust the findings:

- Scan the subject's transcript for any read of the tool's source, its installed
  package path, or its tests. If found, mark the run **contaminated** in the
  manifest — and record it as a finding: the subject reached for the source,
  which is itself an AX gap. For Claude Code the transcript is under
  `~/.claude/projects/<encoded-workspace-path>/*.jsonl`; a one-line check:

  ```bash
  grep -aoEi "site-packages/$tool[/_-][^\"' ]*\.py|/$tool/[^\"' ]*\.py|$tool/tests/|$tool\.__file__" \
    ~/.claude/projects/*/*.jsonl && echo CONTAMINATED || echo VALID
  ```
- For high-rigor runs, remove the temptation entirely: run the harness in a
  container where the tool is installed but its source is not readable (only the
  entrypoint on `PATH`), so cheating is impossible rather than discouraged.
- For high-rigor runs, remove the temptation entirely: run the harness in a
  container where the tool is installed but its source is not readable (only the
  entrypoint on `PATH`), so cheating is impossible rather than discouraged.

## Hand off

The subject files reports through `ax-report` into the corpus. You — or a
separate reviewer — triage with `ax-review`. Stay out of the subject seat: you
orchestrate, audit, and triage; you never do the task yourself.

## Run manifest (store next to the session record)

```json
{
  "session_id": "a1b2c3d4",
  "tool": "anchor",
  "goal": "get a datasheet's specs onto a cited canvas",
  "harness": "claude-code",
  "harness_version": "2.1.x",
  "model": "<model id>",
  "tool_version": "0.2.3",
  "workspace": "/tmp/ax-run-a1b2c3d4",
  "contaminated": false,
  "started_at": "2026-06-10T09:00:00Z"
}
```

Write it to `$AX_REPORTS_DIR/<tool>/sessions/<utc>--<session_id>.json` (or the
`~/.claude/ax-reports/` default), so the reader can tie a batch of findings to
the exact harness, model, and tool version that produced them.
