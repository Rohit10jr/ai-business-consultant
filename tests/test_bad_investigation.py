"""The deliberately bad investigation must be bad in exactly one way.

fixtures/bad-investigation/README.md: every figure true and sourced, so /review cannot
win by finding a missing query; the flaw is the inference, and Supplier A - a fifth of
the rise - appears nowhere. If this fixture ever fails the validator for any reason other
than its empty counter-hypothesis list, phase 4's gate is measuring the grounding checker
again instead of adversarial reasoning.
"""

import filecmp
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "fixtures" / "bad-investigation"
sys.path.insert(0, str(REPO_ROOT / "tools"))
import validate_findings as v  # noqa: E402


class BadInvestigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((FIXTURE / "investigation.json").read_text(encoding="utf-8"))
        cls.text = (FIXTURE / "investigation.json").read_text(encoding="utf-8")
        cls.inv = cls.data["investigations"]["return-rate-doubled"]

    def test_checked_in_json_matches_a_fresh_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            # build.py writes next to itself; run a copy of the builder in a scratch
            # tree that carries the same query scripts.
            scratch = Path(tmp) / "bad-investigation"
            scratch.mkdir()
            (scratch / "queries").mkdir()
            for p in (FIXTURE / "queries").glob("*.py"):
                (scratch / "queries" / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
            (scratch / "build.py").write_text((FIXTURE / "build.py").read_text(encoding="utf-8"), encoding="utf-8")
            subprocess.run([sys.executable, str(scratch / "build.py")], check=True, capture_output=True)
            self.assertTrue(filecmp.cmp(scratch / "investigation.json", FIXTURE / "investigation.json", shallow=False),
                            "investigation.json differs from a fresh build - regenerate with fixtures/bad-investigation/build.py")

    def test_fails_the_validator_only_on_the_missing_alternatives(self):
        errors = v.validate_investigation(self.data)
        self.assertEqual(len(errors), 5, errors)
        self.assertTrue(all("counter" in e or "class" in e for e in errors), errors)

    def test_supplier_a_appears_nowhere(self):
        self.assertNotIn("Supplier A", self.text)

    def test_claims_the_whole_rise_for_supplier_b(self):
        self.assertIn("14.75", self.inv["claim"])
        self.assertIn("Supplier B", self.inv["claim"])
        self.assertEqual(self.inv["claim_strength"], "established")
        self.assertEqual(self.inv["counter_hypotheses"], [])

    def test_every_figure_carries_its_script_verbatim(self):
        scripts = {p.stem: p.read_text(encoding="utf-8") for p in (FIXTURE / "queries").glob("*.py")}
        figures = self.inv["evidence"] + self.inv["reverified"] + [self.inv["recoverable_at_most"]] + self.inv["decompositions"]
        for fig in figures:
            name = Path(fig["query"]).stem
            self.assertEqual(fig["query_text"], scripts[name], f"{fig.get('label', name)} query_text is not the script")

    def test_decomposes_by_category_not_supplier(self):
        # The lens that flatters the story. A supplier table would show Supplier A.
        self.assertEqual([d["components_by"] for d in self.inv["decompositions"]], ["category"])


if __name__ == "__main__":
    unittest.main()
