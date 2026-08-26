"""The preflight tool is what /discover's row-count rule rests on.

It is checked against the fixture corpus, whose mess is documented in
fixtures/acme-d2c/EXPECTED.md: one exact duplicate row, March 2025 dates in
DD/MM/YYYY, blank customer ids and weights.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ORDERS = REPO_ROOT / "fixtures" / "acme-d2c" / "orders" / "orders_export.csv"
TOOL = REPO_ROOT / "tools" / "preflight_csv.py"

sys.path.insert(0, str(REPO_ROOT / "tools"))
import preflight_csv  # noqa: E402


class OrdersExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = preflight_csv.preflight(ORDERS, key=["order_id", "line_no"])

    def test_counts_before_and_after_deduplication(self):
        self.assertEqual(self.report["rows_raw"], 5476)
        self.assertEqual(self.report["rows_deduplicated"], 5475)
        self.assertEqual(len(self.report["duplicate_rows"]), 1)

    def test_key_repeats_are_gone_once_exact_duplicates_are(self):
        # The only repeated (order_id, line_no) is the exact duplicate; bundle
        # lines share an order_id but have distinct line numbers.
        self.assertEqual(self.report["key_repeats"], [])

    def test_mixed_date_formats_are_reported(self):
        formats = self.report["date_columns"]["order_date"]
        self.assertIn("iso YYYY-MM-DD", formats)
        self.assertIn("day-first DD/MM/YYYY", formats)
        self.assertEqual(sum(formats.values()), 5475)

    def test_blank_cells_are_counted(self):
        blanks = self.report["blank_cells"]
        self.assertGreater(blanks["customer_id"], 0)
        self.assertGreater(blanks["weight_kg"], 0)
        # Not returned -> no reason. Most lines.
        self.assertGreater(blanks["return_reason"], 4000)

    def test_render_names_the_mixed_format(self):
        text = preflight_csv.render(self.report)
        self.assertIn("rows raw: 5476", text)
        self.assertIn("rows after exact-duplicate removal: 5475", text)
        self.assertIn("MIXED FORMATS", text)


class CliTests(unittest.TestCase):
    def test_cli_runs_on_the_fixture(self):
        result = subprocess.run(
            [sys.executable, str(TOOL), "--key", "order_id,line_no", str(ORDERS)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("duplicates: 1", result.stdout)

    def test_key_missing_from_a_file_is_skipped_not_fatal(self):
        pnl = REPO_ROOT / "fixtures" / "acme-d2c" / "financials" / "pnl_monthly.csv"
        result = subprocess.run(
            [sys.executable, str(TOOL), "--key", "order_id,line_no", str(pnl)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("key check skipped", result.stdout)

    def test_unreadable_file_is_a_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(TOOL), str(Path(tmp) / "missing.csv")],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("unreadable", result.stdout)


if __name__ == "__main__":
    unittest.main()
