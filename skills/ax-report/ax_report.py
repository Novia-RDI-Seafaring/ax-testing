#!/usr/bin/env python3
"""ax-report — file and triage Agent Experience (AX) reports.

A small, dependency-free CLI. Agents call `file` to record evidenced friction
with a tool; humans (or a triage agent) call `list` / `show` to review and
promote the real ones into the tool's issue tracker.

Storage: one JSON file per report under the reports directory (default
``~/.claude/ax-reports/<tool>/``; override with ``AX_REPORTS_DIR``). Reports are
never overwritten, so the corpus is append-only and safe to read concurrently.

See ``schema/ax-report.schema.json`` for the shape and ``heuristics.md`` for the
``heuristic`` vocabulary.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "0.1"
HEURISTICS = {
    "contract_truth",
    "pure_machine_output",
    "single_round_trip",
    "honest_verdicts",
    "discoverability",
    "self_correcting_errors",
    "other",
}
SEVERITIES = {"low", "medium", "high", "critical"}
KINDS = {"friction", "feature_request"}
# Fields an agent supplies; the rest (id, created_at, schema_version) are stamped.
_INPUT_FIELDS = (
    "tool", "surface", "kind", "heuristic", "severity",
    "task", "expected", "actual", "workaround", "suggestion",
    "agent", "session_hint",
)


def reports_dir() -> Path:
    return Path(os.environ.get("AX_REPORTS_DIR", "~/.claude/ax-reports")).expanduser()


def validate(report: dict) -> list[str]:
    """Return a list of problems; empty means valid."""
    problems: list[str] = []
    if not str(report.get("tool", "")).strip():
        problems.append("tool is required")
    kind = report.get("kind")
    if kind not in KINDS:
        problems.append(f"kind must be one of {sorted(KINDS)}")
    if kind == "friction":
        for field in ("task", "expected", "actual"):
            if not str(report.get(field, "")).strip():
                problems.append(f"{field} is required for a friction report (give evidence)")
        if report.get("heuristic") not in HEURISTICS:
            problems.append(f"heuristic must be one of {sorted(HEURISTICS)}")
        if report.get("severity") not in SEVERITIES:
            problems.append(f"severity must be one of {sorted(SEVERITIES)}")
    if kind == "feature_request" and not str(report.get("suggestion", "")).strip():
        problems.append("suggestion is required for a feature_request")
    if "heuristic" in report and report["heuristic"] not in HEURISTICS:
        problems.append(f"heuristic must be one of {sorted(HEURISTICS)}")
    if "severity" in report and report["severity"] not in SEVERITIES:
        problems.append(f"severity must be one of {sorted(SEVERITIES)}")
    return problems


def _collect(args: argparse.Namespace) -> dict:
    """Build a report dict from --json stdin and/or flags (flags win)."""
    report: dict = {}
    if args.json:
        raw = sys.stdin.read() if args.json == "-" else Path(args.json).read_text()
        loaded = json.loads(raw)
        if not isinstance(loaded, dict):
            raise ValueError("--json must provide a JSON object")
        report.update({k: v for k, v in loaded.items() if k in _INPUT_FIELDS})
    for field in _INPUT_FIELDS:
        value = getattr(args, field, None)
        if value is not None:
            report[field] = value
    return report


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_file(args: argparse.Namespace) -> int:
    report = _collect(args)
    problems = validate(report)
    if problems:
        print("Report is not valid:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    report["schema_version"] = SCHEMA_VERSION
    report["id"] = str(uuid.uuid4())
    report["created_at"] = _now_iso()
    out_dir = reports_dir() / report["tool"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{report['created_at'].replace(':', '')}-{report['id'][:8]}.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Filed {report['kind']} report {report['id']}")
    print(f"  {path}")
    return 0


def _iter_reports(tool: str | None):
    root = reports_dir()
    if not root.exists():
        return
    pattern = f"{tool}/*.json" if tool else "*/*.json"
    for path in sorted(root.glob(pattern)):
        try:
            yield path, json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue


def cmd_list(args: argparse.Namespace) -> int:
    rows = 0
    for _path, r in _iter_reports(args.tool):
        if args.kind and r.get("kind") != args.kind:
            continue
        if args.severity and r.get("severity") != args.severity:
            continue
        line = (
            f"{r.get('created_at', '?')}  {r.get('id', '?')[:8]}  "
            f"{r.get('tool', '?')}  {r.get('kind', '?'):<15}  "
            f"{(r.get('severity') or '-'):<8}  {(r.get('heuristic') or '-'):<22}  "
            f"{r.get('surface', '')}"
        )
        print(line)
        rows += 1
    if rows == 0:
        print(f"No reports under {reports_dir()}", file=sys.stderr)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    for _path, r in _iter_reports(None):
        if r.get("id", "").startswith(args.id):
            print(json.dumps(r, indent=2))
            return 0
    print(f"No report with id starting {args.id!r}", file=sys.stderr)
    return 1


def cmd_validate(args: argparse.Namespace) -> int:
    raw = sys.stdin.read() if args.path == "-" else Path(args.path).read_text()
    problems = validate(json.loads(raw))
    if problems:
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("valid")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ax-report", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    f = sub.add_parser("file", help="File a new AX report.")
    f.add_argument("--json", help="Read fields from a JSON object ('-' for stdin).")
    for field in _INPUT_FIELDS:
        f.add_argument(f"--{field.replace('_', '-')}", dest=field, default=None)
    f.set_defaults(func=cmd_file)

    ls = sub.add_parser("list", help="List filed reports (triage).")
    ls.add_argument("--tool")
    ls.add_argument("--kind", choices=sorted(KINDS))
    ls.add_argument("--severity", choices=sorted(SEVERITIES))
    ls.set_defaults(func=cmd_list)

    sh = sub.add_parser("show", help="Show one report by id prefix.")
    sh.add_argument("id")
    sh.set_defaults(func=cmd_show)

    v = sub.add_parser("validate", help="Validate a report file ('-' for stdin).")
    v.add_argument("path")
    v.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
