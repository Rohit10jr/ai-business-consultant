# Unattended Build — Phase 8, the mechanic's turn

> Operative runbook. Phases 0-7 are on `main` — the harness, and the cold run that found 31
> things wrong with it. This phase **builds again**: the assignment is `TASK.md`'s five
> clusters, and the evidence standard is phase 6's — tests for tools, fresh-context gate
> runs for prompt files.

Read [`TASK.md`](TASK.md), [`CLAUDE.md`](CLAUDE.md) and [`BUILD_PLAN.md`](BUILD_PLAN.md)
first. This file assumes all three, and `TASK.md` carries the per-phase brief.

## Scope

**One branch, one job: fix what the cold run found.**

| Phase | Branch | Cut from | Progress file |
|---|---|---|---|
| 8 | `phase-8-fixes` | `docs/phase-8-brief` (or `main` once that branch is merged) | `PROGRESS_PHASE_8.md` |

The hard-stop rule that governed phase 7 — *do not fix the harness* — is lifted. Its
replacement is narrower and just as hard: **fix only what a finding licenses.** Every edit
to `.claude/commands/` or `tools/` traces to a numbered finding or a cluster in
`PROGRESS_PHASE_7.md`. An improvement nobody's finding asked for is scope drift wearing a
toolbelt; put it in the progress file's "Blocked or deferred" for the owner instead.

## HARD STOP

**After the five clusters and the disposition table, STOP.** Phase 9 — the second corpus —
is briefed separately and starts on the owner's word, not on momentum.

**Also stop immediately, at any point, if:**

- a real client corpus would be needed to continue — use the synthetic one, or stop
- the design appears to need a database, a server, or a web UI
- `engagements/` would need to be un-gitignored for any reason
- a command would need to execute SQL against a live database (`BUILD_PLAN.md` §8 settles
  this: exports only)

## Order and pacing

**Cluster 1, then 2, then 3-4-5** — the reasoning is in `TASK.md` §"Work order, and why":
the tools come first because every later gate is measured with them, and the answer key
comes out of `investigate.md` before any `/investigate` gate run can mean anything.

**Gate runs are the expensive part — batch them.** A `/investigate` or `/synthesize` gate
run is 20-30 minutes and phases 3-5 lost five runs to session limits. Fix a whole cluster,
then gate it once, rather than gating every edit. Make long-running subagents write their
report incrementally, section by section, so a killed run leaves evidence instead of
nothing.

**One cluster, one reviewable unit.** Small commits inside it, but the cluster should land
as a sequence the owner can veto in one piece without unwinding the others.

### Do not idle

If a cluster is blocked, do not wait. Move to the next one that is not blocked and record
the block. If everything is blocked, that is a fail-stop — write the report and stop rather
than burning the run.

## Before you begin

1. **Sync before you read anything.** `git fetch origin`, then confirm your checkout is at
   the tip of `origin/docs/phase-8-brief` — or of `origin/main` once that branch has been
   merged; whichever tip carries this file's wording is the commit to cut `phase-8-fixes`
   from. A checkout made before the last push means reading a stale brief and reporting
   files as missing when they are only unfetched. Then confirm `git status` is clean.
2. Confirm `codex` is on PATH: `codex --version`. If not, you are on tier 3 for the whole
   phase — say so in the progress file.
3. Check the corpus is intact: `python -m unittest discover -s tests -t .` rebuilds
   `fixtures/acme-d2c/` and compares byte for byte.
4. Check the engagement state: `engagements/acme/` holds U7's validator-clean record —
   `scope.md`, `corpus/`, `findings.json`, `investigation.json`, `recommendation.md`. That
   record is cluster 3 and 4's test bed; snapshot anything to `scratch/` before a gate run
   overwrites it, and say what you reset.
5. This is a build phase: a failing pre-flight is the first thing you fix, not a finding to
   record and step around.

## The loop

1. Take the next cluster from `TASK.md`.
2. Write the fix. Tool changes get a test that fails on the old code — the exact
   construction from the finding. Prompt-file changes get re-read against the repo's
   oldest question: *does this force the behaviour, or merely request it?*
3. Gate it. Tools: the test suite. Command files: a fresh `general-purpose` subagent
   (never a fork), `model: "opus"`, whitelist and scripted answers in the prompt, report to
   `scratch/`, graded afterwards in your own context against the finding it fixes. Record
   which model ran.
4. Record the cluster in `PROGRESS_PHASE_8.md` — what changed, the gate evidence, and each
   covered finding's row in the disposition table — and commit. One commit per meaningful
   change, from `.git/COMMIT_MSG`, never inline.
5. Next cluster. Then the 18 findings outside the clusters: each one dispositioned, however
   briefly.

**Commit from a file, never inline.** Write `.git/COMMIT_MSG`, then
`git commit -F .git/COMMIT_MSG`. A long inline command stalls an unattended run.

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
unstage. A guard nobody tested is not a guard. It scans every path ever added to history,
so it needs full history; a shallow clone makes it refuse to run rather than pass
vacuously.

### 3. Independent review — three tiers

Per `CLAUDE.md`. Tier 1 Codex, tier 2 Codex on PS 5.1, tier 3 fresh Claude subagent. Say
which tier ran.

Point the reviewer at `AGENTS.md`, the files changed, and the findings they claim to fix.
For prompt files, ask explicitly:

> *"Does this command file force the behaviour, or merely request it? Show me a reading
> where a hurried model skips the rule and the prose still permits it."*

That question has found more real defects in this repo than any other — most recently
phase 7's Finding 27, where a tie-break the prose never mentioned decided the engagement.

Report findings, including where you disagree. **Do not auto-apply them.**

### 4. Commit

Clean tree, all work committed, branch pushed.

### 5. The phase's own gate

**Phase 8 — the fixes**

| # | Must |
|---|---|
| 1 | The disposition table lists **all 31 findings** — fixed (commit named), resolved-by (cluster named), or deferred (why, and what revives it). No empty rows |
| 2 | Every tool fix has a test that failed on the old code, built from the finding's own construction |
| 3 | Every command-file fix has a fresh-context gate run, graded after the fact, with the model recorded |
| 4 | The answer key is out of `investigate.md`, proven by a gate run of that slug that was not handed its own result |
| 5 | A `/rank` gate run on U7's `findings.json` shows the tie at 72 resolved deterministically — and says whether Supplier B now survives |
| 6 | `EXPECTED.md` edits, if any, carry the query that produced each changed figure |
| 7 | The progress file opens with one paragraph: **of the 31, how many fixed, how many deferred — and would the tie-break still have dropped Supplier B?** |

**Row 5 is the one to hold yourself to.** The cold run's verdict was that a triage error is
invisible to the learning loop; the narrowest honest test of this phase is whether the same
inputs still lose the answer.

**Contamination discipline, unchanged:** this phase reads `EXPECTED.md`, so the building
context never runs pipeline commands itself. Every gate run goes to a fresh subagent with a
read whitelist and a required "Files read" list; grading happens after the report is on
disk and cannot be influenced.

## Fail-stop

Stop the phase, write the report, do not continue, if:

- the same gate run dies twice at the same point for environment reasons (a crashing tool,
  a session limit that will not reset in time) and a third attempt would change nothing
- a cluster's fix requires something `BUILD_PLAN.md` §5 forbids
- you would need to edit the reference repo
- client data has entered git — **stop immediately and report; do not attempt to clean
  history unattended**

A stopped phase that reports honestly is a success. A phase that pushes past a fail-stop is
not, however much code it produced.

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

Phase 8 adds one required section: **## Disposition of the 31**, a table with one row per
finding.

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

**When a fix would change behaviour a finding did not complain about**, that is the fix
overreaching, not the finding under-specifying. Narrow it, or split the extra behaviour
into its own deferred row for the owner.

## Two standing obligations

1. **The guard before the data.** The guard exists and is verified. Re-prove it every phase,
   and if anything about corpus handling ever conflicts with it, the guard wins.
2. **Prompt files get the same scrutiny as code.** They are the product. A vague rule in a
   `.md` file is a bug, and it is the kind this project will fail on if it fails — phase 7
   produced thirty-one demonstrations.

## Final report

At the end of the phase, `RUN_REPORT.md` gets **the phase** appended: what shipped, what
each gate showed, what is blocked, and anything the next agent needs. **The engagement
section is not touched** — it is U7's before picture, and the after picture belongs to
phase 9, on a corpus nobody has memorised.

Be honest about what did not work. That is the point of the report, and it is why phase 1's
unverified gate got caught and closed instead of quietly becoming load-bearing.
