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

    def test_untrusted_rule_is_carried_into_subagent_prompts(self):
        # Present at the top is not enough; the rule must ride along into any
        # subagent the command spawns (docs/REFERENCE_PATTERN.md §6).
        carry = re.compile(r"Put this sentence in the prompt of any (such )?subagent")
        for path in self.command_files():
            with self.subTest(command=path.name):
                self.assertRegex(path.read_text(encoding="utf-8"), carry)

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
        # A disagreeing second derivation must be terminal, not a user choice,
        # and the output template must have no slot for "disagrees by".
        self.assertRegex(gate, r"\*\*If they disagree, there\s+is no baseline\.\*\*")
        self.assertNotIn("disagrees by", self.text)
        self.assertIn("row count before and after the join", gate)
        self.assertIn("On **edit**", gate)

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


class DiscoverTests(unittest.TestCase):
    def setUp(self):
        self.text = read("discover.md")

    def test_never_reads_the_fixture_answer_key(self):
        # TASK.md: the rule in prose is the protection; this stops it being deleted.
        self.assertIn("EXPECTED.md", self.text)
        self.assertRegex(self.text, r"never `fixtures/\*/EXPECTED\.md`")
        self.assertIn("**Never read `fixtures/`**", self.text)

    def test_row_counts_before_and_after_dedup_and_across_joins(self):
        self.assertIn("rows before and after", self.text)
        self.assertIn("preflight_csv.py", self.text)
        self.assertIn("row count of each input and of the output", self.text)
        self.assertIn("Row counts before and after de-duplication, and in and out of every join", self.text)

    def test_ungrounded_figure_is_removed_not_softened(self):
        self.assertIn("**A finding that fails any check is not softened, it is not recorded.**", self.text)
        self.assertIn('Not "roughly", not\n"approximately"', self.text)

    def test_query_executed_this_turn_and_shown(self):
        self.assertIn("run **in this turn**", self.text)
        self.assertIn("**Every figure has a query, run this turn, shown.**", self.text)

    def test_gates_and_single_writer(self):
        self.assertGreaterEqual(len(STOP_HERE.findall(self.text)), 1)
        self.assertIn("`/discover` is the only writer of this file", self.text)
        self.assertIn("Do not run it. Stop here.", self.text)
        self.assertIn("Run `/scope <client>` first", self.text)

    def test_separates_known_from_new_and_explains_zero_price_lines(self):
        self.assertIn("known_to_client", self.text)
        self.assertIn("zero_price_lines_explained", self.text)
        self.assertIn("mix_at_boundaries", self.text)

    def test_stated_figures_need_a_record_document_and_a_script(self):
        # Review finding: "stated" must not be a bypass of the query rule. A stated
        # figure comes only from a record document, never an interview, and is
        # still produced by a script that prints the line.
        self.assertIn("**only** when the document is a *record*", self.text)
        self.assertIn("An interview, the brief, or a note\nof what someone said is never a record", self.text)
        self.assertIn("A stated figure still gets a script run this turn", self.text)
        self.assertIn('writing "not possible" is a\n   failed check', self.text)
        # "partial" is allowed, but only structured - see validate_findings.py.
        self.assertIn("which part agrees and what the remainder depends on", self.text)
        self.assertIn("separated by a semicolon", self.text)
        self.assertIn("A bare `partial` is a failed check", self.text)

    def test_magnitude_must_be_expressed_in_the_baseline_metric(self):
        self.assertIn("baseline_metric", self.text)
        self.assertIn("**Only when a query can produce it.**", self.text)
        self.assertIn("A fabricated\n   magnitude is worse than an absent one", self.text)
        self.assertNotIn("docs/CONSULTING_METHOD.md", self.text)

    def test_subagent_prompts_carry_the_whitelist(self):
        self.assertIn("do-not-read list from Step 0 verbatim", self.text)
        self.assertIn("**Re-run every returned query yourself before accepting the figure.**", self.text)


class RankTests(unittest.TestCase):
    def setUp(self):
        self.text = read("rank.md")

    def test_weights_come_from_frameworks_and_are_never_invented(self):
        self.assertIn("`practice/frameworks.md`", self.text)
        self.assertIn("**Do not invent weights and do not fall back to defaults in your head**", self.text)
        self.assertNotRegex(self.text, r"\b40%\b.*\b30%\b")  # no weights baked into the prompt

    def test_baseline_restating_findings_are_vetoed_not_merely_scored_low(self):
        # The symptom outranked every lever in the phase 2 run because it carries the
        # whole gap as its impact. A cap cannot fix that - it has to leave the list.
        self.assertIn("restates-the-baseline", self.text)
        self.assertIn("The test is aggregation, not wording", self.text)
        self.assertIn("Do not score it low instead", self.text)

    def test_veto_records_a_slug_and_a_human_reason(self):
        self.assertIn("rank_veto_reason", self.text)
        self.assertIn("is the rule and is not a reason", self.text)
        for slug in ("out-of-scope", "ungrounded", "restates-the-baseline"):
            self.assertIn(slug, self.text)

    def test_impact_is_read_not_reconstructed(self):
        self.assertIn("magnitude.baseline_metric", self.text)
        self.assertIn("do not attempt the conversion yourself", self.text)

    def test_vetoes_precede_scoring_and_are_terminal_for_the_finding(self):
        self.assertIn("## Step 1: Vetoes", self.text)
        self.assertIn("a vetoed finding is **not scored**", self.text)
        self.assertRegex(self.text, r"\*\*Do not score it lower to\s+compensate; do not score it at all\.\*\*")

    def test_impact_is_computed_or_flagged_never_estimated(self):
        self.assertIn("**10, and flag `unquantified`**", self.text)
        self.assertIn("`unquantified` flag cannot exceed **park**", self.text)

    def test_annotation_is_additive_only(self):
        self.assertIn("`rank_*` keys and `status` are the only keys `/rank` writes", self.text)
        self.assertIn("byte-identical", self.text)
        # status is the one shared key; the check must say it is set aside, not ignored.
        self.assertIn("with `status` and the `rank_*` keys set aside", self.text)
        for key in ("rank_score", "rank_verdict", "rank_date", "rank_veto"):
            self.assertIn(key, self.text)

    def test_presents_and_asks_and_does_not_chain(self):
        self.assertIn("Which findings should `/investigate` pursue?", self.text)
        self.assertIn("**If the user gives none, stop here.**", self.text)
        self.assertIn("Do not run it. Stop here.", self.text)

    def test_triage_depth_only(self):
        self.assertIn("No corpus reads, no new queries, no research.", self.text)


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
