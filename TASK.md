# TASK — start here

You are building **ai-business-consultant**, a Claude Code harness that runs a consulting
engagement end to end.

Phases 0, 1 and 2 are built, reviewed, merged to `main`, and **verified by live runs** —
not by reading the command files. Phases 3, 4 and 5 are yours, and they finish the pipeline.

---

## Already on `main` — do not rebuild

| Phase | Delivered | Verified how |
|---|---|---|
| **0** | Client-data guard (staged, tracked **and history**), CI, the synthetic corpus | Guard proven failing on a staged fixture; history scan proven on a commit-then-delete |
| **1** | `/setup`, `/scope` | `/scope acme` run live: handed a plausible 19% twice by the corpus, it refused both and computed the figure from the file |
| **2** | `/discover`, `/rank`, `preflight_csv.py`, `validate_findings.py` | Run live on the fixture corpus: found the joined finding, ignored the planted instruction, reported 5,475 de-duplicated rows, never touched the answer key |

95 tests pass, CI is green. `PROGRESS_PHASE_0/1/2.md` and `RUN_REPORT.md` record what each
gate showed and what is still soft.

## Your assignment

**Phases 3, 4 and 5, then a complete engagement.**

| Phase | Branch | Delivers |
|---|---|---|
| **3** | `phase-3-investigate` | `/investigate` |
| **4** | `phase-4-synthesize` | `/synthesize` + `/review` |
| **5** | `phase-5-outcome` | `/outcome` + calibration back into `/rank` |

**The deliverable is not the commands.** It is one complete engagement on Acme — scope →
discover → rank → investigate → synthesize → review → outcome — ending in the
**recommendation you would hand a founder**, with its evidence. Working commands that have
never been run end to end are not the assignment. See "The final deliverable" below.

---

## Read in this order

Roughly 45 minutes. Most design questions are already answered.

| # | File | Why |
|---|---|---|
| 1 | [`CLAUDE.md`](CLAUDE.md) | The rules you are working under |
| 2 | [`BUILD_PLAN.md`](BUILD_PLAN.md) | Architecture, **the grounding contract (§3)**, state model, settled decisions (§8) |
| 3 | [`docs/WORKED_EXAMPLE.md`](docs/WORKED_EXAMPLE.md) | One engagement end to end. What you are building, made concrete |
| 4 | [`.claude/commands/discover.md`](.claude/commands/discover.md) and [`rank.md`](.claude/commands/rank.md) | **The two commands you are extending.** Your output succeeds theirs; match their shape |
| 5 | [`docs/CONSULTING_METHOD.md`](docs/CONSULTING_METHOD.md) | The domain, as an algorithm — steps 8-13 are yours |
| 6 | [`RUNBOOK.md`](RUNBOOK.md) | The loop, the gates, fail-stop rules, progress format |
| 7 | [`AGENTS.md`](AGENTS.md) | What the reviewer will judge you on. Read it before writing, not after |

**Optional, for depth:** the reference implementation at
`D:\02_Personal\01_OpenSource\03_Applications\ai-job-search`. Read-only — never edit it,
never run git in it. `docs/REFERENCE_PATTERN.md` distils what matters.

---

## The five things that matter most

1. **Client data never enters git.** `engagements/` is gitignored and the CI guard checks
   staged paths, tracked paths **and every path ever added to history** — `git rm` clears
   the tree and never the history. Re-prove it fails on a staged fixture as part of your
   gate.

2. **No number without a source, and no cause without a counter-hypothesis.** Phases 0-2
   established the first half: every figure traces to a query executed in that run. Your
   phases add the second. A cause asserted without stating what else would produce the same
   numbers is not a finding, it is a hunch with decimals.

3. **No Claude attribution.** No `Co-Authored-By` trailer, no crediting Claude in commit
   messages, PR text or release notes. Naming the file `CLAUDE.md` or writing "Claude Code
   harness" is fine — those are a filename and a platform.

4. **Prompt files are the product.** You are mostly writing markdown that an LLM executes.
   A vague rule in a `.md` file is a bug. The test is always: *does this force the behaviour
   or merely request it?* Phase 2 shipped two rules that read fine and did nothing until
   they were tightened; both were caught by a reviewer, not by the author.

5. **Keep shell commands short.** A command over ~400 characters escalates to human review
   and stalls an unattended run. Commit with `git commit -F .git/COMMIT_MSG`. Never
   `cat > file <<'EOF'`. Never `python - <<'PY'`. Use the Write tool.

---

## Phase 3 in detail — `/investigate`

`/discover` says *what* is in the data. `/rank` says *which of it matters*. `/investigate`
says **why**, and proves it is not something else.

### What you are building

`/investigate <client>` reads `engagements/<client>/findings.json`, takes the findings the
human selects from the ranked list, and writes `engagements/<client>/investigation.json`.
It builds the case on each: the mechanism, the evidence, and the alternatives it ruled out.

It does not recommend. Recommendations are `/synthesize`, in phase 4.

### The counter-hypothesis rule

Before any cause may be asserted, the command must state **what else would produce the same
numbers**, and rule each one out with a query — or record that it could not, and weaken the
claim to match. An investigation with an empty counter-hypothesis list is not an
investigation.

The corpus is built to punish skipping this. The current top finding is
`return-rate-doubled`. Apparel returns rose **14.75 points**, and the decomposition is:

| Component | Points |
|---|---|
| Supplier B's own rate rise | +9.93 |
| **Supplier A's own rate rise** | **+3.04** |
| Interaction (B's share grew while its rate exploded) | +1.82 |
| Pure mix at the old rates | −0.03 |

**Pure mix is almost zero**, because in Q3 FY24 both suppliers returned at nearly the same
rate. So an investigator who checks "did the mix change?", sees ≈0, and concludes "therefore
it is all quality" has performed the check and still reached the wrong answer. A fifth of
the rise belongs to a supplier the naive story never mentions. `/discover` already records
`mix_at_boundaries` on those findings, so the check is possible from the file.

### The allocation rule

Phase 2 produced two `/discover` runs that disagreed about the same segment:

> Orders under ₹999 earned **26.1% vs 28.4%** contribution before marketing — a 2.3 point
> gap, judged not a finding. After marketing was allocated to orders: **7.4% vs 21.5%** — a
> 14 point gap, and one run's headline finding.

Same corpus, same rows, same arithmetic. The entire difference is a choice about how shared
spend is attributed. Six of eleven findings in the current file record
`second_derivation: partial` for exactly this reason.

So: **every figure that depends on an allocation must say so, and must be reported alongside
its allocation-free counterpart.** A conclusion that survives only under one allocation is a
conclusion about the allocation. Say which, state the rule used, and show both numbers.

### The gate

- Separates **rate from mix** on the Supplier B finding, and names Supplier A's contribution
- Every allocation-dependent figure paired with its allocation-free counterpart
- Every counter-hypothesis either ruled out with a query, or recorded as not ruled out with
  the claim weakened to match
- A figure missing its source is **removed, not softened** — the phase-3 gate in
  `BUILD_PLAN.md` §7
- `validate_findings.py` extended (not duplicated) to cover the new keys, and passing
- Never reads `fixtures/` — the answer key lives there

---

## Phase 4 in detail — `/synthesize` and `/review`

**`/synthesize <client>`** turns investigated findings into the "so what": one
recommendation with **2-3 options** and their trade-offs, each tied back to the scope
baseline in its own unit. Costs, sequencing, what you would do first and why. This is the
document a human presents.

**`/review <client>`** is an adversarial agent whose job is to **kill** it. Fresh context,
content passed inline, a whitelist of readable files, and a two-part output contract —
structured edits plus prose critique. `/discover`'s subagent handling is the local pattern;
the reference repo's `apply.md` reviewer is the original.

### Two gates, because one is circular

The plan says *"reviewer kills a deliberately planted bad inference"*. That cannot be tested
against a good investigation, and it proves nothing if one context wrote both the flaw and
the reviewer. So:

| Test | Input | Passes when |
|---|---|---|
| Is `/investigate` sound? | the real corpus, fresh session | it separates mix from rate unprompted |
| Is `/review` adversarial? | **`fixtures/bad-investigation/`** | it kills the recommendation |

**Build the bad-investigation fixture first.** Its full specification — the exact figures,
what it must claim, what it must omit, and what `/review` must catch — is in
[`fixtures/bad-investigation/README.md`](fixtures/bad-investigation/README.md). Read it
before writing `/review`, because it defines what "adversarial enough" means.

The pass bar is specific: the review must name **Supplier A's 3.04 points**, not merely ask
"have you considered other factors?". Generic scepticism is free and proves nothing.

---

## Phase 5 in detail — `/outcome` and calibration

This is the phase that makes it a practice rather than a report generator.

**`/outcome <client>`** records what the client actually did with each recommendation —
`accepted` / `modified` / `rejected` — and why, into `practice/tracker.csv`.

Then it has to **change something**, or the loop is decorative. The chain:

```
/outcome  →  practice/tracker.csv        (gitignored — it names real clients)
/setup    →  reads tracker.csv, proposes changes to practice/frameworks.md
/rank     →  reads frameworks.md, orders differently next time
```

### Two constraints that are easy to break

**Single writer survives.** `/outcome` owns `tracker.csv`. **`/setup` remains the only
writer of `frameworks.md`** — phase 1 said so deliberately and deferred this:

> *"`/setup` never reads or writes `practice/tracker.csv` in this phase. Calibrating the
> profile from recorded outcomes is a later phase's concern and will be added to this file
> explicitly when it is designed."*

This is now that phase, so **you will edit `/setup`** — the first time a later phase reaches
back into an earlier one. Do it in `setup.md` explicitly, and delete that deferral sentence.
The tempting shortcut is letting `/outcome` write the weights directly. It breaks the model
and every later phase inherits the breakage.

**Confidentiality survives the crossing.** `tracker.csv` is gitignored and may hold client
names. `frameworks.md` is **tracked** and may not. So what `/setup` carries across must be
generalised — sector, size band, engagement type, finding type, outcome. "A D2C apparel
brand rejected a channel-spend recommendation" is fine. "Acme rejected cutting Meta" is not.
`/setup`'s existing confidentiality rule already says this; make sure the new path obeys it.

### The gate

A recorded rejection must visibly change the next ranking. That needs a before and after:

```
/rank acme --all          →  record the order
/outcome acme             →  reject one recommendation
/setup frameworks         →  apply the calibration
/rank acme --all          →  the order has moved
```

Show both orderings and the diff in `PROGRESS_PHASE_5.md`. If the order does not move, the
loop does not close, and saying so honestly is the correct outcome of the phase.

---

## Grading without cheating

You will read `fixtures/acme-d2c/EXPECTED.md` and `fixtures/bad-investigation/README.md` to
build the gates. A run in that same context already knows the answers and will produce them
for the wrong reason. **A contaminated pass is worse than no run**, because the next phase
gets built on a gate you wrongly believe is proven.

Phase 2 solved this and it worked — reuse the pattern rather than re-deriving it:

1. Build the command.
2. Run it in a **fresh `general-purpose` subagent** (not a fork — a fork inherits your
   context), told to read only the command file, the tools it names, `engagements/<client>/`
   and `practice/`, and told explicitly not to open `fixtures/`, `docs/`, `TASK.md`,
   `RUNBOOK.md`, progress files or `scratch/`.
3. Require it to append a **"Files read"** list to its report, and check that list.
4. Grade the saved output against the answer key afterwards, here.

If you cannot arrange step 2, **say so and mark the gate unverified**. Do not grade your own
run and call it a pass.

---

## The final deliverable

After phase 5's gate, run the whole pipeline on Acme in order and keep the output:

```
/scope → /discover → /rank → /investigate → /synthesize → /review → /outcome
```

Write **`RUN_REPORT.md`**'s final section as the engagement itself: the question, the
baseline, the top findings with their magnitudes in the baseline's unit, the recommendation
with its options, what `/review` attacked and whether it survived, and what a founder would
be asked to decide.

That document is the deliverable. It is what the owner will read to judge whether the
harness works — not the test count.

Everything under `engagements/` stays gitignored. Quote figures into `RUN_REPORT.md` freely:
Acme is synthetic and its corpus is tracked in `fixtures/`.

---

## When you are done

1. `PROGRESS_PHASE_3.md`, `PROGRESS_PHASE_4.md`, `PROGRESS_PHASE_5.md` — format in
   `RUNBOOK.md`
2. `RUN_REPORT.md` — append this run, ending with the engagement deliverable above. Do not
   delete the phase 0-2 history already there.
3. All three branches pushed. **No merge to `main`** — the owner merges.

Be honest in the report about what did not work. Phase 1 recorded an unverified gate
plainly, which is the only reason it was caught and closed. A stopped run that reports
clearly is a success; a run that pushes past a fail-stop is not, however much it produced.
