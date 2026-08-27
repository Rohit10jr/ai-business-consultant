# TASK — start here

**ai-business-consultant** is a Claude Code harness that runs a consulting engagement end to
end. The pipeline is built. Phase 6 fixes two things the first engagement exposed.

---

## Already on `main` — do not rebuild

Eight commands, 166 tests, CI green. `/setup`, `/scope`, `/discover`, `/rank`,
`/investigate`, `/synthesize`, `/review`, `/outcome`, plus the client-data guard, the
synthetic corpus, and three validators.

The pipeline has been run on the synthetic client, Acme. `RUN_REPORT.md`'s final section is
the engagement it produced; `PROGRESS_PHASE_0.md` through `PROGRESS_PHASE_5.md` record what
each gate showed.

## Your assignment

**Two fixes. Then stop.**

| # | Fix | Why now |
|---|---|---|
| **1** | The ceiling denominator | Every ceiling in the deliverable is wrong by roughly a third, and `/review` already proved it |
| **2** | The calibration gate, then the calibration rule | The rule is blunt because the gate demanded it. Fix the gate first |

**Do not run the full pipeline.** That is phase 7, and it must be a different session — one
that did not make these fixes. Whoever fixes the harness cannot credibly demonstrate it,
for the same reason the phase 2-5 gates were graded by fresh subagents.

---

## Read in this order

| # | File | Why |
|---|---|---|
| 1 | [`CLAUDE.md`](CLAUDE.md) | The rules you are working under |
| 2 | [`RUN_REPORT.md`](RUN_REPORT.md) — the last two sections | The engagement, and what `/review` said about it. **Fix 1 is in there** |
| 3 | [`.claude/commands/investigate.md`](.claude/commands/investigate.md) Step 6 | Where the ceiling is defined |
| 4 | [`.claude/commands/synthesize.md`](.claude/commands/synthesize.md) | Where ceilings are combined into options |
| 5 | [`PROGRESS_PHASE_5.md`](PROGRESS_PHASE_5.md) — Findings from review | **Fix 2's argument, and the reviewer's objection to it** |
| 6 | [`RUNBOOK.md`](RUNBOOK.md) | The loop, the gates, fail-stop rules |
| 7 | [`AGENTS.md`](AGENTS.md) | What the reviewer will judge you on |

`BUILD_PLAN.md` §3 is the grounding contract and still governs everything.

---

## Fix 1 — the ceiling is measured against a frozen denominator

### The bug

`investigate.md` Step 6 defines `recoverable_at_most` as *"a cost delta over the same period
÷ the baseline's denominator"*. For Acme that gave **7.3044 pts** on the Supplier B cause.

`/review` showed that is wrong, and the main context reproduced it:

> the 7.30-pt ceiling is rupees over a **static denominator** — as a movement of the margin
> it is **+5.02 pts (19.72% → 24.74%)**, because re-earned returns lift net revenue too

The baseline is a *ratio*: contribution ÷ net revenue. Fixing the cause moves **both** terms —
a return that stops happening restores its revenue as well as its contribution. Dividing the
rupee recovery by the frozen denominator answers a question nobody asked.

It is not a rounding difference. It is roughly a third of the headline figure, it runs
through every ceiling in the deliverable, and `recommendation.md` still states **9.4483 pts**
for Option B while `RUN_REPORT.md` records the reviewer disproving it.

### What to build

**Record both figures, named so they cannot be confused.**

- `recoverable_at_most` — **rupees only.** Drop the "pts" unit from it entirely. This is the
  figure that compares between causes and is the right one to sum when checking that an
  option does not claim more than its causes contain.
- `baseline_movement_at_most` — the baseline metric **recomputed with the fix applied**:
  `from`, `to`, `delta`, unit, and a query whose output shows **both** the numerator and the
  denominator changing. This is the only figure that may ever be stated as "pts of the
  baseline" or compared against the baseline.

Where the movement cannot be computed, `not derivable — <why>` as elsewhere. A cause with a
rupee ceiling and no movement figure is honest; a cause quoting rupees ÷ frozen denominator
as "pts" is not.

### The second-order problem — do not skip this

`/synthesize` builds Option B by **adding** two causes' ceilings (7.3044 + 2.1439 = 9.4483).
Rupees add. **Baseline movements do not** — each is a ratio computed against a denominator
the other one also moves, so summing them overstates again, in the same direction.

An option combining causes must **recompute the movement jointly** — one query, both fixes
applied, one resulting margin — not add the parts. If a joint recomputation is not possible,
the option states its rupee total and says the movement is not derivable. Never add two
movement figures.

### Gate

| # | Must |
|---|---|
| 1 | `recoverable_at_most` carries a currency unit only; no ceiling is expressed in baseline points except via `baseline_movement_at_most` |
| 2 | The movement query's output shows numerator **and** denominator moving |
| 3 | `check_recommendation.py` rejects a ceiling stated in baseline units that is not sourced from a movement figure, and rejects any option whose movement is the sum of its causes' movements |
| 4 | Re-running `/investigate` on Acme's Supplier B cause reproduces **≈+5.02 pts**, matching what `/review` found independently |
| 5 | Tests cover both the single-cause and combined-option cases |

Item 4 is the real test: the number already exists, computed by an adversary that had never
seen this fix.

### Regenerating Acme's artifacts

`engagements/acme/investigation.json` and `recommendation.md` were written under the old
rule. Re-run `/investigate` and `/synthesize` for the affected causes to bring them into
line — a fresh subagent, per the usual procedure — **or**, if that is too expensive, leave
them and add one line at the top of `recommendation.md` naming the figure as superseded and
pointing at `RUN_REPORT.md`. Do not leave two documents silently disagreeing. Say which you
chose and why.

---

## Fix 2 — the calibration rule, and the gate that shaped it

### The bug is in the gate, not only the rule

`practice/frameworks.md` calibrates fixability by `25 × (a − r) / n`. At **n = 1** that is
the full ±25: one client, one rejection, one afternoon, and every future finding of that type
is marked down across every future engagement.

Phase 5's reviewer called it too blunt. The phase 5 agent disagreed, and its reasoning names
the actual cause:

> *`TASK.md`'s gate is "a recorded rejection must visibly change the next ranking": one
> rejection has to move the order, or the loop is decorative.*

That is correct — and it means **the gate dictated the rule.** A rule tuned so that one data
point swings a ranking is a rule tuned to pass a test. The agent's other defences (it
averages down, the human confirms, it moves fixability only) are all fair; they just do not
answer the objection, because the objection is about n = 1 and those are about n > 1.

**So fix the gate first, then let the rule follow from the honest question.** Do them in that
order and record the new gate before you touch the formula — otherwise you will fit the rule
to whatever you happen to build.

### The new gate

Replace *"a recorded rejection must visibly change the next ranking"* with something that
tests the mechanism rather than forcing a swing. It must require:

- The calibration's effect is **measurable within one run** — `rank_score_uncalibrated`
  beside `rank_score`, same agents, same raw scores. Phase 5 already built this; keep it.
- The strength is a **recorded, argued decision** in `frameworks.md`, next to the formula:
  what it does at n = 1, what it does at n = 5, and why that is the right trade for a
  practice that has just started.
- The run **tabulates the adjustment across row counts** — n = 1, 2, 5, mixed — so a reader
  sees the curve, not one point on it.
- Whether a single row may move a finding across a verdict band (`pursue` → `consider`) is
  **stated either way with its reasoning**. Both answers are defensible. Silence is not.

### The rule

Then change the formula, or argue in writing that it should stand. Shapes worth considering,
not prescriptions:

- **Shrinkage** — `25 × (a − r) / (n + k)`, so one row moves a fraction and evidence
  accumulates toward the full weight
- **A floor** — no adjustment until n reaches some minimum, with the rows still recorded
- **Confidence-scaled** — the adjustment's size tied to how consistent the rows are, not only
  how many

Whichever you choose, `frameworks.md` carries the formula, the reasoning, and the n-table,
because `/setup` reads the rule from that file rather than recomputing it.

**Do not remove the calibration.** A loop that records outcomes and changes nothing is the
thing phase 5 existed to avoid. The question is its strength, never its existence.

### Gate

| # | Must |
|---|---|
| 1 | The gate is rewritten in `TASK.md` and `RUNBOOK.md` **before** the formula changes, and the commit order shows it |
| 2 | `frameworks.md` carries the formula, its reasoning, and the adjustment at n = 1, 2, 5 |
| 3 | A single rejection's effect is stated as a number, and whether it can cross a verdict band is answered explicitly |
| 4 | `/setup` still reads the rule from the file, never from memory; `/outcome` still writes only `tracker.csv` |
| 5 | Nothing client-identifying still crosses into tracked `frameworks.md` — the phase 5 rule holds |

---

## The rules that have not changed

1. **Client data never enters git.** Re-prove the guard fails on a staged fixture.
2. **No number without a source.** `BUILD_PLAN.md` §3.
3. **No Claude attribution** — no `Co-Authored-By`, no mention in commit messages or PR text.
4. **Prompt files are the product.** *Does this force the behaviour, or merely request it?*
5. **Keep shell commands short.** Commit with `git commit -F .git/COMMIT_MSG`. Never
   `cat > file <<'EOF'`. Never `python - <<'PY'`.

## Grading

Same procedure as every phase: build here, run in a **fresh `general-purpose` subagent** with
the whitelist and do-not-read list, check its "Files read", grade afterwards. If you cannot
arrange it, mark the gate **unverified** rather than grading your own run.

## When you are done

1. `PROGRESS_PHASE_6.md` — format in `RUNBOOK.md`
2. `RUN_REPORT.md` — append this run. Do not delete what is there.
3. Branch `phase-6-fixes` pushed. **No merge to `main`** — the owner merges.

**Then stop.** Do not run the pipeline end to end; that is phase 7, deliberately a different
session. Say in the report whether Acme's artifacts were regenerated or annotated, because
phase 7 needs to know which it is starting from.
