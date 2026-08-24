"""The client-data guard must fail loudly, and must be seen to fail.

Two layers: pure unit tests on `find_violations`, and an end-to-end run of the
script against a throwaway git repo with a client file actually staged. The
second layer exists because a guard that is only unit-tested has never been
observed refusing anything.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUARD = REPO_ROOT / "tools" / "check_no_client_data.py"

sys.path.insert(0, str(REPO_ROOT / "tools"))
import check_no_client_data as guard  # noqa: E402


class FindViolationsTests(unittest.TestCase):
    def test_engagements_path_at_any_depth_is_rejected(self):
        for path in [
            "engagements/acme/scope.md",
            "engagements/acme/corpus/financials/pnl.xlsx",
            "some/nested/engagements/x.txt",
            "Engagements/acme/notes.md",
        ]:
            with self.subTest(path=path):
                self.assertEqual(len(guard.find_violations([path])), 1)

    def test_corpus_file_outside_fixtures_is_rejected(self):
        for path in ["export.csv", "data/pnl.xlsx", "practice/tracker.csv", "docs/deck.pptx"]:
            with self.subTest(path=path):
                self.assertEqual(len(guard.find_violations([path])), 1)

    def test_synthetic_fixtures_are_allowed(self):
        paths = [
            "fixtures/acme-d2c/orders/orders_export.csv",
            "fixtures/acme-d2c/financials/pnl_monthly.csv",
            "fixtures/README.md",
        ]
        self.assertEqual(guard.find_violations(paths), [])

    def test_ordinary_repo_files_are_allowed(self):
        paths = ["README.md", "tools/check_no_client_data.py", ".claude/commands/scope.md"]
        self.assertEqual(guard.find_violations(paths), [])

    def test_message_names_the_offending_path(self):
        (message,) = guard.find_violations(["engagements/acme/scope.md"])
        self.assertIn("engagements/acme/scope.md", message)


class GitignoreRulesTests(unittest.TestCase):
    def test_repo_gitignore_passes(self):
        self.assertEqual(guard.check_gitignore(REPO_ROOT), [])

    def test_missing_rule_and_stray_negation_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
            text = text.replace("engagements/\n", "", 1) + "!engagements/acme/\n"
            (root / ".gitignore").write_text(text, encoding="utf-8")
            errors = guard.check_gitignore(root)
        self.assertTrue(any("'engagements/'" in e and "missing" in e for e in errors))
        self.assertTrue(any("!engagements/acme/" in e for e in errors))


@unittest.skipIf(shutil.which("git") is None, "git is required for the end-to-end guard test")
class EndToEndTests(unittest.TestCase):
    """Run the real script against a scratch repo. Nothing touches this repo."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "test")
        shutil.copy(REPO_ROOT / ".gitignore", self.root / ".gitignore")
        (self.root / "README.md").write_text("scratch\n", encoding="utf-8")
        self.git("add", "README.md", ".gitignore")
        self.git("commit", "-q", "-m", "init")

    def tearDown(self):
        self._tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def run_guard(self):
        return subprocess.run(
            [sys.executable, str(GUARD), str(self.root)],
            capture_output=True, text=True,
        )

    def test_clean_repo_passes(self):
        result = self.run_guard()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_staged_engagement_file_fails(self):
        target = self.root / "engagements" / "acme" / "corpus" / "pnl.csv"
        target.parent.mkdir(parents=True)
        target.write_text("month,revenue\n2026-01,1\n", encoding="utf-8")
        # -f because .gitignore would otherwise refuse - the guard is the
        # second line of defence, and it has to hold when the first is bypassed.
        self.git("add", "-f", str(target.relative_to(self.root)))
        result = self.run_guard()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("engagements/acme/corpus/pnl.csv", result.stdout)

    def test_committed_corpus_file_outside_fixtures_fails(self):
        target = self.root / "export.xlsx"
        target.write_bytes(b"not really a workbook")
        self.git("add", "-f", "export.xlsx")
        self.git("commit", "-q", "-m", "oops")
        result = self.run_guard()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("export.xlsx", result.stdout)


if __name__ == "__main__":
    unittest.main()
