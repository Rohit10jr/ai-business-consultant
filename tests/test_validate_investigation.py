"""The investigation half of the validator: the counter-hypothesis rule, made mechanical.

It cannot tell whether an alternative was the *right* one to test. It can tell whether
every class of alternative was tested, whether each carries the query that decided it,
whether the decomposition sums to the change it claims to explain, whether every number
in the claim exists in the record, and whether the claim is worded no stronger than the
record supports.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import validate_findings as v  # noqa: E402

Q = "scratch/acme/investigate/s/q01.py"


def fig(label="x", value=1.0, query=Q, **kw):
    f = {"label": label, "value": value, "unit": "%", "period": "Q1 FY26 (Jan-Mar 2026, inclusive)",
         "query": query, "query_text": "import csv\n...", "rows_in": 5475, "rows_out": 100, "join": "none"}
    f.update(kw)
    return f


def hyp(cls, status="ruled_out", **kw):
    h = {"hypothesis": f"{cls} alternative", "class": cls, "stated_by": "you",
         "would_be_true_if": "x > 5 points", "killed_if": "x < 1 point",
         "query": "scratch/acme/investigate/s/q02.py", "query_text": "import csv\n...",
         "rows_in": 5475, "rows_out": 42, "result": "x = 0.3 points", "status": status}
    if cls in ("mix", "common-cause"):
        h["field"] = "supplier"
    h.update(kw)
    return h


def decomposition(**kw):
    d = {
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
    }
    d.update(kw)
    return d


def good() -> dict:
    return {
        "client": "acme", "scope_question": "q", "baseline": "b",
        "investigations": {
            "return-rate-doubled": {
                "finding": "return-rate-doubled", "title": "Return rate doubled",
                "investigated_on": "2026-08-26",
                "reverified": [fig("return rate Q1 FY26", 19.1, recorded=19.1, rederived=19.1, match=True)],
                "claim": "Supplier B's own rate rise accounts for 9.93 of the 14.75 points; Supplier A's rise accounts for 3.04; interaction 1.82; mix -0.03.",
                "claim_strength": "established",
                "mechanism": "Sizing returns on Supplier B lines rose to 59.0% of lines while Supplier A moved to 15.8%.",
                "preregistered_in": "scratch/acme/investigate/s/hypotheses.json",
                "decompositions": [decomposition()],
                "counter_hypotheses": [
                    hyp("mix"), hyp("common-cause", "supported", size="3.04 points (Supplier A)"),
                    hyp("measurement"), hyp("named", "supported", size="9.93 points"),
                ],
                "allocation_dependence": "none - return_handling is recorded per line in orders_export.csv (returned, line_value) and cogs_by_sku.csv (unit_cost_2023); no shared cost is spread",
                "allocation_pairs": [],
                "evidence": [fig("Supplier B return rate Q2 FY26", 59.0), fig("Supplier A return rate Q2 FY26", 15.8)],
                "recoverable_at_most": fig("ceiling", 4.1, unit="pts of contribution margin", query="scratch/acme/investigate/s/q05.py"),
                "open_questions": [],
                "status": "investigated",
            }
        },
    }


def one(d):
    return d["investigations"]["return-rate-doubled"]


def pair(**kw):
    p = {"label": "return cost per order",
         "allocation_free": fig("free", 150.0, unit="rupees", query="scratch/acme/investigate/s/q04.py"),
         "allocated": fig("alloc", 438.6, unit="rupees", query="scratch/acme/investigate/s/q04.py", rule="writedown spread by unit cost"),
         "conclusion_changes": False}
    p.update(kw)
    return p


class ValidateInvestigationTests(unittest.TestCase):
    def test_good_record_passes(self):
        self.assertEqual(v.validate_investigation(good()), [])

    def test_empty_counter_hypotheses_fails(self):
        d = good()
        one(d)["counter_hypotheses"] = []
        self.assertTrue(any("empty" in e for e in v.validate_investigation(d)))

    def test_every_class_must_be_covered(self):
        d = good()
        one(d)["counter_hypotheses"] = [hyp("named", "supported", size="9.93 points")]
        errors = v.validate_investigation(d)
        for cls in ("mix", "common-cause", "measurement"):
            self.assertTrue(any(f"class {cls!r}" in e for e in errors), errors)

    def test_only_mix_may_be_not_applicable_and_only_for_a_non_rate(self):
        d = good()
        one(d)["counter_hypotheses"][2] = hyp("measurement", "not_applicable", needs="no booking change indicated")
        errors = v.validate_investigation(d)
        self.assertTrue(any("never not_applicable" in e for e in errors), errors)
        d = good()
        one(d)["counter_hypotheses"][0] = hyp("mix", "not_applicable", needs="the finding is a rate-card step")
        errors = v.validate_investigation(d)
        self.assertTrue(any("has a decomposition" in e for e in errors), errors)
        one(d)["decompositions"] = "n/a - the finding is a rate-card step, not a rate over a denominator"
        one(d)["claim"] = "The January rate-card steps account for the rise; Supplier B's rate reached 59.0%."
        one(d)["mechanism"] = "Each January the base rate steps up and the invoice follows."
        self.assertEqual(v.validate_investigation(d), [])

    def test_killed_if_needs_a_number(self):
        d = good()
        one(d)["counter_hypotheses"][0]["killed_if"] = "if the mix did not change much"
        self.assertTrue(any("killed_if has no figure" in e for e in v.validate_investigation(d)))

    def test_preregistration_path_required(self):
        d = good()
        one(d)["preregistered_in"] = ""
        self.assertTrue(any("preregistered_in" in e for e in v.validate_investigation(d)))

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
        one(d)["decompositions"][0]["terms"][0]["points"] = 1.0  # Supplier A quietly shrunk
        errors = v.validate_investigation(d)
        self.assertTrue(any("not the whole denominator" in e for e in errors), errors)

    def test_decomposition_needs_mix_interaction_and_two_rate_terms(self):
        d = good()
        one(d)["decompositions"][0]["terms"] = [{"component": "Supplier B", "kind": "rate", "points": 14.75}]
        one(d)["decompositions"][0]["sum_of_terms"] = 14.75
        errors = v.validate_investigation(d)
        self.assertTrue(any("at least two" in e for e in errors), errors)
        self.assertTrue(any("no mix term" in e for e in errors), errors)
        self.assertTrue(any("no interaction term" in e for e in errors), errors)

    def test_every_field_a_candidate_names_gets_a_table(self):
        # The story is about suppliers; an alternative lives on category. The
        # supplier table alone does not test it.
        d = good()
        one(d)["counter_hypotheses"][1]["field"] = "category"
        errors = v.validate_investigation(d)
        self.assertTrue(any("no decomposition by it" in e and "'category'" in e for e in errors), errors)
        one(d)["decompositions"].append(decomposition(components_by="category", metric="apparel return rate by category"))
        self.assertEqual(v.validate_investigation(d), [])

    def test_mix_candidate_must_name_its_field(self):
        d = good()
        del one(d)["counter_hypotheses"][0]["field"]
        self.assertTrue(any("must name the field" in e for e in v.validate_investigation(d)))

    def test_decompositions_may_be_na_with_a_reason(self):
        d = good()
        one(d)["counter_hypotheses"][0] = hyp("mix", "not_applicable", needs="not a rate")
        one(d)["decompositions"] = "n/a - the finding is a rate-card step, not a rate over a denominator"
        one(d)["claim"] = "The January rate-card steps account for the rise."
        one(d)["mechanism"] = "Each January the base rate steps up and the invoice follows."
        self.assertEqual(v.validate_investigation(d), [])
        one(d)["decompositions"] = "skipped"
        self.assertTrue(any("decompositions must be" in e for e in v.validate_investigation(d)))

    def test_allocation_dependence_must_be_stated_and_consistent(self):
        d = good()
        one(d)["allocation_dependence"] = "none"
        self.assertTrue(any("no evidence" in e for e in v.validate_investigation(d)))
        d = good()
        one(d)["allocation_dependence"] = ""
        self.assertTrue(any("allocation_dependence must be" in e for e in v.validate_investigation(d)))
        d = good()
        one(d)["allocation_dependence"] = "see allocation_pairs"
        self.assertTrue(any("which is empty" in e for e in v.validate_investigation(d)))
        one(d)["allocation_pairs"] = [pair()]
        self.assertEqual(v.validate_investigation(d), [])
        one(d)["allocation_dependence"] = "none - all costs at line level"
        self.assertTrue(any("not empty" in e for e in v.validate_investigation(d)))

    def test_allocation_pair_halves_are_full_figures_with_a_rule(self):
        d = good()
        one(d)["allocation_dependence"] = "see allocation_pairs"
        one(d)["allocation_pairs"] = [pair()]
        one(d)["allocation_pairs"][0]["allocated"]["rule"] = ""
        self.assertTrue(any("no rule" in e for e in v.validate_investigation(d)))
        one(d)["allocation_pairs"][0]["allocated"]["rule"] = "by order share"
        del one(d)["allocation_pairs"][0]["allocation_free"]["query_text"]
        self.assertTrue(any("allocation_free" in e and "query_text" in e for e in v.validate_investigation(d)))

    def test_allocation_that_changes_the_conclusion_blocks_established(self):
        d = good()
        one(d)["allocation_dependence"] = "see allocation_pairs"
        one(d)["allocation_pairs"] = [pair(conclusion_changes=True)]
        self.assertTrue(any("allocation pair changes the conclusion" in e for e in v.validate_investigation(d)))

    def test_unreproduced_figure_fails(self):
        d = good()
        one(d)["reverified"][0]["match"] = False
        self.assertTrue(any("did not reproduce" in e for e in v.validate_investigation(d)))

    def test_blocked_entry_still_needs_its_rerun_query_and_a_mismatch(self):
        d = good()
        one(d)["status"] = "blocked"
        one(d)["counter_hypotheses"] = []
        errors = v.validate_investigation(d)
        self.assertTrue(any("blocked on what" in e for e in errors), errors)
        one(d)["reverified"][0]["match"] = False
        self.assertEqual(v.validate_investigation(d), [])
        one(d)["reverified"][0]["query_text"] = ""
        self.assertTrue(any("empty query_text" in e for e in v.validate_investigation(d)))

    def test_recoverable_at_most_is_a_figure_or_a_reasoned_not_derivable(self):
        d = good()
        one(d)["recoverable_at_most"] = "roughly 4 points"
        self.assertTrue(any("recoverable_at_most must be" in e for e in v.validate_investigation(d)))
        one(d)["recoverable_at_most"] = "not derivable"
        self.assertTrue(any("no reason" in e for e in v.validate_investigation(d)))
        one(d)["recoverable_at_most"] = "not derivable - returns by value are not in the P&L; would need a refunds export"
        self.assertEqual(v.validate_investigation(d), [])
        one(d)["recoverable_at_most"] = {"value": 4.1, "unit": "pts"}  # no query behind it
        self.assertTrue(any("recoverable_at_most: missing keys" in e for e in v.validate_investigation(d)))

    def test_numbers_in_the_claim_must_exist_in_the_record(self):
        d = good()
        one(d)["claim"] = "Supplier B accounts for 9.93 of the 14.75 points and the fix is worth 6.2 pts of margin."
        errors = v.validate_investigation(d)
        self.assertTrue(any("'6.2'" in e and "number from nowhere" in e for e in errors), errors)
        # Years and quarter labels are not figures.
        one(d)["claim"] = "Between Q3 FY24 and 2026, Supplier B accounts for 9.93 of the 14.75 points."
        self.assertEqual(v.validate_investigation(d), [])

    def test_numbers_in_the_mechanism_must_exist_in_the_record(self):
        d = good()
        one(d)["mechanism"] = "Returns cost 438.59 rupees each, from the ops interview."
        errors = v.validate_investigation(d)
        self.assertTrue(any("mechanism contains '438.59'" in e for e in errors), errors)

    def test_cli_detects_the_record_kind(self):
        self.assertIn("investigations", v.main.__code__.co_consts)


if __name__ == "__main__":
    unittest.main()
