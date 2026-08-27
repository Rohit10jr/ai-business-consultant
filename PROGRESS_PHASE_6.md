# Phase 6 — PASS (runtime gates unverified by design)   [branch: phase-6-fixes]

Two corrections the first engagement exposed. **Nothing was run against Acme and no
subagent was spawned**, per `TASK.md`: every rule below is proved on hand-written inputs
and by reading; every runtime gate is recorded `unverified` with the run that would verify
it, for phase 7.

## What shipped

**Fix 1 — the ceiling denominator**
- `.claude/commands/investigate.md` Step 6: `recoverable_at_most` is **rupees only**; a new `baseline_movement_at_most` is the baseline **recomputed with the fix applied** — `numerator_from/to/delta`, `denominator_from/to/delta`, `from`, `to`, `delta` — from a query whose printed output shows both terms before and after, with `denominator_unchanged_because` required when the denominator does not move. Rule 7b: rupees ÷ frozen denominator is written nowhere. A worked example walks Acme's Supplier B numbers by hand: ₹124,540.03 / ₹631,425.85 = 19.72% → (+₹46,121.67) / (+₹58,370) → ₹170,661.70 / ₹689,795.85 = **24.74%, +5.02 pts**, against the 7.30 the frozen denominator gave.
- `tools/validate_findings.py`: refuses a points unit on `recoverable_at_most`; requires every movement term; checks `from`/`to` are the recomputed ratios and `delta = to − from`; requires a reason for an unmoved denominator. Movement terms join the "number from nowhere" check.
- `.claude/commands/synthesize.md`: options are sized in rupees (rupees add) and their movement is **recomputed jointly** — `to = 100 × (n₀ + Δn₁ + Δn₂) / (d₀ + Δd₁ + Δd₂)` in one Arithmetic line — never the sum of two movements; causes that overlap are not combined. The Option template carries a rupee `Ceiling:` line and a separate `Movement:` line.
- `tools/check_recommendation.py`: a `- Ceiling:` line may carry no points/percent unit and must be a `recoverable_at_most` value or a sum of them; a `- Movement:` figure must be a recorded movement term or a ratio recomputed in the Arithmetic section; any figure equal to the sum of two or more causes' movement deltas is refused even when an Arithmetic line produced it; the literal `100` is the only unrecorded term a ratio line may carry.
- `fixtures/bad-investigation/`: rebuilt under the new shape — rupee ceiling (₹19,880.79/quarter), a true movement figure (20.27% → 21.16%, +0.89 pts, both terms shown by `q02_saving.py`), still failing the validator on exactly its five counter-hypothesis omissions, Supplier A still absent.
- `engagements/acme/recommendation.md` (gitignored): one note at the top — figures superseded, Supplier B ≈ +5.02 pts not 7.30, Option B's 9.4483 not a movement, rupees stand. Not regenerated.
- Tests: `test_validate_investigation.py` (+6), `test_check_recommendation.py` (rewritten: single cause, combined option, sum-of-movements, frozen-denominator ceiling, points-unit ceiling), lint (+2).

**Fix 2 — the calibration gate, then the rule** (two commits, gate first)
- `TASK.md` §"The gate, as rewritten" and `RUNBOOK.md` §"The calibration gate, standing": the loop passes when the mechanism is shown — effect measurable within one run, an argued strength in the tracked file, the curve tabulated, band-crossing answered either way, mechanics unchanged. Whether one rejection reorders the ranking is reported, not demanded. Committed as `4a1bb27`, before the formula.
- `practice/frameworks.md`: `adjustment = round(25 × (accepted − rejected) / (rows + 2)), capped at +10`, rounded half away from zero. One row ±8, two −13, five −18, ten −21, mixed 3/2 +4; the full 25 is a limit reached only with dozens of one-sided rows. Reasoning stated; band-crossing answered *yes, accepted* (±2.4 score points, below the ±1–3 noise of fresh agents, never silent because `/rank` names every finding whose position or band changed). The live rows `/setup` had written under the old rule are **cleared** to the placeholder with a note — not recomputed by hand, because `/setup` is the file's only writer; U5 regenerates them.
- After review: `baseline_movement_at_most` carries `query_output` and the validator finds all four terms in it; a points-of-the-baseline unit is refused on any figure but the movement; `overlaps` records a `shared_rows` count per pair of causes and `/synthesize` combines only pairs at zero; `check_recommendation.py` accepts a ratio as a movement only when rebuilt from `numerator_from + Δ` over `denominator_from + Δ`, and polices points of the baseline across the whole document; `/rank`'s "Calibration moved" line names verdict-band changes.
- `.claude/commands/setup.md`: the arithmetic example follows the file's formula and says the file is the authority.
- `tests/test_calibration_rule.py`: reads the formula from `frameworks.md` and checks every n-table row and every live row against it, so the rule and its tables cannot drift apart.

## Gate
| Check | Result |
|---|---|
| Tests | 186 passing, 0 skipped, 0 failing |
| Client-data guard | re-proved: staged `engagements/zzz-guard-proof/pnl.csv` → failure naming the path; unstaged → OK |
| Review | tier 1 — Codex, 190k tokens. See below |
| Phase gate | Fix 1: 5/5 checkable-now items; Fix 2: 5/5. Runtime items `unverified` — listed below |
| Commits | 5 on this branch (`c2e8998` fix 1, `4a1bb27` gate, `388c68f` rule, the review fixes, then this file with `RUN_REPORT.md`) |

### Fix 1 gate — checkable now

| # | Must | Result |
|---|---|---|
| 1 | `recoverable_at_most` currency only; no ceiling in baseline points except via `baseline_movement_at_most` | **PASS** — validator refuses a points unit (`test_recoverable_at_most_must_be_a_currency`); checker refuses a points/percent `Ceiling:` line even when the number is a real movement (`test_ceiling_in_points_is_rejected_even_when_the_number_exists`) |
| 2 | `investigate.md` requires the movement query's output to show numerator **and** denominator moving, unmissably | **PASS by reading** — Step 6 bolds it, the schema names both terms, the validator refuses a movement missing either (`test_movement_needs_both_terms_before_and_after`) and one whose ratio was not recomputed (`test_movement_ratio_is_recomputed_not_copied`) |
| 3 | checker rejects a ceiling in baseline units not from a movement figure, and an option whose movement is the sum of its causes' movements | **PASS** — `test_frozen_denominator_figure_cannot_be_a_ceiling` (7.30 = 46,121.67 ÷ 631,425.85 refused), `test_sum_of_two_movements_is_rejected` (5.02 + 2.15 = 7.17 refused even from an Arithmetic line) |
| 4 | tests cover single-cause and combined-option cases on hand-written inputs | **PASS** — `MovementTests` (single cause from the record; joint recomputation 26.70% / +6.98 accepted; sum refused; figure from nowhere refused; non-ratio laundering refused) |
| 5 | worked example reaches ≈+5.02 by hand | **PASS** — 170,661.70 ÷ 689,795.85 = 24.74%; 24.74 − 19.72 = 5.02; pinned by the lint and by `test_hand_worked_supplier_b_example_passes` |

### Fix 2 gate — checkable now

| # | Must | Result |
|---|---|---|
| 1 | gate rewritten in `TASK.md` and `RUNBOOK.md` **before** the formula, commit order shows it | **PASS** — `4a1bb27` (gate) precedes the rule commit; the gate commit touches no formula |
| 2 | `frameworks.md` carries the formula, its reasoning, and the adjustment at n = 1, 2, 5 | **PASS** — table at n = 1, 1, 2, 5, 5 (mixed), 10; `test_n_table_matches_the_formula` |
| 3 | a single rejection's effect stated as a number; band-crossing answered explicitly | **PASS** — −8 fixability, ±2.4 score points; "Yes, and that is accepted", with reasoning; `test_single_row_effect_is_stated_and_band_crossing_is_answered` |
| 4 | `/setup` reads the rule from the file; `/outcome` writes only `tracker.csv` | **PASS by reading** — `setup.md` Step 2b unchanged in mechanism ("read the rule from the file; do not recompute it from memory"), example follows the file; `outcome.md` untouched; lint unchanged and green |
| 5 | nothing client-identifying crosses | **PASS by reading** — the phase-5 rule (structured columns only) is untouched; the live rows changed only in their adjustment column |

### Runtime gates — `unverified`, and the run that would verify each

| # | What phase 7 must run | Passes when |
|---|---|---|
| U1 | `/investigate acme supplier-b-returns-negative-contribution` in a fresh session | `baseline_movement_at_most` ≈ 19.72% → 24.74% (+5.02 pts) with `numerator_delta` ≈ 46,121.67 and `denominator_delta` ≈ 58,370; `recoverable_at_most` in rupees; validator clean |
| U2 | `/investigate acme meta-cac-doubled` (or any cause that moves only the numerator) | the movement carries `denominator_unchanged_because`, or a denominator delta with its reason |
| U3 | `/synthesize acme` on the regenerated investigation | Option B's `Movement:` line is one joint division over both terms (≈ 26–27%), not 5.02 + 2.14; `check_recommendation.py` clean |
| U4 | `/review acme` on the regenerated recommendation | the reviewer no longer wounds the ceilings on the denominator point |
| U5 | `/setup frameworks` on the existing tracker (2 rows), the table now empty | proposes `supplier +8`, `channel-spend −8` from the file's formula with the arithmetic shown; nothing from `pushback`/`notes` crosses |
| U6 | `/rank acme --all` after U5 | "Calibration moved: …" line from one run, naming position and verdict changes; `google-cac-flat` fixability 80 → 72 (−8, not −25), score 80 → ≈77.6; whether it still leaves `pursue` is reported, not demanded |
| U8 | `/investigate acme` with two or more slugs | `overlaps` carries a `shared_rows` count per pair from a query; the return-rate cause and the Supplier B cause are recorded as overlapping (the same returns), and `/synthesize` declines to combine them |
| U7 | the whole pipeline cold, `/scope` → `/outcome`, in a session that did not make these fixes | the engagement section of `RUN_REPORT.md` regenerated with rupee ceilings and recomputed movements |

## Findings from review
Tier 1, Codex (`codex exec -s read-only`, PS7), ~15 minutes, 190k tokens. It verified the worked example arithmetically (19.7236% → 24.7409%, +5.0173), the commit order, the n-table row by row, and that the fixture fails only on its five omissions. Eight findings: seven applied, one was true at review time and is closed by this commit.

- **Blocker — any Arithmetic line with a `/` counted as a recomputed ratio**, so the frozen-denominator bug itself (`7.30 = 100 × 46,121.67 / 631,425.85`) passed as a `Movement:` line; the reviewer ran `check()` and got `[]`. **Applied** — a movement-grade ratio must be rebuilt from the baseline's own terms: a recorded `numerator_from` plus a `numerator_delta` over a recorded `denominator_from` plus a `denominator_delta`. And points of the baseline are policed across the whole document: "7.30% of revenue" in prose must be a movement figure or a rebuilt ratio; a bare "7.30 pts" must be a recorded figure or a movement, never a number that exists only through the Arithmetic section. Both of the reviewer's examples are now tests.
- **The validator could not see that the query printed both terms.** **Applied** — `baseline_movement_at_most` carries `query_output` verbatim and the validator looks for all four terms in it; a term typed into the JSON fails.
- **Points figures could still be recorded as evidence and then cited.** **Applied** — a unit claiming points of the baseline is refused on evidence, re-derived and allocation figures; points of a rate (a decomposition term) are untouched.
- **Overlap between causes was admitted, not enforced.** **Applied** — with two or more causes investigated, `overlaps` must carry a `shared_rows` count from a query for every pair, and `/synthesize` may combine only a pair recorded at zero. The row-provenance question the run report raised is closed this way rather than by tagging rows.
- **"Calibration moved" compared ordering, not verdict bands** — a `consider` → `pursue` crossing with no position change would print "moved nothing". **Applied** — the line names every finding whose position *or* band changed; `frameworks.md`'s band-crossing argument now claims only that.
- **The hand-edited calibration rows violated "written by `/setup` only"; the note disclosed it, it did not make it consistent.** **Applied, the reviewer's way** — the rows are cleared to the placeholder with a note that `/setup frameworks` regenerates them from the file's formula; the tracker still holds the two rows. A derived table whose rule changed is stale data, and clearing it is what a rule change does to a cache.
- **The calibration test could be silently disabled** by deleting the live table, and its formula regex searched the whole file. **Applied** — rows or the placeholder must be present, and the formula is read from the Calibration section only.
- **The reports claimed four commits pushed while git showed three and uncommitted docs.** True when the reviewer ran, before the docs commit; the counts below are as of that commit.

Confirmed right by the reviewer: the rupee/movement split is conceptually right; the worked example is honest about why the two deltas differ; the gate rewrite tests the mechanism rather than softening the old gate; commit order holds; the n-table matches the formula; the fixture still has to be killed on inference.

## Decisions made
- **Two figures, not one corrected figure.** Rupees compare and add between causes; the movement is a ratio and does neither. Keeping both, named, is what lets the checker refuse the wrong operation on each.
- **A combined option's movement is rebuilt from the recorded terms, not from a new query.** `/synthesize` runs no queries. `(n₀ + ΣΔn) / (d₀ + ΣΔd)` is exactly what a joint query would compute when the causes act on different rows, and it is one division in the Arithmetic section that the checker evaluates. Overlapping causes are not combined. This satisfies `TASK.md`'s "never add two movement figures" without giving `/synthesize` a query it must not have.
- **The literal `100` is the only unrecorded term a ratio line may carry.** Any other bare multiplier would launder a figure through the Arithmetic section.
- **Shrinkage with k = 2**, over a floor or confidence scaling: it keeps one row visible (−8, not 0), keeps the loop non-decorative, and reaches the full weight only with evidence; a floor would silence the first rows entirely, and confidence scaling needs more rows than any new practice has.
- **Band-crossing by one row: allowed, and reported.** The alternative — a rule that a single row may never cross a band — would need band-aware clamping in `/rank`, which is a second mechanism to reason about for a case the "Calibration moved" line already makes visible.
- **The live calibration rows were cleared, not recomputed by hand.** My first instinct was to recompute them (+8 / −8) with a note; the reviewer was right that a hand edit with a promise is still a hand edit to a file `/setup` alone writes. A derived table whose rule changed is stale, and a cleared cache with a note is the honest state. `U5` regenerates it.
- **Acme's artifacts annotated, not regenerated.** One note at the top of `recommendation.md`; `investigation.json` untouched (it fails the new validator on shape, which phase 7's cold run resolves).

## Blocked or deferred
- Everything in the runtime table above, by design.
- `engagements/acme/investigation.json` now fails `validate_findings.py` — confirmed: three entries each `missing keys ['baseline_movement_at_most']` (the points unit on `recoverable_at_most` would be the next error). `check_recommendation.py` on the old `recommendation.md` refuses the `7.3044 pts` ceiling line, and flags the superseding note's own 19.72 / 24.74 / 5.02 as figures from nowhere, which they are in that record. Intentional: both were written under the old rule, `TASK.md` says not to regenerate them here, and `/synthesize` and `/review` refuse them until phase 7 regenerates them from a cold run.

## For the next phase
- Phase 7's first task is the runtime table above, U1 → U8, each in a session that did not make these fixes.
- `scratch/` on this machine still holds every phase 3–5 run's report and query scripts; phase 7's cold run should start from a clean `scratch/acme/`.
