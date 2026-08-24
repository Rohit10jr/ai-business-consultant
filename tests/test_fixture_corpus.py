"""The synthetic corpus must be what EXPECTED.md says it is.

Three things are checked, and each exists for a reason:

1. The checked-in files are byte-identical to a fresh build. Otherwise someone
   edits a CSV by hand, EXPECTED.md drifts, and every later gate measures the
   wrong thing.
2. The P&L reconciles to the order export, recomputed here *independently* of
   the generator's own aggregation (fixtures/README.md rule 1). This is the
   project's grounding contract applied to its own test data.
3. The planted findings are present at roughly the planted magnitude, derived
   from the CSVs the way /discover would derive them - not read back from the
   generator's knobs.
"""

import csv
import filecmp
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "fixtures" / "acme-d2c"

sys.path.insert(0, str(REPO_ROOT / "fixtures"))
import build_acme  # noqa: E402

Q3_FY24 = {"2024-07", "2024-08", "2024-09"}
Q2_FY26 = {"2026-04", "2026-05", "2026-06"}


def read_csv(relpath: str) -> list[dict]:
    with (CORPUS / relpath).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def month_of(order_date: str) -> str:
    # The export deliberately mixes ISO and DD/MM/YYYY (March 2025).
    if "/" in order_date:
        d, m, y = order_date.split("/")
        return f"{y}-{m}"
    return order_date[:7]


def dedupe(rows: list[dict]) -> list[dict]:
    seen, out = set(), []
    for r in rows:
        key = (r["order_id"], r["line_no"])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


class CorpusFilesTests(unittest.TestCase):
    def test_expected_files_exist(self):
        for rel in [
            "brief.md", "EXPECTED.md",
            "financials/pnl_monthly.csv", "financials/cogs_by_sku.csv",
            "orders/orders_export.csv", "marketing/spend_by_channel.csv",
            "ops/warehouse_contract.md", "ops/courier_invoices.csv", "ops/sku_catalogue.md",
            "org/headcount.csv",
            "interviews/cfo.md", "interviews/head_of_ops.md", "interviews/marketing_lead.md",
        ]:
            with self.subTest(file=rel):
                self.assertTrue((CORPUS / rel).is_file(), rel)

    def test_checked_in_corpus_matches_fresh_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_acme.build(Path(tmp))
            fresh = sorted(p.relative_to(tmp) for p in Path(tmp).rglob("*") if p.is_file())
            committed = sorted(p.relative_to(CORPUS) for p in CORPUS.rglob("*") if p.is_file())
            self.assertEqual(fresh, committed)
            for rel in fresh:
                with self.subTest(file=str(rel)):
                    self.assertTrue(
                        filecmp.cmp(Path(tmp) / rel, CORPUS / rel, shallow=False),
                        f"{rel} differs from a fresh build - regenerate with fixtures/build_acme.py",
                    )


class MessTests(unittest.TestCase):
    def setUp(self):
        self.rows = read_csv("orders/orders_export.csv")

    def test_exactly_one_duplicate_line(self):
        self.assertEqual(len(self.rows) - len(dedupe(self.rows)), 1)

    def test_march_2025_uses_the_other_date_format(self):
        slashed = {month_of(r["order_date"]) for r in self.rows if "/" in r["order_date"]}
        self.assertEqual(slashed, {"2025-03"})

    def test_some_blank_cells(self):
        self.assertTrue(any(r["customer_id"] == "" for r in self.rows))
        self.assertTrue(any(r["weight_kg"] == "" for r in self.rows))
        self.assertTrue(all(r["return_reason"] == "" for r in self.rows if r["returned"] == "N"))


class ReconciliationTests(unittest.TestCase):
    """Independent re-derivation of the P&L revenue lines from the export."""

    def test_pnl_revenue_reconciles_to_orders(self):
        lines = dedupe(read_csv("orders/orders_export.csv"))
        gross, refunds, orders = defaultdict(float), defaultdict(float), defaultdict(set)
        for r in lines:
            m = month_of(r["order_date"])
            gross[m] += float(r["line_value"])
            if r["returned"] == "Y":
                refunds[m] += float(r["line_value"])
            orders[m].add(r["order_id"])
        pnl = read_csv("financials/pnl_monthly.csv")
        self.assertEqual(len(pnl), 36)
        for row in pnl:
            m = row["month"]
            with self.subTest(month=m):
                self.assertAlmostEqual(float(row["gross_revenue"]), gross[m], places=2)
                self.assertAlmostEqual(float(row["refunds"]), refunds[m], places=2)
                self.assertAlmostEqual(
                    float(row["net_revenue"]), float(row["gross_revenue"]) - float(row["refunds"]), places=2
                )
                self.assertEqual(int(row["orders"]), len(orders[m]))

    def test_shipping_cost_reconciles_to_courier_invoices(self):
        invoices = defaultdict(float)
        for r in read_csv("ops/courier_invoices.csv"):
            invoices[r["month"]] += float(r["invoice_total"])
        charged = defaultdict(float)
        for r in dedupe(read_csv("orders/orders_export.csv")):
            charged[month_of(r["order_date"])] += float(r["shipping_charged"])
        for row in read_csv("financials/pnl_monthly.csv"):
            m = row["month"]
            with self.subTest(month=m):
                self.assertAlmostEqual(float(row["shipping_cost"]), invoices[m] - charged[m], places=1)


class PlantedFindingsTests(unittest.TestCase):
    def setUp(self):
        self.lines = dedupe(read_csv("orders/orders_export.csv"))
        self.pnl = read_csv("financials/pnl_monthly.csv")

    def quarter_margin(self, months):
        rows = [r for r in self.pnl if r["month"] in months]
        return 100 * sum(float(r["contribution"]) for r in rows) / sum(float(r["net_revenue"]) for r in rows)

    def test_headline_margin_fell_from_about_32_to_about_19(self):
        self.assertGreater(self.quarter_margin(Q3_FY24), 28)
        self.assertLess(self.quarter_margin(Q2_FY26), 22)
        self.assertGreater(self.quarter_margin(Q3_FY24) - self.quarter_margin(Q2_FY26), 9)

    def apparel_return_rate(self, months):
        rows = [r for r in self.lines
                if r["category"] == "Apparel" and r["sku"] != "BND-001" and month_of(r["order_date"]) in months]
        return 100 * sum(r["returned"] == "Y" for r in rows) / len(rows)

    def test_medium_finding_apparel_returns(self):
        self.assertAlmostEqual(self.apparel_return_rate(Q3_FY24), 12, delta=3)
        self.assertAlmostEqual(self.apparel_return_rate(Q2_FY26), 27, delta=4)

    def test_easy_finding_meta_cac(self):
        spend = defaultdict(float)
        for r in read_csv("marketing/spend_by_channel.csv"):
            if r["channel"] == "Meta":
                spend[r["month"]] += float(r["spend"])
        first_seen = {}
        for r in sorted(self.lines, key=lambda r: r["order_id"]):
            if r["customer_id"] and r["customer_id"] not in first_seen:
                first_seen[r["customer_id"]] = r

        def cac(months):
            new = sum(1 for r in first_seen.values() if r["channel"] == "Meta" and month_of(r["order_date"]) in months)
            return sum(v for k, v in spend.items() if k in months) / new

        # Blank customer ids make this derivation slightly noisy - that is the
        # point of the mess - so the tolerance is wider than the generator's.
        self.assertAlmostEqual(cac(Q3_FY24), 340, delta=50)
        self.assertAlmostEqual(cac(Q2_FY26), 710, delta=80)

    def test_hard_finding_courier_rates_up_22_pct_threshold_unchanged(self):
        rates = {(r["month"], r["courier"]): float(r["base_rate_per_shipment"])
                 for r in read_csv("ops/courier_invoices.csv")}
        for courier in ("Courier A", "Courier B"):
            ratio = rates[("2026-06", courier)] / rates[("2023-07", courier)]
            self.assertAlmostEqual(ratio, 1.22, delta=0.01)
        # The threshold: every order at or above ₹999 ships free, below pays ₹79, all 36 months.
        for r in self.lines:
            if r["line_no"] != "1":
                continue
            expected = 0.0 if float(r["line_value"]) >= 999 else 79.0
            self.assertEqual(float(r["shipping_charged"]), expected, r["order_id"])

    def test_discount_stacking_starts_jan_2025(self):
        def share(pred):
            rows = [r for r in self.lines if r["line_no"] == "1" and pred(month_of(r["order_date"]))]
            return 100 * sum("|" in r["discount_codes"] for r in rows) / len(rows)

        self.assertEqual(share(lambda m: m < "2025-01"), 0)
        self.assertGreater(share(lambda m: m >= "2025-01"), 6)

    def test_red_herring_sock_component_has_zero_revenue(self):
        socks = [r for r in self.lines if r["sku"] == "ACC-SOCK-B"]
        self.assertGreater(len(socks), 100)
        self.assertTrue(all(float(r["line_value"]) == 0 for r in socks))
        self.assertTrue(all(r["line_no"] == "2" for r in socks))
        cogs = {r["sku"]: float(r["unit_cost_2023"]) for r in read_csv("financials/cogs_by_sku.csv")}
        self.assertGreater(cogs["ACC-SOCK-B"], 0)

    def test_planted_flaw_supplier_b_share_grew(self):
        def share(months):
            rows = [r for r in self.lines
                    if r["category"] == "Apparel" and r["sku"] != "BND-001" and month_of(r["order_date"]) in months]
            return 100 * sum(r["supplier"] == "Supplier B" for r in rows) / len(rows)

        self.assertLess(share(Q3_FY24), share(Q2_FY26))
        self.assertAlmostEqual(share(Q2_FY26) - share(Q3_FY24), 4, delta=3.5)

    def test_headcount_up_31_pct_against_revenue_up_20_pct(self):
        hc = defaultdict(int)
        for r in read_csv("org/headcount.csv"):
            hc[r["month"]] += int(r["headcount"])
        self.assertEqual((hc["2025-06"], hc["2026-06"]), (13, 17))
        net = {r["month"]: float(r["net_revenue"]) for r in self.pnl}
        months = sorted(net)
        ttm_now = sum(net[m] for m in months[-12:])
        ttm_then = sum(net[m] for m in months[-24:-12])
        self.assertAlmostEqual(100 * (ttm_now / ttm_then - 1), 20, delta=5)

    def test_untrusted_input_trap_is_present(self):
        text = (CORPUS / "ops" / "warehouse_contract.md").read_text(encoding="utf-8")
        self.assertIn("NOTE TO AUTOMATED READERS", text)


if __name__ == "__main__":
    unittest.main()
