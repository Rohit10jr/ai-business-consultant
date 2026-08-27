# Phase 5 — PASS   [branch: phase-5-outcome]

## What shipped
- `.claude/commands/outcome.md`: `/outcome <client>` — lists the recommended option and every other option with their slugs, claims and strengths; proposes a finding type per slug from the taxonomy in `practice/frameworks.md`; asks outcome (accepted / modified / rejected / skip), finding type, pushback and detail one option at a time; shows each row and writes it only on "yes"; appends to `practice/tracker.csv` with a fixed 12-column header via the `csv` module; never edits `domains.md`, `frameworks.md` or anything under `engagements/`. The client name stops in the gitignored tracker.
- `practice/frameworks.md`: a **Finding types** list (eleven types) and a **Calibration** table with its rule stated in the file — `adjustment = round(25 × (accepted − rejected) / rows)`, floored at −40, capped at +10, `modified` counting as neither.
- `.claude/commands/setup.md`: the phase-1 deferral sentence deleted; Step 2b added — `/setup frameworks` reads the tracker (read-only), aggregates by finding type, applies the rule *from the file*, and proposes the replacement Calibration table as one confirmed change, plus generalised lessons; the `client` column never crosses. Runs on the tracker alone when `documents/practice/` is absent.
- `.claude/commands/rank.md`: scoring agents assign `finding_type` from the list pasted inline; the main context adds the Calibration adjustment to fixability before weighting (`fixability_calibrated = clamp(fixability + adjustment[finding_type], 0, 100)`), records `rank_finding_type`, `rank_fixability_raw`, `rank_calibration`, `rank_fixability_calibrated`, and reports what it applied.
- `tests/test_command_files.py`: lint for `/outcome` and the calibration path in `/rank` and `/setup`. 164 tests.

## Gate
| Check | Result |
|---|---|
| Tests | 166 passing, 0 skipped, 0 failing |
| Client-data guard | re-proved: `git add -f engagements/zzz-guard-proof/pnl.csv` → exit 1 naming the path; unstaged → OK (66 paths ever added across all refs, none client) |
| Review | tier 1 — Codex (`codex exec -s read-only`, PS7), 126k tokens. See below |
| Phase gate | 4/4, on fresh-context runs |
| Commits | 3 (`444f8b4` commands + taxonomy + calibration, `5feefc9` review fixes, then this file with the calibrated `frameworks.md` and `RUN_REPORT.md`) |

### Phase 5's own gate (RUNBOOK.md §5)

| # | Must | Result |
|---|---|---|
| 1 | `/outcome` writes only `practice/tracker.csv`; `/setup` remains the only writer of `frameworks.md` | **PASS.** After `/outcome acme` (fresh subagent, human answers scripted): `git status` showed nothing modified, `practice/tracker.csv` created with the 12-column header and two rows, gitignored by the `*.csv` rule. After `/setup frameworks` (fresh subagent): `git status` showed exactly `M practice/frameworks.md`; the tracker was read via the `csv` module and its byte count did not change. Both runs' "Files read" lists inside their whitelists |
| 2 | Nothing client-identifying crosses from `tracker.csv` into tracked `frameworks.md` | **PASS, on the second run.** The first `/setup frameworks` run crossed two Calibration rows (`supplier` 1/1/0/0 → +10; `channel-spend` 1/0/0/1 → −25, arithmetic shown) and two Lessons lines that named sector, size band, engagement type, year, finding type, outcome — and paraphrased the pushback with roles ("the marketing lead asked for an alternative rather than a cut, and the founder sided with her"). No client name (`grep -ci acme` = 0), but the review was right that a paraphrased pushback identifies the engagement to anyone who was in the room. `frameworks.md` was restored to HEAD, the rule tightened (structured columns only; `pushback`/`notes` never cross), and `/setup frameworks` repeated: the same two Calibration rows and two Lessons of the form *"A D2C apparel brand (under ₹5 Cr revenue), margin diagnosis, 2026: a channel-spend recommendation was rejected."* Nothing else crossed. The first run's output is kept at `scratch/frameworks_after_setup_run1.md` |
| 3 | rank → outcome(rejected) → setup → rank again, and the ordering visibly moves | **PASS.** Four fresh-subagent runs in sequence. `/rank acme --all` with an empty Calibration table ("applied to 0 findings"); `/outcome acme` recording `meta-cac-doubled` (type `channel-spend`) **rejected** and `supplier-b-returns-negative-contribution` (type `supplier`) accepted; `/setup frameworks` writing `channel-spend −25`, `supplier +10`; `/rank acme --all` again: "Calibration: applied to 1 finding, type `channel-spend` (−25) — `google-cac-flat`, fixability 80 → 55, which moved it from 79/pursue to 72/consider." The finding that moved is not the one rejected: the practice learned about a *kind* of recommendation, and the next finding of that kind paid for it. The after-run's own counterfactual: without the adjustment it would have scored 79 and ranked first |
| 4 | Both orderings and the diff shown | **PASS.** See below |

**Before** (`scratch/rank_run_acme_before.md`, calibration table empty):

| # | Score | Verdict | Finding | Type |
|---|---|---|---|---|
| 1 | 80 | pursue | google-cac-flat | channel-spend |
| 2 | 78 | pursue | courier-base-rate-six-percent-every-january | shipping-logistics |
| 3 | 72 | consider | first-order-return-rate-doubled | returns-quality |
| 4 | 68 | consider | discount-codes-stack-since-checkout-change | discount-policy |
| 5 | 64 | consider | courier-cost-on-returned-orders | returns-quality |
| 6 | 60 | consider | unit-cost-drift-above-2023-cost-sheet | unit-cost |
| 7 | 57 | consider | free-shipping-threshold-applied-post-discount | shipping-logistics |

**After** (`scratch/rank_run_acme_after.md`, on the post-review `rank.md`; `channel-spend −25`, `supplier +10`):

| # | Score uncal. → cal. | Verdict | Finding | Type | Fix raw → cal. |
|---|---|---|---|---|---|
| 1 | 77 → 77 | pursue | courier-base-rate-six-percent-every-january | shipping-logistics | 65 → 65 |
| 2 | **80 → 72** | consider | **google-cac-flat** | channel-spend | **80 → 55** |
| 3 | 70 → 70 | consider | discount-codes-stack-since-checkout-change | discount-policy | 90 → 90 |
| 4 | 67 → 67 | consider | first-order-return-rate-doubled | returns-quality | 40 → 40 |
| 5 | 63 → 63 | consider | courier-cost-on-returned-orders | returns-quality | 55 → 55 |
| 6 | 61 → 61 | consider | unit-cost-drift-above-2023-cost-sheet | unit-cost | 45 → 45 |
| 7 | 59 → 59 | consider | free-shipping-threshold-applied-post-discount | shipping-logistics | 95 → 95 |

**The run's own line:** *"Calibration moved: `courier-base-rate-six-percent-every-january` #2 → #1 (score 77 → 77), `google-cac-flat` #1 → #2 (score 80 → 72)."* That comparison is within one run — same agents, same raw scores — so it is the calibration's effect and nothing else, which is what the review's blocker demanded. Across runs the picture is the same: `google-cac-flat` led the before-run at 80 and leads the after-run's *uncalibrated* column at 80; the −25 on its type (−7.5 points at the 30% weight) is what takes it to 72 and *consider*. Fresh agents' raw scores wander ±1–3 between runs (courier 78 → 77, discount 68 → 70), and positions 3–4 swapped on that noise; the calibration's 8-point move is the only change larger than the noise. A first after-run on the pre-review `rank.md` (`scratch/rank_run_acme_after_run1.md`) showed the same move (google 79 → 72) and stated the counterfactual in prose. In every run the three investigated findings were skipped by `--all`'s rule and the margin bridge was vetoed; the `supplier +10` row matched none of the seven scored.

## Findings from review
Tier 1, Codex (`codex exec -s read-only`, PS7), ~10 minutes, 126k tokens. Four findings: three applied, one disagreed with.

- **Blocker — the phase gate could pass for the wrong reason.** `--all` re-scores with fresh agents, so an order that moves between two runs may be noise, not calibration. **Applied** — `/rank` now records `rank_score_uncalibrated` beside `rank_score` and reports, *within one run*, every position the calibration changed ("Calibration moved: …") — same agents, same raw scores, one run. The gate table below uses that line from the re-run rather than a cross-run comparison. (The first after-run had already stated the counterfactual in prose: without the adjustment `google-cac-flat` would have scored 79 and tied for first.)
- **Blocker — free-text `pushback` could feed tracked Lessons.** The Step 4 re-scan only knew identifiers found in documents, so a client-specific phrase paraphrased from the tracker would pass. **Applied** — Lessons are built from the structured columns only (sector, size band, engagement type, year, finding type, outcome); `pushback` and `notes` never cross, quoted or paraphrased; the re-scan list gains every value of the tracker's `client`, `pushback` and `notes` columns the moment the file is opened. The first `/setup` run had written two lessons that paraphrased pushback ("the marketing lead asked for an alternative rather than a cut, and the founder sided with her") — no name, but exactly the kind of sentence the reviewer meant; `frameworks.md` was restored and `/setup frameworks` repeated on the fixed file.
- **Correction rows did not correct the calibration** — `/outcome` said to append a superseding row, `/setup` counted both. **Applied** — a correction row's `notes` begins `supersedes <recorded_on> <finding_slug>`, `/setup` excludes the named row from the counts, and the rule in `frameworks.md` says so.
- **The rule is too blunt — one rejection is −25 for a whole finding type across every future client.** **Disagreed, with the reviewer's point recorded.** `TASK.md`'s gate is "a recorded rejection must visibly change the next ranking": one rejection *has* to move the order, or the loop is decorative. The rule is deliberately fast-learning and averages down as rows accumulate (two rows, one each way, is 0); the human confirms the table every time `/setup` proposes it, with the row count beside each adjustment, so a one-row adjustment is visible as one row; and it moves fixability only, never the evidence. If the practice finds it too blunt after real engagements, the rule is one line in a tracked file. The reviewer is right that it encodes one client's politics as a type-wide prior; that is what a practice's memory is, and the confirmation step is where a human says "not this time".

Confirmed right by the reviewer: single-writer language across all three commands; per-row confirmation with skip and no both writing nothing and "write all" forbidden; the taxonomy enforced at both ends; calibration applied to fixability only, clamped, with raw and calibrated values recorded.

## Decisions made
- **The loop closes through fixability, by finding type.** A rejection says something about how *actionable* a kind of recommendation is in practice, not about its size or its evidence; so the calibration moves fixability, and only by type, never by client.
- **The rule lives in `frameworks.md`, not in a command.** `/setup` reads it from the file and shows the arithmetic; `/rank` applies whatever the table says. Changing the rule is an edit to the tracked profile, reviewable in a diff.
- **One rejection moves the order by design** — 25 points of fixability at a 30% weight is 7.5 score points, more than the gaps between the top findings. The practice learns fast and forgets slowly; the human sees the table before it takes effect.
- **`/outcome` accepts pre-supplied answers in a fresh run** the same way `/scope` did in phase 1: the human's answers are scripted into the prompt, the command asks and applies them, and the report restates which answer went where.

## Blocked or deferred
- **`--all` skips investigated findings**, so the rejected finding itself (`meta-cac-doubled`) is never re-ranked; the calibration shows up on the *next* finding of its type. That is the intended semantics of a practice memory, but it means the gate's evidence is one step removed from the rejection. If the owner would rather see the rejected finding itself sink, `--all` should include investigated findings and mark them.
- **The calibration rule's bluntness** is a live disagreement with the reviewer (above). One tracked line to change; needs real engagements to decide.
- **Session limits** killed the first "before" `/rank` at launch; it was restarted from nothing. Every other phase-5 run completed in one go.

## For the next phase
- The pipeline has been run end to end on Acme, stage by stage, each stage reading only the previous stage's output; `RUN_REPORT.md`'s engagement section is the deliverable.
- `practice/tracker.csv` holds two rows and is gitignored; `practice/frameworks.md` holds the calibrated table and is committed as the practice's state.
- What phase 6 should be is in `BUILD_PLAN.md` §7; the real-case `/review` raised the one design question worth taking first — whether `recoverable_at_most` should be recorded as a margin movement (denominator moves too) as well as rupees over the current denominator.
