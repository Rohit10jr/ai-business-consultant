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

    def test_corpus_file_at_fixtures_root_is_rejected(self):
        # Only the named synthetic corpora are exempt, not the directory name.
        self.assertEqual(len(guard.find_violations(["fixtures/client_export.csv"])), 1)
        self.assertEqual(len(guard.find_violations(["fixtures/other-client/pnl.xlsx"])), 1)

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

    def test_history_remedy_says_rewrite_not_unstage(self):
        # The staged advice is actively wrong for a path already in history:
        # unstaging fixes nothing, and "just delete it" leaves the blob reachable.
        (message,) = guard.find_violations(["engagements/acme/pnl.csv"], guard.HISTORY_REMEDY)
        self.assertIn("history", message.lower())
        self.assertIn("filter-repo", message)
        self.assertNotIn("restore --staged", message)


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

    def test_weakened_gitignore_in_index_fails_even_if_working_tree_is_clean(self):
        path = self.root / ".gitignore"
        good = path.read_text(encoding="utf-8")
        path.write_text(good.replace("engagements/\n", "", 1), encoding="utf-8")
        self.git("add", ".gitignore")
        path.write_text(good, encoding="utf-8")  # working tree looks fine again
        result = self.run_guard()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("'engagements/'", result.stdout)

    def test_file_committed_then_deleted_is_still_caught_in_history(self):
        # The scenario the history scan exists for: a client file committed in a
        # hurry and removed an hour later. `git rm` clears the tree, never the
        # history, so checks 1-3 see a clean repo and only check 4 can catch it.
        target = self.root / "engagements" / "acme" / "pnl.csv"
        target.parent.mkdir(parents=True)
        target.write_text("month,revenue,ebitda\n2026-04,41200000,-3100000\n", encoding="utf-8")
        self.git("add", "-f", "engagements/acme/pnl.csv")
        self.git("commit", "-q", "-m", "wip")
        self.git("rm", "-q", "engagements/acme/pnl.csv")
        self.git("commit", "-q", "-m", "remove client data")

        # Staged and tracked are both clean now - proving the scan is what fires.
        self.assertEqual(guard.find_violations(guard.git_paths_to_check(self.root)), [])

        result = self.run_guard()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("engagements/acme/pnl.csv", result.stdout)
        self.assertIn("in git history", result.stdout)

    def test_shallow_clone_fails_rather_than_passing_vacuously(self):
        # `actions/checkout` clones with fetch-depth: 1 by default. A history scan
        # there sees one commit and finds nothing, so it must refuse to run. This
        # test is what stops someone dropping `fetch-depth: 0` from CI and leaving
        # a guard that reports OK while checking nothing.
        with tempfile.TemporaryDirectory() as tmp:
            clone = Path(tmp) / "shallow"
            subprocess.run(
                ["git", "clone", "-q", "--depth", "1", self.root.as_uri(), str(clone)],
                check=True, capture_output=True,
            )
            result = subprocess.run(
                [sys.executable, str(GUARD), str(clone)], capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("shallow", result.stdout)
        self.assertIn("fetch-depth: 0", result.stdout)

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
