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

### Make the changes. Run nothing.

**This phase spawns no subagents and runs no command against Acme.** Not `/investigate`, not
`/synthesize`, not `/rank` — not once, not "just to check". The owner's session budget is
committed elsewhere, and phases 3-5 spent most of theirs on exactly these runs: 20-30 minutes
and 150-300k tokens each, five of which hit session limits.

What you deliver is the changed commands, the changed checker, and tests that prove the new
rules on inputs you construct yourself. Unit tests are cheap and local; live runs are not.

**Every runtime gate below is therefore deliberately `unverified`,** and saying so is the
correct outcome — not a shortfall. It is the same discipline as phase 1, which recorded an
unverified gate honestly and was right to.

**Do not run the full pipeline either.** That is phase 7, and it must be a different session
— one that did not make these fixes. Whoever fixes the harness cannot credibly demonstrate
it, which is why every gate in this repo has been graded by a context that did not build the
thing.

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

**Checkable now, without running anything:**

| # | Must |
|---|---|
| 1 | `recoverable_at_most` carries a currency unit only; no ceiling is expressed in baseline points except via `baseline_movement_at_most` |
| 2 | `investigate.md` requires the movement query's output to show numerator **and** denominator moving, and says it in a way a hurried model cannot read past |
| 3 | `check_recommendation.py` rejects a ceiling stated in baseline units not sourced from a movement figure, and rejects an option whose movement is the sum of its causes' movements |
| 4 | Tests cover the single-cause and the combined-option cases, on inputs you construct — **hand-written JSON, not a live run** |
| 5 | A worked example in the command file walks Acme's Supplier B numbers through the new rule by hand: ₹46,121.67 recovered, net revenue rising with it, arriving at ≈+5.02 pts |

Item 5 is the substitute for running it, and it is a good one. `/review` derived +5.02
independently before this fix existed, so if your arithmetic does not reach it by hand, the
rule you have written is the wrong rule — and you learn that for the cost of a paragraph
rather than half an hour.

**Deferred to phase 7, recorded as `unverified`:** re-running `/investigate` on Acme's
Supplier B cause and reproducing ≈+5.02 pts live.

### Acme's artifacts — annotate, do not regenerate

`engagements/acme/investigation.json` and `recommendation.md` were written under the old
rule. **Do not re-run anything to fix them.** Add one line at the top of
`recommendation.md`: the ceiling figures are superseded by phase 6's rule, the corrected
Supplier B movement is ≈+5.02 pts rather than 7.30, and `RUN_REPORT.md` carries the
reviewer's finding. That closes the contradiction between the two documents at the cost of a
sentence. Phase 7 regenerates them properly, from a cold run.

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

### The gate, as rewritten (phase 6 — committed before the formula changed)

The calibration loop passes when **the mechanism is shown, not when a swing is forced**:

1. **Measurable within one run.** `/rank` records `rank_score_uncalibrated` beside
   `rank_score` and prints "Calibration moved: …" from the same agents and the same raw
   scores — every difference between the two orderings is the calibration's effect and
   nothing else. A comparison across two runs proves nothing, because fresh scoring agents
   move raw scores by ±1–3 on their own.
2. **A recorded, argued strength.** `practice/frameworks.md` carries the formula, and
   beside it what one row does, what five rows do, and why that is the right trade for a
   practice that has just started. The strength is a decision in a tracked file, never a
   number a command chose.
3. **The curve, not a point.** The same file tabulates the adjustment at n = 1, 2, 5 and a
   mixed case, so a reader sees how fast the practice learns and where it stops.
4. **Band-crossing answered either way.** Whether a single row may move a finding across
   a verdict band is stated, with the reasoning. Both answers are defensible; silence is
   not.
5. **The mechanics unchanged.** `/setup` reads the rule from the file and never from
   memory; `/outcome` writes only `tracker.csv`; nothing client-identifying crosses.

It does **not** require that one rejection reorder the next ranking. If one row moves a
finding across a band under the recorded rule, that is the rule's stated behaviour; if it
does not, the loop has still closed — the adjustment is recorded, visible, and will grow
with evidence. Whether the order moved is reported, not demanded.

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

All five are checkable by reading and by unit test. **Fix 2 needs no live run at all:** the
n-table is arithmetic, and whether `/setup` reads the rule from the file rather than from
memory is a property of the prose and the lint.

---

## The rules that have not changed

1. **Client data never enters git.** Re-prove the guard fails on a staged fixture.
2. **No number without a source.** `BUILD_PLAN.md` §3.
3. **No Claude attribution** — no `Co-Authored-By`, no mention in commit messages or PR text.
4. **Prompt files are the product.** *Does this force the behaviour, or merely request it?*
5. **Keep shell commands short.** Commit with `git commit -F .git/COMMIT_MSG`. Never
   `cat > file <<'EOF'`. Never `python - <<'PY'`.

## Grading

**No subagent runs this phase.** The usual fresh-context procedure is suspended — not because
it stopped mattering, but because the budget is committed elsewhere and phase 7 will do it
properly on a cold run.

So: unit tests, the lint, `python -m unittest discover -s tests -t .`, the client-data guard,
and a reading of the prose against the question that has found more defects here than any
other — *does this force the behaviour, or merely request it?* An independent review is still
worth running if `codex` is on PATH; that is not the constrained budget.

Mark every runtime gate **unverified** in the progress file, with the sentence that would
verify it, so phase 7 picks each one up without re-deriving what it was meant to show.

## When you are done

1. `PROGRESS_PHASE_6.md` — format in `RUNBOOK.md`
2. `RUN_REPORT.md` — append this run. Do not delete what is there.
3. Branch `phase-6-fixes` pushed. **No merge to `main`** — the owner merges.

**Then stop.** Do not run the pipeline end to end, and do not run any single command against
Acme; that is phase 7, deliberately a different session with a fresh budget.

`PROGRESS_PHASE_6.md` must list, in one place, **every gate left unverified and the exact run
that would verify it.** That list is phase 7's first task, and writing it well is most of
what this phase hands forward.
