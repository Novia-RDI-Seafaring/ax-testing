"""Tests for ax_report — run with `python3 -m unittest` (no dependencies)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "ax-report"))

import ax_report  # noqa: E402


class ValidateTests(unittest.TestCase):
    def test_friction_requires_evidence(self):
        problems = ax_report.validate({"tool": "anchor", "kind": "friction"})
        joined = " ".join(problems)
        for field in ("task", "expected", "actual", "heuristic", "severity"):
            self.assertIn(field, joined)

    def test_valid_friction_passes(self):
        report = {
            "tool": "anchor", "kind": "friction", "heuristic": "honest_verdicts",
            "severity": "high", "task": "t", "expected": "e", "actual": "a",
        }
        self.assertEqual(ax_report.validate(report), [])

    def test_feature_request_requires_suggestion(self):
        self.assertIn(
            "suggestion", " ".join(ax_report.validate({"tool": "x", "kind": "feature_request"}))
        )

    def test_bad_heuristic_and_severity_rejected(self):
        problems = ax_report.validate({
            "tool": "x", "kind": "friction", "task": "t", "expected": "e",
            "actual": "a", "heuristic": "nope", "severity": "huge",
        })
        self.assertTrue(any("heuristic" in p for p in problems))
        self.assertTrue(any("severity" in p for p in problems))


class FileRoundTripTests(unittest.TestCase):
    def test_file_stamps_and_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            ax_report.os.environ["AX_REPORTS_DIR"] = tmp
            args = ax_report.build_parser().parse_args([
                "file", "--tool", "anchor", "--kind", "friction",
                "--heuristic", "discoverability", "--severity", "high",
                "--task", "find search", "--expected", "skill lists search",
                "--actual", "skill omitted it", "--workaround", "ran --help",
            ])
            self.assertEqual(args.func(args), 0)
            files = list(Path(tmp).glob("anchor/*.json"))
            self.assertEqual(len(files), 1)
            report = json.loads(files[0].read_text())
            self.assertEqual(report["schema_version"], ax_report.SCHEMA_VERSION)
            self.assertTrue(report["id"])
            self.assertTrue(report["created_at"].endswith("Z"))


if __name__ == "__main__":
    unittest.main()
