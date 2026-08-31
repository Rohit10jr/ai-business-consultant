# Unattended Run — Phase 7, the cold run

> Operative runbook. Phases 0-6 are on `main`. Nothing here builds; this phase **runs** the
> harness and reports what it does. The list of what to run is `PROGRESS_PHASE_6.md`
> §"Runtime gates", U1 to U8.

Read [`TASK.md`](TASK.md), [`CLAUDE.md`](CLAUDE.md) and [`BUILD_PLAN.md`](BUILD_PLAN.md)
first. This file assumes all three, and `TASK.md` carries the per-phase briefs.

## Scope

**One branch, one job: run it.**

| Phase | Branch | Cut from | Progress file |
|---|---|---|---|
| 7 | `phase-7-cold-run` | `main` | `PROGRESS_PHASE_7.md` |

The eight runtime items phase 6 left `unverified` are the assignment, and they are already
written with their pass conditions in `PROGRESS_PHASE_6.md`. `TASK.md` carries the framing
and the one rule that matters: **if it breaks, let it break.**

## HARD STOP

**Do not fix the harness.** Not a prompt file, not a validator, not a threshold — however
obvious the fix, however small. Record the failure and move to the next item. A repaired run
is exactly the artefact this phase exists to replace: the repo already has seven of those and
no cold one.

**After U7 and U8, STOP.** Do not start on fixes; that is phase 8, and it should be briefed
from what you find, not decided mid-run.

**Also stop immediately, at any point, if:**

- a real client corpus would be needed to continue — use the synthetic one, or stop
- the design appears to need a database, a server, or a web UI
- `engagements/` would need to be un-gitignored for any reason
- a command would need to execute SQL against a live database (`BUILD_PLAN.md` §8 settles
  this: exports only)

## Order and pacing

**The parts before the whole.** U1-U6 and U8 exercise one command each; U7 is the entire
pipeline in one sitting. Run the parts first — they are cheaper, and finding that
`/investigate` is broken on U1 costs you twenty minutes instead of four hours.

**Then reset the engagement and run U7 properly.** Leave `engagements/acme/corpus/` and
`scope.md`; clear what the parts wrote — `investigation.json`, `recommendation.md`,
`findings.json` — so U7 starts where a real engagement starts and not on the shakedown's
leftovers. Say in the progress file exactly what you cleared.

U7 is one continuous run, `/scope` through `/outcome`, with nothing changed in between.

### Do not idle

If a phase is blocked, do not wait. Move to the next thing that is not blocked and record
the block. If everything is blocked, that is a fail-stop — write the report and stop rather
than burning the run.

### This is the expensive one — budget for it

Phases 3-5 cost roughly 1.5M subagent tokens and 3-4 hours for one engagement, and five runs
died on session limits. Expect the same. `/investigate` and `/review` are 20-30 minutes each
on their own.

If the session ends mid-run, **say where it stopped and what had been written**. A partial
run reported precisely is a usable result; a partial run described vaguely is not, because
nobody can tell afterwards which output came from where.

Every subagent goes out with `model: "opus"` — `CLAUDE.md` §"Which model a subagent runs on".
A dispatch without it is a finding.

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

**Phase 7 — the run itself**

The gate is not "the code passes". It is "the run happened and is honestly written down".

| # | Must |
|---|---|
| 1 | Every one of U1-U8 is recorded as **passed, failed, or not reached** — no item silently absent |
| 2 | A failed item carries **the output that failed**, verbatim, not a description of it |
| 3 | U7 ran as one continuous sitting, from a reset engagement, with nothing changed in between |
| 4 | Nothing was fixed mid-run; anything repaired is named, with why it stopped the run being *possible* rather than merely wrong |
| 5 | `RUN_REPORT.md`'s engagement section is replaced by this run's output, under the corrected ceiling rule |
| 6 | The progress file opens with one paragraph answering: **did the pipeline run end to end, or not?** |

**Item 4 is the one to hold yourself to.** The temptation to fix a one-line prompt bug and
carry on is exactly what produced seven repaired runs and no cold one.

**You are the fresh context this time.** You did not write phase 6's fixes, which is what
makes this run evidence. Do not open `fixtures/*/EXPECTED.md` before or during a run; compare
against it afterwards, once the output is on disk and cannot be influenced by knowing the
answer.

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
