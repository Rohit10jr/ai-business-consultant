# Unattended Run — Phase 6

> Operative runbook. Phases 0-5 are on `main` and the pipeline has run on Acme. Phase 6 is
> two corrections the first engagement exposed. Phase 7 — the cold end-to-end run — gets its
> own file and its own session.

Read [`TASK.md`](TASK.md), [`CLAUDE.md`](CLAUDE.md) and [`BUILD_PLAN.md`](BUILD_PLAN.md)
first. This file assumes all three, and `TASK.md` carries the per-phase briefs.

## Scope

**One branch, two fixes.** Both are corrections to commands already on `main`.

| Phase | Branch | Cut from | Progress file |
|---|---|---|---|
| 6 | `phase-6-fixes` | `main` | `PROGRESS_PHASE_6.md` |

`TASK.md` carries both briefs in full. In short: the ceiling is measured against a frozen
denominator and overstates by roughly a third; and the calibration rule is blunt because the
gate that tested it demanded a swing.

## HARD STOP

**After both fixes are gated, STOP.** Do not run the pipeline end to end. That is phase 7,
and it must be a session that did not make these fixes — the same reasoning that has graded
every gate in this repo with a fresh subagent. A run by the author of the fix demonstrates
the author, not the harness.

**Also stop immediately, at any point, if:**

- a real client corpus would be needed to continue — use the synthetic one, or stop
- the design appears to need a database, a server, or a web UI
- `engagements/` would need to be un-gitignored for any reason
- a command would need to execute SQL against a live database (`BUILD_PLAN.md` §8 settles
  this: exports only)

## Order and pacing

**Fix 1 before fix 2** — they are independent, but fix 1 touches the artifacts phase 7 will
regenerate, and it is the one with a number already waiting to be matched.

**Inside fix 2, the gate before the rule, and in separate commits.** The rule is blunt
because the gate demanded a swing; rewrite the gate first and the honest formula follows.
Change the formula first and you will fit the gate to whatever you built. The commit order is
part of the gate.

### Do not idle

If a phase is blocked, do not wait. Move to the next thing that is not blocked and record
the block. If everything is blocked, that is a fail-stop — write the report and stop rather
than burning the run.

### This is smaller than phases 3-5

Two command edits, a checker rule, a formula, and their tests. The expensive part is
re-running `/investigate` and `/synthesize` on Acme to regenerate the artifacts, and `TASK.md`
gives you an explicit cheaper alternative if the budget will not carry it. Spend the budget
on getting fix 1's number right, not on polish.

## Before you begin

1. **Sync before you read anything.** `git fetch origin`, then check
   `git log --oneline -1 origin/main` and confirm your branch is cut from that commit.
   The brief you work from - `TASK.md`, this file, `fixtures/` - lives on `main`, so a
   checkout made before the last merge means reading a stale brief and reporting files as
   missing when they are only unfetched. Then confirm `git status` is clean.
2. Read `docs/REFERENCE_PATTERN.md` if you have not this session. Ten minutes, and it
   prevents re-deriving decisions already made.
3. Confirm `codex` is on PATH: `codex --version`. If not, you are on tier 3 for the whole
   run — say so in the progress file.
4. Check the corpus is intact: `python -m unittest discover -s tests -t .` rebuilds
   `fixtures/acme-d2c/` and compares byte for byte. If that fails, stop and fix it first —
   every gate is measured against it.
5. Check the engagement state. `engagements/acme/` should hold `scope.md`, `corpus/` and a
   ranked `findings.json`. Run `python tools/validate_findings.py engagements/acme/findings.json`.
   If it reports the vetoed finding lacks `rank_veto_reason`, the file predates that rule —
   `/rank acme --all` regenerates it, and that is the first thing to do.

## The loop

Per phase:

1. Read the phase's section in `TASK.md` and the phase row in `BUILD_PLAN.md` §7. Together
   they are the contract.
2. Write the smallest thing that could satisfy it.
3. Commit. One commit per meaningful change — **not one per phase**.
4. Repeat until the gate below passes.
5. Write `PROGRESS_PHASE_<N>.md`.
6. Next phase.

**Commit from a file, never inline.** Write `.git/COMMIT_MSG`, then
`git commit -F .git/COMMIT_MSG`. A long inline command stalls an unattended run.

**No `Co-Authored-By: Claude`. No mention of Claude in commit messages.** `CLAUDE.md` rule
2. Easy to reintroduce by habit; check before every commit.

## The gate

All four, in order, plus the phase's own. A phase is not done until all of them pass.

### 1. Tests pass

```
python -m unittest discover -s tests -t . -v
```

Zero failures. A skipped test is acceptable only with a comment saying why.

### 2. The client-data guard holds

```
python tools/check_no_client_data.py
```

**Verify it actually fails** — stage a fixture under `engagements/`, confirm non-zero exit,
unstage. A guard nobody tested is not a guard. It now also scans every path ever added to
history, so it needs full history; a shallow clone makes it refuse to run rather than pass
vacuously.

### 3. Independent review — three tiers

Per `CLAUDE.md`. Tier 1 Codex, tier 2 Codex on PS 5.1, tier 3 fresh Claude subagent. Say
which tier ran.

Point the reviewer at `AGENTS.md` and the files changed. For prompt files, ask explicitly:

> *"Does this command file force the behaviour, or merely request it? Show me a reading
> where a hurried model skips the rule and the prose still permits it."*

That question has found more real defects in this repo than any other. In phase 2 it caught
a rule that let a user choose between two disagreeing derivations, and a `stated` escape
hatch that bypassed the query requirement. Both were in prose the author had read twice.

Report findings, including where you disagree. **Do not auto-apply them.**

### 4. Commit

Clean tree, all work committed, branch pushed.

### 5. The phase's own gate

Full reasoning in `TASK.md`. In short:

**Fix 1 — the ceiling denominator**

| # | Must |
|---|---|
| 1 | `recoverable_at_most` carries a currency unit only; baseline points come only from `baseline_movement_at_most` |
| 2 | The movement query's output shows numerator **and** denominator moving |
| 3 | `check_recommendation.py` rejects baseline-unit ceilings not sourced from a movement figure, and rejects an option whose movement is the sum of its causes' |
| 4 | Re-running `/investigate` on Acme's Supplier B cause reproduces **≈+5.02 pts** — the figure `/review` found independently |
| 5 | Tests cover the single-cause and the combined-option cases |

**Fix 2 — the calibration gate, then the rule**

| # | Must |
|---|---|
| 1 | The gate is rewritten in `TASK.md` and `RUNBOOK.md` **before** the formula changes, and the commit order shows it |
| 2 | `frameworks.md` carries the formula, its reasoning, and the adjustment at n = 1, 2, 5 |
| 3 | A single rejection's effect is a stated number, and whether it can cross a verdict band is answered explicitly either way |
| 4 | `/setup` still reads the rule from the file; `/outcome` still writes only `tracker.csv` |
| 5 | Nothing client-identifying crosses into tracked `frameworks.md` — the phase 5 rule holds |

**Grade every one of these in a session that has not read the answer key.** `TASK.md`
§"Grading without cheating" has the procedure. If you cannot arrange it, mark the gate
**unverified** rather than grading your own run.

## Fail-stop

Stop the run, write the report, do not continue, if:

- the same test fails three times with three different fixes
- a gate check cannot be made to pass and you have exhausted the obvious
- the design requires something `BUILD_PLAN.md` §5 forbids
- you would need to edit the reference repo
- client data has entered git — **stop immediately and report; do not attempt to clean
  history unattended**

A stopped run that reports honestly is a success. A run that pushes past a fail-stop is not,
however much code it produced.

## PROGRESS_PHASE_&lt;N&gt;.md

One per phase, this format:

```markdown
# Phase <N> — <PASS | FAILED | STOPPED>   [branch: <name>]

## What shipped
- <file>: <what it does, in one line>

## Gate
| Check | Result |
|---|---|
| Tests | <n> passing, <n> skipped, 0 failing |
| Client-data guard | verified failing on staged fixture |
| Review | tier <n> — <reviewer> |
| Phase gate | <n>/<n>, graded on a fresh-context run |
| Commits | <n> |

## Findings from review
- <finding> — <applied / disagreed, with reasoning>

## Decisions made
- <decision> — <why>

## Blocked or deferred
- <what> — <why, and what would unblock it>

## For the next phase
- <anything the next agent needs to know>
```

## Judgment calls

**When the reference repo and this plan disagree**, this plan wins — it was written knowing
that repo's defects (`docs/REFERENCE_PATTERN.md` §9). But say so in the progress file; a
disagreement usually means one of the two is wrong.

**When something looks impossible**, it usually means a constraint is being read too
strictly. Write down which constraint and why, then either find the reading that makes it
possible or fail-stop. Do not quietly relax a rule from `BUILD_PLAN.md` §5.

**When one observation contradicts a later one**, reconcile them before reporting, and
report only the conclusion. A file that looks missing and then turns out to be present
almost always means the first look predated a fetch - not that the repo is inconsistent.
Reporting both and leaving the reader to work out which is true wastes the human turn the
report exists to save.

**When two runs of the same command disagree**, that is a finding about the command, not
noise to average away. It has already happened once: two `/discover` runs put the same
segment at 2.3 points and 14 points, differing only in how shared spend was allocated.
Record the disagreement and what caused it.

## Two standing obligations

1. **The guard before the data.** The guard exists and is verified. Re-prove it every phase,
   and if anything about corpus handling ever conflicts with it, the guard wins.
2. **Prompt files get the same scrutiny as code.** They are the product. A vague rule in a
   `.md` file is a bug, and it is the kind this project will fail on if it fails.

## Final report

At the end of the run, `RUN_REPORT.md` gets two things appended:

1. **The run**: what shipped, what each gate showed, what is blocked, what the next runbook
   should cover, and anything you would tell the next agent.
2. **The engagement** — the actual deliverable. `TASK.md` §"The final deliverable" defines
   it: the question, the baseline, the top findings sized in the baseline's unit, the
   recommendation with its options, what `/review` attacked and whether it survived, and
   what a founder would be asked to decide.

Be honest about what did not work. That is the point of the report, and it is why phase 1's
unverified gate got caught and closed instead of quietly becoming load-bearing.
