"""check_recommendation.py: figures come from the investigation, the baseline, or shown
arithmetic; ceilings are rupees from recoverable_at_most; movements are recomputed ratios
and never a sum of movements. Inputs are hand-written - phase 6 runs nothing."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import check_recommendation as c  # noqa: E402

SCOPE = "# Scope\n\nquestion:   q\nbaseline:   19.72% contribution margin, Q1 FY26 (Jan-Mar 2026, inclusive)\n"


def cause(rupees, num_delta, den_delta, from_pct, to_pct, evidence=()):
    return {
        "reverified": [], "decompositions": "n/a - x", "counter_hypotheses": [],
        "allocation_pairs": [], "evidence": [{"value": v} for v in evidence],
        "recoverable_at_most": {"value": rupees, "unit": "rupees"},
        "baseline_movement_at_most": {
            "numerator_from": 124540.03, "numerator_to": round(124540.03 + num_delta, 2), "numerator_delta": num_delta,
            "denominator_from": 631425.85, "denominator_to": round(631425.85 + den_delta, 2), "denominator_delta": den_delta,
            "from": from_pct, "to": to_pct, "delta": round(to_pct - from_pct, 2), "unit": "pts of contribution margin",
        },
    }


# Acme's Supplier B cause by hand (+5.02), and a second, smaller cause that moves only
# the numerator (+2.15). Their movements do not add: jointly they are +6.98, not +7.17.
INV = {
    "investigations": {
        "supplier-b": cause(46121.67, 46121.67, 58370.00, 19.72, 24.74, evidence=[9.93, 14.75]),
        "meta": cause(13537.11, 13537.11, 0.0, 19.72, 21.87),
    }
}


class FigureTests(unittest.TestCase):
    def test_recorded_figures_pass(self):
        text = "Supplier B is worth 46,121.67 rupees; the margin moves 19.72% to 24.74%, +5.02 pts."
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_unrecorded_figure_fails(self):
        errors = c.check("The fix is worth 4.1 pts of margin.", INV, SCOPE)
        self.assertTrue(any("'4.1'" in e for e in errors), errors)

    def test_baseline_date_tokens_are_not_figures(self):
        errors = c.check("This saves 26% of something unsupported.", INV, SCOPE)
        self.assertTrue(any("'26'" in e for e in errors), errors)


class ArithmeticTests(unittest.TestCase):
    def test_arithmetic_result_is_computed_not_trusted(self):
        text = "Worth 100 pts.\n\n## Arithmetic\n\n- 100 = 9.93 + 14.75\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("the terms make 24.68" in e for e in errors), errors)

    def test_arithmetic_over_an_unrecorded_term_fails(self):
        text = "Worth 14.03 pts.\n\n## Arithmetic\n\n- 14.03 = 9.93 + 4.1\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("not recorded figures" in e for e in errors), errors)


class CeilingTests(unittest.TestCase):
    def test_rupee_ceiling_from_recoverable_passes(self):
        text = "### Option A — x\n- Ceiling: ₹46,121.67 [S · recoverable_at_most]\n"
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_ceiling_in_points_is_rejected_even_when_the_number_exists(self):
        # 5.02 is a real movement figure; it still may not be called a ceiling.
        text = "### Option A — x\n- Ceiling: 5.02 pts of contribution margin\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("stated in points or percent" in e for e in errors), errors)

    def test_frozen_denominator_figure_cannot_be_a_ceiling(self):
        # 46,121.67 / 631,425.85 = 7.30: the phase 3-5 bug, written out.
        text = "### Option A — x\n- Ceiling: 7.30 pts [Arithmetic]\n\n## Arithmetic\n\n- 7.30 = 100 × 46,121.67 / 631,425.85\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("stated in points or percent" in e for e in errors), errors)

    def test_ceiling_from_a_finding_magnitude_fails(self):
        text = "### Option A — x\n- Ceiling: ₹14.75\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("not a recoverable_at_most value" in e for e in errors), errors)

    def test_rupee_ceilings_add(self):
        text = ("### Option B — x\n- Ceiling: ₹59,658.78 [Arithmetic]\n\n## Arithmetic\n\n"
                "- 59,658.78 = 46,121.67 + 13,537.11\n")
        self.assertEqual(c.check(text, INV, SCOPE), [])


class MovementTests(unittest.TestCase):
    def test_single_cause_movement_from_the_record_passes(self):
        text = "### Option A — x\n- Ceiling: ₹46,121.67\n- Movement: 19.72% → 24.74% (+5.02 pts) [S · baseline_movement_at_most]\n"
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_sum_of_two_movements_is_rejected(self):
        # 5.02 + 2.15 = 7.17: the second-order bug TASK.md names.
        text = ("### Option B — x\n- Ceiling: ₹59,658.78 [Arithmetic]\n- Movement: +7.17 pts [Arithmetic]\n\n"
                "## Arithmetic\n\n- 59,658.78 = 46,121.67 + 13,537.11\n- 7.17 = 5.02 + 2.15\n")
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("do not add" in e for e in errors), errors)

    def test_joint_recomputation_from_both_terms_passes(self):
        # (124,540.03 + 46,121.67 + 13,537.11) / (631,425.85 + 58,370.00 + 0) = 26.70%; +6.98 pts.
        text = ("### Option B — x\n- Ceiling: ₹59,658.78 [Arithmetic]\n"
                "- Movement: 19.72% → 26.70% (+6.98 pts) [Arithmetic]\n\n## Arithmetic\n\n"
                "- 59,658.78 = 46,121.67 + 13,537.11\n"
                "- 26.70 = 100 × (124,540.03 + 46,121.67 + 13,537.11) / (631,425.85 + 58,370.00)\n"
                "- 6.98 = 26.70 − 19.72\n")
        self.assertEqual(c.check(text, INV, SCOPE), [])

    def test_movement_figure_from_nowhere_fails(self):
        text = "### Option A — x\n- Ceiling: ₹46,121.67\n- Movement: +6.50 pts\n"
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("not a baseline_movement_at_most figure" in e for e in errors), errors)

    def test_frozen_denominator_ratio_is_not_a_movement(self):
        # Review blocker: any `/` counted as a recomputed ratio, so the old bug passed as a
        # Movement line. A rebuilt ratio starts from numerator_from and denominator_from
        # and adds a delta to each.
        text = ("### Option A — x\n- Ceiling: ₹46,121.67\n- Movement: +7.30 pts [Arithmetic]\n\n"
                "## Arithmetic\n\n- 7.30 = 100 × 46,121.67 / 631,425.85\n")
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("not a baseline_movement_at_most figure or a ratio" in e for e in errors), errors)
        text = ("### Option A — x\n- Movement: 100 pts [Arithmetic]\n\n## Arithmetic\n\n- 100 = 100 × 631,425.85 / 631,425.85\n")
        self.assertTrue(c.check(text, INV, SCOPE))

    def test_points_of_the_baseline_in_prose_are_policed(self):
        # Review blocker, second half: narrative "7.30% of revenue" backed by Arithmetic.
        text = ("Supplier B is worth 7.30% of revenue.\n\n## Arithmetic\n\n- 7.30 = 100 × 46,121.67 / 631,425.85\n")
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("stated as points of the baseline" in e for e in errors), errors)
        text = ("Supplier B is worth 7.30 pts.\n\n## Arithmetic\n\n- 7.30 = 100 × 46,121.67 / 631,425.85\n")
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(any("exists only through the Arithmetic section" in e for e in errors), errors)
        # A recorded decomposition term quoted in points is ordinary evidence.
        self.assertEqual(c.check("Supplier A accounts for 9.93 points of the rise.", INV, SCOPE), [])

    def test_movement_from_a_non_ratio_arithmetic_line_fails(self):
        # An Arithmetic line without a division is not a recomputed ratio.
        text = ("### Option A — x\n- Ceiling: ₹46,121.67\n- Movement: +7.30 pts [Arithmetic]\n\n"
                "## Arithmetic\n\n- 7.30 = 5.02 + 2.28\n")
        errors = c.check(text, INV, SCOPE)
        self.assertTrue(errors, "a movement laundered through a non-ratio line must fail")


if __name__ == "__main__":
    unittest.main()
