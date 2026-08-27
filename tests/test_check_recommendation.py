"""check_recommendation.py: the recommendation's figures come from the investigation,
the baseline, or arithmetic shown over those - nowhere else - and ceilings come from
recoverable_at_most alone."""

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
            "allocation_pairs": [], "evidence": [{"value": 9.93}, {"value": 19880.79}, {"value": 14.75}],
            "recoverable_at_most": {"value": 2.94},
        },
        "b": {
            "reverified": [], "decompositions": "n/a - x", "counter_hypotheses": [],
            "allocation_pairs": [], "evidence": [{"value": 5.66}],
            "recoverable_at_most": {"value": 5.21},
        },
    }
}


class FigureTests(unittest.TestCase):
    def test_recorded_figures_pass(self):
        text = "Supplier B accounts for 9.93 pts; the ceiling is 2.94 pts against a 19.7% baseline, 19,880.79 rupees a quarter."
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_unrecorded_figure_fails(self):
        errors = c.check("The fix is worth 4.1 pts of margin.", INV, SCOPE)
        self.assertTrue(any("'4.1'" in e for e in errors), errors)

    def test_baseline_date_tokens_are_not_figures(self):
        # Review finding: "FY26" must not make 26 an allowed value.
        errors = c.check("This saves 26% of something unsupported.", INV, SCOPE)
        self.assertTrue(any("'26'" in e for e in errors), errors)

    def test_years_quarters_and_counts_are_ignored(self):
        self.assertEqual(c.check("Between Q3 FY24 and 2026 there are 3 options and 2 quarters.", INV, SCOPE), [])


class ArithmeticTests(unittest.TestCase):
    def test_shown_arithmetic_over_recorded_terms_passes(self):
        text = "Together 12.97 pts.\n\n## Arithmetic\n\n- 12.97 = 9.93 + 3.04\n\n## Next\n"
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_arithmetic_result_is_computed_not_trusted(self):
        # Review blocker: `100 = 9.93 + 3.04` used to whitelist 100.
        text = "Worth 100 pts.\n\n## Arithmetic\n\n- 100 = 9.93 + 3.04\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("the terms make 12.97" in e for e in errors), errors)
        self.assertTrue(any("'100'" in e for e in errors), errors)

    def test_arithmetic_over_an_unrecorded_term_fails(self):
        text = "Worth 14.03 pts.\n\n## Arithmetic\n\n- 14.03 = 9.93 + 4.1\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("not recorded figures" in e for e in errors), errors)

    def test_units_in_the_expression_are_tolerated(self):
        text = "Together 8.15 pts.\n\n## Arithmetic\n\n- 8.15 pts = 2.94 pts + 5.21 pts\n"
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_non_arithmetic_right_hand_side_fails(self):
        text = "Worth 12.97 pts.\n\n## Arithmetic\n\n- 12.97 = about the sum of 9.93 and 3.04 and some judgement\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(errors, "a prose right-hand side must not launder a figure")


class CeilingTests(unittest.TestCase):
    def test_ceiling_from_recoverable_at_most_passes(self):
        text = "### Option A — x\n- Ceiling: 2.94 pts of net revenue [Arithmetic]\n"
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_ceiling_from_a_finding_magnitude_fails(self):
        # Review finding: 14.75 is recorded (a magnitude) but it is not a ceiling.
        text = "### Option A — x\n- Ceiling: 14.75 pts of net revenue\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("not a recoverable_at_most value" in e for e in errors), errors)

    def test_ceiling_from_arithmetic_over_recoverables_passes(self):
        text = "### Option A — x\n- Ceiling: 8.15 pts [Arithmetic]\n\n## Arithmetic\n\n- 8.15 = 2.94 + 5.21\n"
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_ceiling_from_arithmetic_mixing_in_a_magnitude_fails(self):
        text = "### Option A — x\n- Ceiling: 17.69 pts [Arithmetic]\n\n## Arithmetic\n\n- 17.69 = 2.94 + 14.75\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("not a recoverable_at_most value" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
