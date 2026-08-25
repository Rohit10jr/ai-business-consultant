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
        "magnitude": {"value": 15.2, "unit": "pts", "period": "Q3 FY24 -> Q2 FY26"},
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


if __name__ == "__main__":
    unittest.main()
