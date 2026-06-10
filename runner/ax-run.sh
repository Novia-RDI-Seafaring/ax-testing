#!/usr/bin/env bash
#
# ax-run — reference runner for the `ax-run` skill. Sets up a valid, hard-to-cheat
# AX test against a REAL harness, and audits the run for validity afterwards.
#
# This is optional tooling, not a skill: the skills themselves stay code-free.
# It deliberately does NOT launch the harness for you — it prepares an isolated
# workspace and prints the exact command to run, so the harness launch stays in
# your hands (a real headless agent with tool permissions should be started
# deliberately, not spawned from inside another agent).
#
# Usage:
#   ax-run.sh setup <tool> "<goal>"     # prepare an isolated run; prints next steps
#   ax-run.sh audit <workspace> <tool> <transcript>   # taint check after the run
#
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # repo root (skills/ live here)
cmd="${1:-}"; shift || true

mint()  { (command -v openssl >/dev/null && openssl rand -hex 4) || date +%s | tail -c 9; }
utcnow(){ date -u +%Y-%m-%dT%H%M%SZ; }

setup() {
  local tool="${1:?usage: setup <tool> \"<goal>\"}"
  local goal="${2:?usage: setup <tool> \"<goal>\"}"
  local session utc ws runrep
  session="$(mint)"; utc="$(utcnow)"
  ws="$(mktemp -d "${TMPDIR:-/tmp}/ax-run-${session}.XXXXXX")"
  runrep="$ws/ax-reports"
  mkdir -p "$ws/.claude/skills" "$runrep/$tool/sessions"

  # The subject only needs the reporting contract; ax-review/ax-run stay with you.
  cp -R "$here/skills/ax-report" "$ws/.claude/skills/ax-report"

  cat > "$runrep/$tool/sessions/$utc--$session.json" <<JSON
{
  "session_id": "$session",
  "tool": "$tool",
  "goal": "$goal",
  "harness": "claude-code",
  "harness_version": "<fill in>",
  "model": "<fill in>",
  "tool_version": "<fill in: run '$tool version' from the isolated venv>",
  "workspace": "$ws",
  "contaminated": false,
  "started_at": "$utc"
}
JSON

  cat <<TXT
ax-run set up an isolated run.

  session    : $session
  workspace  : $ws        (no source / tests / repo in reach)
  reports    : $runrep    (AX_REPORTS_DIR for this run)
  ax-report  : installed into the workspace as a project skill

1) Install the RELEASED wheel into an isolated venv (never an editable checkout,
   so the subject cannot read the implementation):

   uv venv "$ws/.venv" && uv pip install --python "$ws/.venv/bin/python" ${tool}-kb

2) Launch the REAL harness, headless, from the clean workspace. Give it ONLY the
   goal plus the black-box contract from the ax-run skill:

   cd "$ws" && AX_REPORTS_DIR="$runrep" PATH="$ws/.venv/bin:\$PATH" \\
     claude -p "Goal: $goal

You are a user of $tool. Use only its user-facing surface (CLI/--help, MCP,
its skill, public docs). Do NOT read its source, installed package files, or
tests; if you find yourself wanting to, that wanting is an AX finding — file it
with ax-report and continue from the user surface."

3) Audit the run for validity (point it at the subject's transcript):

   $(basename "$0") audit "$ws" "$tool" <path-to-transcript.jsonl>
TXT
}

# Scan a transcript for any read of the tool's source / installed package / tests.
# Prints VALID or CONTAMINATED and updates the manifest's "contaminated" flag.
audit() {
  local ws="${1:?usage: audit <workspace> <tool> <transcript>}"
  local tool="${2:?usage: audit <workspace> <tool> <transcript>}"
  local transcript="${3:?usage: audit <workspace> <tool> <transcript>}"
  [ -e "$transcript" ] || { echo "transcript not found: $transcript" >&2; exit 2; }

  # A source read = referencing a .py under the tool's package or repo, or its
  # tests, or introspecting __file__ to locate the implementation.
  local pattern="(site-packages/${tool}[/_-][^\"' ]*\.py|/${tool}/[^\"' ]*\.py|/${tool}[_-]kb/[^\"' ]*\.py|${tool}[^\"' ]*/tests/|${tool}\.__file__|import ${tool}[^A-Za-z].*__file__)"
  local hits
  hits="$(grep -aoEi "$pattern" "$transcript" 2>/dev/null | sort -u || true)"

  local manifest
  manifest="$(ls "$ws"/ax-reports/"$tool"/sessions/*.json 2>/dev/null | head -1 || true)"

  if [ -n "$hits" ]; then
    echo "CONTAMINATED — the subject reached for the tool's source:"
    echo "$hits" | sed 's/^/  - /'
    echo "(This is itself an AX finding: a user surface that drove the agent to the source.)"
    [ -n "$manifest" ] && _set_contaminated "$manifest" true && echo "manifest updated: contaminated=true"
    exit 1
  fi
  echo "VALID — no reads of $tool source / package / tests in the transcript."
  [ -n "$manifest" ] && _set_contaminated "$manifest" false
}

_set_contaminated() {  # portable in-place JSON flag flip (no jq dependency)
  local f="$1" val="$2"
  python3 - "$f" "$val" <<'PY' 2>/dev/null || true
import json,sys
f,val=sys.argv[1],sys.argv[2]=="true"
d=json.load(open(f)); d["contaminated"]=val
json.dump(d,open(f,"w"),indent=2)
PY
}

case "$cmd" in
  setup) setup "$@";;
  audit) audit "$@";;
  *) echo "usage: $(basename "$0") {setup <tool> \"<goal>\" | audit <workspace> <tool> <transcript>}" >&2; exit 2;;
esac
