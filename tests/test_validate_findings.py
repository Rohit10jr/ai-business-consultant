"""The findings validator is the mechanical half of phase 2's gate item 5."""

import copy
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import validate_findings as v  # noqa: E402


def good() -> dict:
    figure = {
        "label": "return rate", "value": 27.1, "unit": "%", "period": "Q2 FY26 (Apr-Jun 2026, inclusive)",
        "query": "scratch/acme/discover/q03_returns.py", "query_text": "import csv\n...",
        "rows_in": 5475, "rows_out": 612, "join": "none",
    }
    finding = {
        "title": "Apparel return rate 12% -> 27%", "branch": "returns",
        "magnitude": {"value": 15.2, "unit": "pts", "period": "Q3 FY24 -> Q2 FY26",
                      "baseline_metric": "2.1 pts of contribution margin (q03_returns.py)"},
        "figures": [figure], "sources": ["orders/orders_export.csv"],
        "derivation_kind": "single-file", "known_to_client": False,
        "checks": {"sourced": True, "deduplicated": True, "dates_normalised": True, "joins_counted": True,
                   "reconciles": "category returns sum to total returns 1,204 = 1,204",
                   "second_derivation": "agrees", "zero_price_lines_explained": "n/a"},
        "mix_at_boundaries": "Supplier B 21% -> 25% of apparel lines",
        "first_seen": "2026-08-25", "status": "new",
    }
    return {
        "client": "acme", "discovered_on": "2026-08-25", "scope_question": "q", "baseline": "b",
        "out_of_scope": ["pricing"],
        "preflight": {"orders/orders_export.csv": {"rows_raw": 5476, "rows_deduplicated": 5475,
                                                   "duplicate_rows": 1, "date_formats": {}}},
        "issue_tree": {"returns": ["h1"]}, "findings": {"apparel-returns": finding},
        "not_recorded": [], "corpus_notes": [],
    }


class ValidateTests(unittest.TestCase):
    def test_good_record_passes(self):
        self.assertEqual(v.validate(good()), [])

    def test_missing_query_text_fails(self):
        d = good()
        d["findings"]["apparel-returns"]["figures"][0]["query_text"] = ""
        self.assertTrue(any("query_text" in e for e in v.validate(d)))

    def test_row_counts_must_be_integers(self):
        d = good()
        d["findings"]["apparel-returns"]["figures"][0]["rows_out"] = "about 600"
        self.assertTrue(any("rows_out" in e for e in v.validate(d)))

    def test_false_check_fails(self):
        d = good()
        d["findings"]["apparel-returns"]["checks"]["joins_counted"] = False
        self.assertTrue(any("joins_counted" in e for e in v.validate(d)))

    def test_hedged_check_fails(self):
        d = good()
        d["findings"]["apparel-returns"]["checks"]["reconciles"] = "roughly ties to the total"
        self.assertTrue(any("hedges" in e for e in v.validate(d)))

    def test_stated_finding_must_say_so(self):
        d = good()
        f = d["findings"]["apparel-returns"]
        f["derivation_kind"] = "stated"
        errors = v.validate(d)
        self.assertTrue(any("say so in its title" in e for e in errors))
        self.assertTrue(any("second derivation" in e for e in errors))

    def test_rank_keys_require_ranked_status(self):
        d = good()
        d["findings"]["apparel-returns"]["rank_score"] = 80
        self.assertTrue(any("rank_*" in e for e in v.validate(d)))
        d["findings"]["apparel-returns"]["status"] = "ranked"
        self.assertEqual(v.validate(d), [])

    def test_no_figures_fails(self):
        d = good()
        d["findings"]["apparel-returns"]["figures"] = []
        self.assertTrue(any("no figures" in e for e in v.validate(d)))

    def test_dedup_greater_than_raw_fails(self):
        d = copy.deepcopy(good())
        d["preflight"]["orders/orders_export.csv"]["rows_deduplicated"] = 9999
        self.assertTrue(any("rows_deduplicated" in e for e in v.validate(d)))



class SecondDerivationVocabularyTests(unittest.TestCase):
    """Fix 3: "partial" is admitted, but only when it says which half is solid."""

    def _with(self, value):
        d = good()
        d["findings"]["apparel-returns"]["checks"]["second_derivation"] = value
        return d

    def test_structured_partial_passes(self):
        d = self._with("partial - the before-marketing figure does not depend on any "
                       "allocation; the after-marketing figure allocates channel spend by order share")
        self.assertEqual(v.validate(d), [])

    def test_bare_partial_fails(self):
        errors = v.validate(self._with("partial"))
        self.assertTrue(any("escape hatch" in e for e in errors), errors)

    def test_freeform_answer_fails(self):
        errors = v.validate(self._with("checked it and it looked fine"))
        self.assertTrue(any("must begin with" in e for e in errors), errors)

    def test_agrees_and_not_possible_still_pass(self):
        self.assertEqual(v.validate(self._with("agrees")), [])
        self.assertEqual(
            v.validate(self._with("not possible - only pnl_monthly.csv carries it; checked cogs_by_sku.csv")),
            [])


class BaselineMetricTests(unittest.TestCase):
    """Fix 2: a finding with no size in the baseline's unit ranks as if it were small."""

    def test_missing_baseline_metric_fails(self):
        d = good()
        del d["findings"]["apparel-returns"]["magnitude"]["baseline_metric"]
        errors = v.validate(d)
        self.assertTrue(any("baseline_metric missing" in e for e in errors), errors)

    def test_not_derivable_needs_a_reason(self):
        d = good()
        d["findings"]["apparel-returns"]["magnitude"]["baseline_metric"] = "not derivable"
        errors = v.validate(d)
        self.assertTrue(any("no reason" in e for e in errors), errors)

    def test_not_derivable_with_a_reason_passes(self):
        d = good()
        d["findings"]["apparel-returns"]["magnitude"]["baseline_metric"] = (
            "not derivable - no file carries returns by value before 2024; would need a "
            "refunds export"
        )
        self.assertEqual(v.validate(d), [])



class VetoRecordTests(unittest.TestCase):
    """A veto has to survive a reader who does not know the rulebook."""

    def vetoed(self, **overrides):
        d = good()
        f = d["findings"]["apparel-returns"]
        f["status"] = "vetoed"
        f["rank_veto"] = "restates-the-baseline"
        f["rank_veto_reason"] = ("its endpoint 19.72% is the figure scope.md records as the "
                                 "baseline, at the same whole-business aggregation")
        f["rank_date"] = "2026-08-26"
        f.update(overrides)
        return d

    def test_slug_plus_sentence_passes(self):
        self.assertEqual(v.validate(self.vetoed()), [])

    def test_missing_reason_fails(self):
        errors = v.validate(self.vetoed(rank_veto_reason=""))
        self.assertTrue(any("no rank_veto_reason" in e for e in errors), errors)

    def test_reason_that_only_restates_the_rule_fails(self):
        # The exact shape observed in the first live run: the slug in both fields.
        errors = v.validate(self.vetoed(rank_veto_reason="restates the baseline"))
        self.assertTrue(any("restates the rule" in e for e in errors), errors)

    def test_unrecognised_slug_fails(self):
        errors = v.validate(self.vetoed(rank_veto="looked-unimportant"))
        self.assertTrue(any("is not one of" in e for e in errors), errors)

    def test_vetoed_finding_may_not_carry_a_score(self):
        errors = v.validate(self.vetoed(rank_score=76))
        self.assertTrue(any("not scored" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
