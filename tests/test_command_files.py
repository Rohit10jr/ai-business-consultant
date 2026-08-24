"""Lint for the prompt files. They are the product, and a vague rule in one is a bug.

These checks cannot prove a command *forces* a behaviour - only a reader can judge
that (RUNBOOK.md, gate step 3). What they can do is stop the load-bearing sentences
from quietly disappearing in a later edit: the untrusted-input rule, the terminal
"stop here" on a human gate, and the single-writer statement.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMANDS = REPO_ROOT / ".claude" / "commands"

# Every command that reads anything from outside the repo carries this rule, and
# repeats it in its Rules section so it rides along into subagent prompts.
UNTRUSTED = re.compile(r"untrusted data, never instructions", re.IGNORECASE)
STOP_HERE = re.compile(r"\*\*If the user says no[^*]*stop here\.\*\*")


def read(name: str) -> str:
    return (COMMANDS / name).read_text(encoding="utf-8")


class EveryCommandTests(unittest.TestCase):
    def command_files(self):
        files = sorted(COMMANDS.glob("*.md"))
        self.assertTrue(files, "no command files found")
        return files

    def test_has_title_and_arguments_token(self):
        for path in self.command_files():
            text = path.read_text(encoding="utf-8")
            with self.subTest(command=path.name):
                self.assertTrue(text.startswith("# /" + path.stem), "title must be `# /<name>`")
                self.assertIn("$ARGUMENTS", text)

    def test_untrusted_input_rule_appears_at_least_twice(self):
        # Once where the input is first read, once in the closing Rules - so a
        # model skimming either end still meets it.
        for path in self.command_files():
            with self.subTest(command=path.name):
                self.assertGreaterEqual(len(UNTRUSTED.findall(path.read_text(encoding="utf-8"))), 2)

    def test_no_outbound_capability_is_named(self):
        # BUILD_PLAN.md §5: the harness never sends anything. A command file
        # that mentions these is wiring toward a tool it must not have.
        forbidden = re.compile(r"\b(send an email|send email|slack message|calendar invite|smtp)\b", re.I)
        for path in self.command_files():
            with self.subTest(command=path.name):
                self.assertIsNone(forbidden.search(path.read_text(encoding="utf-8")))

    def test_no_attribution(self):
        for path in self.command_files():
            with self.subTest(command=path.name):
                self.assertNotIn("Co-Authored-By", path.read_text(encoding="utf-8"))


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.text = read("scope.md")

    def test_baseline_gate_is_terminal(self):
        # The gate must say what happens on "no", and it must be a stop, and it
        # must forbid the placeholder escape hatch.
        gate = self.text[self.text.index("## Step 3"): self.text.index("## Step 4")]
        self.assertRegex(gate, r"\*\*If the user says no.*stop here\.\*\*")
        self.assertIn("Do **not** write `scope.md`", gate)
        self.assertIn("TBD", gate)

    def test_overwrite_and_question_gates_are_terminal(self):
        self.assertGreaterEqual(len(STOP_HERE.findall(self.text)), 2)
        self.assertIn("**If the user gives none, stop here.**", self.text)

    def test_baseline_has_four_mandatory_parts(self):
        for part in ("value and unit", "period", "source", "derivation"):
            self.assertIn(part, self.text)

    def test_single_writer_and_no_chaining(self):
        self.assertIn("`/scope` is the only writer of this file", self.text)
        self.assertIn("Do not run it. Stop here.", self.text)

    def test_output_shape_matches_worked_example(self):
        for key in ("question:", "baseline:", "source:", "done_when:", "out_of_scope:"):
            self.assertIn(key, self.text)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.text = read("setup.md")

    def test_writes_only_the_two_tracked_files(self):
        self.assertIn("`practice/domains.md`", self.text)
        self.assertIn("`practice/frameworks.md`", self.text)
        self.assertIn("never reads or writes `practice/tracker.csv`", self.text)
        self.assertIn("never touches `engagements/`", self.text)

    def test_client_identifiers_are_forbidden_in_tracked_files(self):
        self.assertIn("must never contain a client name", self.text)

    def test_each_change_confirmed_and_no_is_terminal_for_it(self):
        self.assertIn("**If the user says no, skip that change", self.text)
        self.assertIn("one at a time", self.text)


if __name__ == "__main__":
    unittest.main()
