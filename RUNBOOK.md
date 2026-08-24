# Unattended Run — Phases 0 to 2

> Operative runbook. Phases 3-5 get their own file once phase 2's gate passes.

Read [`CLAUDE.md`](CLAUDE.md) and [`BUILD_PLAN.md`](BUILD_PLAN.md) first. This file assumes
both.

## Scope

**Three phases: 0, 1, 2.** Each on its own branch, each cut from the previous phase's
completed tip, each with its own progress file.

| Phase | Branch | Cut from | Progress file |
|---|---|---|---|
| 0 | `phase-0-skeleton` | `main` | `PROGRESS_PHASE_0.md` |
| 1 | `phase-1-scope` | `phase-0-skeleton` | `PROGRESS_PHASE_1.md` |
| 2 | `phase-2-discover` | `phase-1-scope` | `PROGRESS_PHASE_2.md` |

## HARD STOP

**After phase 2's gate passes, STOP.** Do not start phase 3. The grounding checklist is
the hardest part of this project and needs a human read of phase 2's output before its
design is settled.

**Also stop immediately, at any point, if:**

- a real client corpus would be needed to continue — use the synthetic one, or stop
- the design appears to need a database, a server, or a web UI
- `engagements/` would need to be un-gitignored for any reason

## Order and pacing

**0 → 1 → 2.** Phase 0 first because its CI guard protects everything after it; a client
corpus landing before the guard exists is the one unrecoverable failure in this project.

### Do not idle

If a phase is blocked, do not wait. Move to the next thing that is not blocked, and record
the block in the progress file. If everything is blocked, that is a fail-stop — write the
report and stop rather than burning the run.

## Before you begin

1. `git status` is clean, and you are on the right branch cut from the right parent.
2. Read the reference repo's `docs/ai-job-search/01-architecture.md` and
   `02-data-flow.md` if you have not this session. Twenty minutes, and it prevents
   re-deriving decisions that are already made.
3. Confirm `codex` is on PATH: `codex --version`. If it is not, you are on tier 3 for the
   whole run — say so in the progress file.
4. Check the synthetic corpus exists (`fixtures/acme-d2c/`). Phase 2 cannot be gated
   without it; if phase 2 is in scope and it is missing, building it is the first task.

## The loop

Per phase:

1. Read the phase row in `BUILD_PLAN.md` §7. That is the contract.
2. Write the smallest thing that could satisfy it.
3. Commit. One commit per meaningful change — **not one per phase**.
4. Repeat until the gate below passes.
5. Write `PROGRESS_PHASE_<N>.md`.
6. Next phase.

**Commit from a file, never inline.** Write `.git/COMMIT_MSG`, then
`git commit -F .git/COMMIT_MSG`. See `CLAUDE.md` §Keep shell commands short — a long
inline command stalls an unattended run indefinitely.

**No `Co-Authored-By: Claude`. No mention of Claude in commit messages.** `CLAUDE.md`
rule 2. Easy to reintroduce by habit; check before every commit.

## The gate

All four, in order. A phase is not done until all four pass.

### 1. Tests pass

```
python -m unittest discover -s tests -t . -v
```

Zero failures. A skipped test is acceptable only with a comment saying why.

### 2. The client-data guard holds

From phase 0 onward, every phase re-runs it:

```
python tools/check_no_client_data.py
```

It must fail loudly when a file under `engagements/` is staged. **Verify it actually
fails** — stage a fixture, confirm non-zero exit, unstage. A guard nobody tested is not a
guard.

### 3. Independent review — three tiers

Per `CLAUDE.md`. Tier 1 Codex, tier 2 Codex on PS 5.1, tier 3 fresh Claude subagent.
Say which tier ran.

Point the reviewer at `AGENTS.md` and the specific files changed. For prompt files, ask
explicitly:

> *"Does this command file force the behaviour, or merely request it? Show me a reading
> where a hurried model skips the rule and the prose still permits it."*

That question finds more real defects in this repo than any other.

Report findings, including where you disagree. **Do not auto-apply them.**

### 4. Commit

Clean tree, all work committed, branch pushed.

## Fail-stop

Stop the run, write the report, do not continue, if:

- the same test fails three times with three different fixes
- a gate check cannot be made to pass and you have exhausted the obvious
- the design requires something `BUILD_PLAN.md` §5 forbids
- you would need to edit the reference repo
- client data has entered git — **stop immediately and report; do not attempt to clean
  history unattended**

A stopped run that reports honestly is a success. A run that pushes past a fail-stop is
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
that repo's defects (`docs/ai-job-search/04-findings.md`). But say so in the progress file;
a disagreement usually means one of the two is wrong.

**When the reference repo does something that looks wrong**, check
`docs/ai-job-search/04-findings.md` first. Several of its rough edges are already
catalogued — dead parsers with passing tests, a detail path that bypasses retry, a template
that renders off-page. Do not reproduce them, and do not spend the run re-discovering them.

**When something looks impossible**, it usually means a constraint is being read too
strictly. Write down which constraint and why, then either find the reading that makes it
possible or fail-stop. Do not quietly relax a rule from `BUILD_PLAN.md` §5.

## Two standing obligations

1. **The guard before the data.** No phase adds corpus-reading capability before phase 0's
   guard is verified working. If ordering ever conflicts with this, the guard wins.
2. **Prompt files get the same scrutiny as code.** They are the product. A vague rule in a
   `.md` file is a bug, and it is the kind this project will fail on if it fails.

## Final report

At the end of the run, write `RUN_REPORT.md`: what shipped, what each gate showed, what is
blocked, what the next runbook should cover, and anything you would tell the next agent.

Be honest about what did not work. That is the point of the report.
