"""practice/frameworks.md is the authority for the calibration rule, and /setup applies
it from the file. So the file has to agree with itself: every row of its n-table, and
every row of its live Calibration table, must be what its own formula makes them.

The formula is read from the file's code block - not re-typed here - so a change to the
rule that forgets the tables fails, and a change to the tables that forgets the rule
fails too. This is the mechanical half of phase 6's calibration gate (items b and c).
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FRAMEWORKS = REPO_ROOT / "practice" / "frameworks.md"

FORMULA = re.compile(
    r"adjustment = round\(25 × \(accepted − rejected\) / \(rows \+ (?P<k>\d+)\)\), capped at \+(?P<cap>\d+)"
)
N_TABLE_ROW = re.compile(r"^\| (\d+) \| (\d+) \| (\d+) \| [^|]+ \| ([+−-]\d+) \|$", re.M)
LIVE_ROW = re.compile(r"^\| `?([a-z-]+)`? \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| ([+−-]\d+) \|$", re.M)


def read_rule():
    text = FRAMEWORKS.read_text(encoding="utf-8")
    section = text[text.index("## Calibration"): text.index("## Lessons")]
    m = FORMULA.search(section)  # the active rule, in its section - not any line anywhere
    assert m, "the formula line in practice/frameworks.md's Calibration section no longer matches the shape this test reads"
    return text, int(m.group("k")), int(m.group("cap"))


def adjustment(accepted, rejected, rows, k, cap):
    raw = 25 * (accepted - rejected) / (rows + k)
    rounded = int(raw + 0.5) if raw >= 0 else -int(-raw + 0.5)  # half away from zero
    return min(rounded, cap)


def to_int(token):
    return int(token.replace("−", "-"))


class CalibrationRuleTests(unittest.TestCase):
    def test_formula_is_present_with_shrinkage(self):
        _, k, cap = read_rule()
        self.assertGreaterEqual(k, 1, "shrinkage of at least one phantom row")
        self.assertEqual(cap, 10)

    def test_n_table_matches_the_formula(self):
        text, k, cap = read_rule()
        section = text[text.index("## Calibration"): text.index("## Lessons")]
        rows = N_TABLE_ROW.findall(section)
        self.assertGreaterEqual(len(rows), 5, "the n-table must show n = 1, 2, 5 and a mixed case")
        for n, a, r, adj in rows:
            with self.subTest(rows=n, accepted=a, rejected=r):
                self.assertEqual(adjustment(int(a), int(r), int(n), k, cap), to_int(adj))
        ns = {int(n) for n, _, _, _ in rows}
        self.assertTrue({1, 2, 5} <= ns, f"n-table covers {sorted(ns)}, needs 1, 2 and 5")
        self.assertTrue(any(int(a) and int(r) for _, a, r, _ in rows), "no mixed row")

    def test_single_row_effect_is_stated_and_band_crossing_is_answered(self):
        text, k, cap = read_rule()
        one = adjustment(0, 1, 1, k, cap)
        self.assertIn(f"{abs(one)}", text)
        self.assertIn("**Can a single row move a finding across a verdict band?**", text)
        self.assertRegex(text, r"\*\*Can a single row move a finding across a verdict band\?\*\* (Yes|No)")

    def test_live_calibration_table_matches_the_formula(self):
        text, k, cap = read_rule()
        section = text[text.index("## Calibration"): text.index("## Lessons")]
        live = LIVE_ROW.findall(section)
        # Either /setup has written rows, or the placeholder says none - never silence.
        self.assertTrue(live or "_none yet_" in section, "no live rows and no placeholder: the table is gone")
        for ftype, n, a, m, r, adj in live:
            with self.subTest(finding_type=ftype):
                self.assertEqual(int(n), int(a) + int(m) + int(r))
                self.assertEqual(adjustment(int(a), int(r), int(n), k, cap), to_int(adj))

    def test_full_weight_is_a_limit_reached_only_with_evidence(self):
        _, k, cap = read_rule()
        self.assertLess(abs(adjustment(0, 1, 1, k, cap)), 25)
        self.assertLess(abs(adjustment(0, 10, 10, k, cap)), 25)
        self.assertLessEqual(abs(adjustment(0, 100, 100, k, cap)), 25)
        self.assertGreater(abs(adjustment(0, 100, 100, k, cap)), abs(adjustment(0, 5, 5, k, cap)))


if __name__ == "__main__":
    unittest.main()
