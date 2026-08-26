"""The investigation half of the validator: the counter-hypothesis rule, made mechanical.

It cannot tell whether an alternative was the *right* one to test. It can tell whether
every class of alternative was tested, whether each carries the query that decided it,
whether the decomposition sums to the change it claims to explain, and whether the claim
is worded no stronger than the record supports.
"""

import copy
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import validate_findings as v  # noqa: E402


def fig(label="x", value=1.0, query="scratch/acme/investigate/s/q01.py"):
    return {"label": label, "value": value, "unit": "%", "period": "Q1 FY26 (Jan-Mar 2026, inclusive)",
            "query": query, "query_text": "import csv\n...", "rows_in": 5475, "rows_out": 100, "join": "none"}


def hyp(cls, status="ruled_out", **kw):
    h = {"hypothesis": f"{cls} alternative", "class": cls, "stated_by": "you",
         "would_be_true_if": "x > 5", "killed_if": "x < 1",
         "query": "scratch/acme/investigate/s/q02.py", "query_text": "import csv\n...",
         "rows_in": 5475, "rows_out": 42, "result": "x = 0.3", "status": status}
    h.update(kw)
    return h


def good() -> dict:
    return {
        "client": "acme", "scope_question": "q", "baseline": "b",
        "investigations": {
            "return-rate-doubled": {
                "finding": "return-rate-doubled", "title": "Return rate doubled",
                "investigated_on": "2026-08-26",
                "reverified": [dict(fig("return rate Q1 FY26", 19.1), recorded=19.1, rederived=19.1, match=True)],
                "claim": "Supplier B's own rate rise accounts for 9.93 of the 14.75 points; Supplier A's rise accounts for 3.04; interaction 1.82; mix -0.03.",
                "claim_strength": "established",
                "mechanism": "Sizing returns on Supplier B lines rose from ...",
                "decomposition": {
                    "metric": "apparel return rate", "components_by": "supplier",
                    "from": "Q3 FY24", "to": "Q2 FY26", "start": 11.85, "end": 26.60, "total_change": 14.75,
                    "terms": [
                        {"component": "Supplier A", "kind": "rate", "points": 3.04},
                        {"component": "Supplier B", "kind": "rate", "points": 9.93},
                        {"component": "all", "kind": "mix", "points": -0.03},
                        {"component": "all", "kind": "interaction", "points": 1.82},
                    ],
                    "sum_of_terms": 14.76, "reconciles": True,
                    "query": "scratch/acme/investigate/s/q03.py", "query_text": "import csv\n...",
                    "rows_in": 5475, "rows_out": 3000,
                },
                "counter_hypotheses": [
                    hyp("mix"), hyp("common-cause", "supported", size="3.04 points (Supplier A)"),
                    hyp("measurement"), hyp("named", "supported", size="9.93 points"),
                ],
                "allocation_pairs": [
                    {"label": "return cost per order",
                     "allocation_free": {"value": 150.0, "unit": "rupees", "period": "Q1 FY26", "query": "scratch/acme/investigate/s/q04.py"},
                     "allocated": {"value": 438.6, "unit": "rupees", "period": "Q1 FY26", "rule": "writedown spread by unit cost", "query": "scratch/acme/investigate/s/q04.py"},
                     "conclusion_changes": False},
                ],
                "evidence": [fig("Supplier B return rate Q2 FY26", 59.0)],
                "recoverable_at_most": "4.1 pts of contribution margin (q05_ceiling.py)",
                "open_questions": [],
                "status": "investigated",
            }
        },
    }


def one(d):
    return d["investigations"]["return-rate-doubled"]


class ValidateInvestigationTests(unittest.TestCase):
    def test_good_record_passes(self):
        self.assertEqual(v.validate_investigation(good()), [])

    def test_empty_counter_hypotheses_fails(self):
        d = good()
        one(d)["counter_hypotheses"] = []
        errors = v.validate_investigation(d)
        self.assertTrue(any("empty" in e for e in errors), errors)

    def test_every_class_must_be_covered(self):
        d = good()
        one(d)["counter_hypotheses"] = [hyp("named", "supported", size="9.93 points")]
        errors = v.validate_investigation(d)
        for cls in ("mix", "common-cause", "measurement"):
            self.assertTrue(any(f"class {cls!r}" in e for e in errors), errors)

    def test_not_applicable_needs_a_reason_and_counts_as_coverage(self):
        d = good()
        one(d)["counter_hypotheses"][0] = hyp("mix", "not_applicable", needs="")
        self.assertTrue(any("needs" in e for e in v.validate_investigation(d)))
        one(d)["counter_hypotheses"][0] = hyp("mix", "not_applicable", needs="the finding is a rate card step, no denominator")
        self.assertEqual(v.validate_investigation(d), [])

    def test_ruled_out_needs_a_query_and_a_result(self):
        d = good()
        one(d)["counter_hypotheses"][0]["query_text"] = ""
        self.assertTrue(any("query_text" in e for e in v.validate_investigation(d)))
        d = good()
        one(d)["counter_hypotheses"][0]["result"] = ""
        self.assertTrue(any("no result" in e for e in v.validate_investigation(d)))

    def test_soft_words_are_not_a_ruling_out(self):
        d = good()
        one(d)["counter_hypotheses"][0]["result"] = "unlikely to matter"
        self.assertTrue(any("soft word" in e for e in v.validate_investigation(d)))

    def test_established_claim_cannot_coexist_with_open_alternative(self):
        d = good()
        one(d)["counter_hypotheses"][2] = hyp("measurement", "not_ruled_out", needs="a refunds export by reason")
        errors = v.validate_investigation(d)
        self.assertTrue(any("not_ruled_out" in e and "established" in e for e in errors), errors)
        one(d)["claim_strength"] = "partial"
        self.assertEqual(v.validate_investigation(d), [])

    def test_supported_alternative_needs_a_size(self):
        d = good()
        one(d)["counter_hypotheses"][1]["size"] = ""
        self.assertTrue(any("no size" in e for e in v.validate_investigation(d)))

    def test_decomposition_must_sum_to_the_total(self):
        d = good()
        one(d)["decomposition"]["terms"][0]["points"] = 1.0  # Supplier A quietly shrunk
        errors = v.validate_investigation(d)
        self.assertTrue(any("not the whole denominator" in e for e in errors), errors)

    def test_decomposition_needs_mix_interaction_and_two_rate_terms(self):
        d = good()
        one(d)["decomposition"]["terms"] = [{"component": "Supplier B", "kind": "rate", "points": 14.75}]
        one(d)["decomposition"]["sum_of_terms"] = 14.75
        errors = v.validate_investigation(d)
        self.assertTrue(any("at least two" in e for e in errors), errors)
        self.assertTrue(any("no mix term" in e for e in errors), errors)
        self.assertTrue(any("no interaction term" in e for e in errors), errors)

    def test_decomposition_may_be_na_with_a_reason(self):
        d = good()
        one(d)["decomposition"] = "n/a - the finding is a rate-card step, not a rate over a denominator"
        self.assertEqual(v.validate_investigation(d), [])
        one(d)["decomposition"] = "skipped"
        self.assertTrue(any("decomposition must be" in e for e in v.validate_investigation(d)))

    def test_allocation_pair_needs_both_halves_and_a_rule(self):
        d = good()
        one(d)["allocation_pairs"][0]["allocated"]["rule"] = ""
        self.assertTrue(any("no rule" in e for e in v.validate_investigation(d)))
        d = good()
        del one(d)["allocation_pairs"][0]["allocation_free"]
        self.assertTrue(any("allocation_free" in e for e in v.validate_investigation(d)))

    def test_allocation_that_changes_the_conclusion_blocks_established(self):
        d = good()
        one(d)["allocation_pairs"][0]["conclusion_changes"] = True
        self.assertTrue(any("allocation pair changes the conclusion" in e for e in v.validate_investigation(d)))

    def test_unreproduced_figure_fails(self):
        d = good()
        one(d)["reverified"][0]["match"] = False
        self.assertTrue(any("did not reproduce" in e for e in v.validate_investigation(d)))

    def test_blocked_entry_is_exempt_but_must_have_a_mismatch(self):
        d = good()
        one(d)["status"] = "blocked"
        one(d)["counter_hypotheses"] = []
        errors = v.validate_investigation(d)
        self.assertTrue(any("blocked on what" in e for e in errors), errors)
        one(d)["reverified"][0]["match"] = False
        self.assertEqual(v.validate_investigation(d), [])

    def test_recoverable_at_most_is_a_figure_or_a_reasoned_not_derivable(self):
        d = good()
        one(d)["recoverable_at_most"] = "roughly 4 points"
        self.assertTrue(any("hedges" in e for e in v.validate_investigation(d)))
        one(d)["recoverable_at_most"] = "not derivable"
        self.assertTrue(any("no reason" in e for e in v.validate_investigation(d)))
        one(d)["recoverable_at_most"] = "not derivable - returns by value are not in the P&L; would need a refunds export"
        self.assertEqual(v.validate_investigation(d), [])

    def test_cli_detects_the_record_kind(self):
        # Same CLI, told apart by the top-level key - no second script.
        self.assertIn("investigations", v.main.__code__.co_consts)


if __name__ == "__main__":
    unittest.main()
