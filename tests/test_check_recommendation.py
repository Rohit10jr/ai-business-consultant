"""check_recommendation.py: the recommendation's figures come from the investigation,
the baseline, or arithmetic shown over those - nowhere else."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import check_recommendation as c  # noqa: E402

SCOPE = "# Scope\n\nquestion:   q\nbaseline:   19.7% contribution margin, Q1 FY26 (Jan-Mar 2026, inclusive)\n"
INV = {
    "investigations": {
        "a": {
            "reverified": [], "decompositions": "n/a - x", "counter_hypotheses": [{"size": "3.04 points", "result": "x"}],
            "allocation_pairs": [], "evidence": [{"value": 9.93}, {"value": 19880.79}],
            "recoverable_at_most": {"value": 2.94},
        }
    }
}


class CheckTests(unittest.TestCase):
    def test_recorded_figures_pass(self):
        text = "Supplier B accounts for 9.93 pts; the ceiling is 2.94 pts against a 19.7% baseline, 19,880.79 rupees a quarter."
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_unrecorded_figure_fails(self):
        text = "The fix is worth 4.1 pts of margin."
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("'4.1'" in e for e in errors), errors)

    def test_shown_arithmetic_over_recorded_terms_passes(self):
        text = "Option A recovers 12.97 pts.\n\n## Arithmetic\n\n- 12.97 = 9.93 + 3.04\n\n## Next\n"
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_arithmetic_over_an_unrecorded_term_fails(self):
        text = "Option A recovers 14.03 pts.\n\n## Arithmetic\n\n- 14.03 = 9.93 + 4.1\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("not recorded figures" in e for e in errors), errors)
        self.assertTrue(any("'14.03'" in e for e in errors), errors)

    def test_years_quarters_and_counts_are_ignored(self):
        text = "Between Q3 FY24 and 2026 there are 3 options and 2 quarters."
        self.assertEqual(c.check(text, INV, SCOPE), [])


if __name__ == "__main__":
    unittest.main()
