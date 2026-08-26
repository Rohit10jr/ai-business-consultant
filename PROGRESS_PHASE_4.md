# Phase 4 — <STATUS>   [branch: phase-4-synthesize]

## What shipped
- `.claude/commands/synthesize.md`: `/synthesize <client>` — refuses an `investigation.json` the validator rejects; tabulates every established/partial cause with its ceiling; builds two or three options that trade different things (one of them do-less), each sized as the written-out sum of its causes' `recoverable_at_most` and nothing more; a `partial` cause is "up to" with its alternative named, an `unsupported` cause is not an option; costs are never invented; out-of-scope levers never appear; a per-stakeholder section addresses each interviewee's stated concern with no new figures; an Evidence table and an Arithmetic section close the document. Runs no queries: `tools/check_recommendation.py` is run on the draft and a figure it lists is removed, not softened. Single writer of `recommendation.md`.
- `.claude/commands/review.md`: `/review <client>` — Part 0 is the two mechanical checks run by the main context; then exactly one fresh `general-purpose` reviewer with the case pasted inline (query text elided — it must re-derive), a corpus-only whitelist, and the instruction that a finding is a number: re-derive every figure, decompose every rate by *every* field the corpus offers and name each material component the case does not, run the counter-hypotheses the case did not, recompute the ceiling from the named cause alone, check allocation pairs and scope, say what would make the recommendation wrong. Two-part output — structured edits, and findings by category with a killed / wounded / survives verdict per cause. The main context re-runs every query behind a kill or wound, discards a review whose read list contains `fixtures/`, drops edits whose `old` text does not exist, and applies nothing.
- `tools/check_recommendation.py` + tests: every figure-shaped number in `recommendation.md` must match a value in `investigation.json`, the baseline line, or a line of the `## Arithmetic` section whose every term is itself recorded.
- `fixtures/bad-investigation/`: `build.py` + four query scripts → `investigation.json`. Every figure true and produced by its embedded script (apparel returns 11.85% → 26.60%, Supplier B 20.9% → 25.0% share and 11.4% → 59.0% rate, the rise costing ₹19,880.79 a quarter = 2.94 pts of net revenue); decomposed by *category*, the lens that flatters the story; `counter_hypotheses: []`; Supplier A absent. `tests/test_bad_investigation.py` pins all of that and that the validator fails it on exactly the five omissions.
- `tests/test_command_files.py`: lint for both commands.

## Gate
| Check | Result |
|---|---|
| Tests | 158 passing, 0 skipped, 0 failing |
| Client-data guard | re-proved: `git add -f engagements/zzz-guard-proof/pnl.csv` → failure naming the path; unstaged → OK |
| Review | tier 1 — Codex (`codex exec -s read-only`, PS7), 176k tokens. See below |
| Phase gate | 4/4, graded on fresh-context runs |
| Commits | 4 (`030e526` commands + checker + fixture, `6a40a16` review fixes, `44a52ad` verdict definition, then this file) |

### Phase 4's own gate (RUNBOOK.md §5) — graded on fresh-context runs

All runs by fresh `general-purpose` subagents with the whitelist and do-not-read list, "Files read" appended and checked. Graded here with `scratch/grade_acme_phase4.py`.

| # | Must | Result |
|---|---|---|
| 1 | `/synthesize` gives one recommendation with 2–3 options, each tied to the baseline in its unit | **PASS.** `/synthesize acme` (15 min, 23 tool calls): three options — A *fix Supplier B's sizing, nothing else* (do-less, 7.3044 pts of Q1 FY26 contribution margin), B *fix Supplier B's sizing and hold Meta at its 2024 spend for one month* (recommended, up to 9.4483 pts = 7.3044 established + up to 2.1439 partial, the Meta alternative named), C *pull Supplier B's three SKUs now* (exit; ceiling stated as the segment's recorded loss, less than the cause). Every ceiling a `recoverable_at_most` value or written-out arithmetic over them; `check_recommendation.py` clean on the post-review checker; "wrong if" on every option names the open write-down convention with the alternative figure; read list inside the whitelist |
| 2 | `/investigate` run fresh separates mix from rate unprompted | **PASS** — phase 3's graded run: supplier and category tables, Supplier A's own rise named in the claim (+1.34 of +8.89 pts; +2.59 pts in the Supplier B entry's common-cause check) |
| 3 | `/review` fed `fixtures/bad-investigation/` kills it, naming Supplier A's 3.04 points | **PASS.** `/review acme-review-test` on the final command file (21 min, 31 tool calls; reviewer ~146k tokens): verdict **killed**. Verbatim: *"Decomposing the claim's own denominator (apparel ex BND-001) by supplier, Supplier B's own rate effect is 9.93 pts of the 14.75-pt rise the claim assigns to it; Supplier A's 3.04 pts and 1.82 pts of interaction are folded in, and the ceiling is 13,317.12 rupees / 1.97 pts of net revenue, not 19,880.79 / 2.94."* And: *"Supplier A's own rate effect is +3.04 points (12.0% → 15.8%, entirely first-order customers 5.2% → 16.7%) and appears nowhere in the investigation."* Every kill reproduced by the main context's own scripts; the Fields table covers all 18 columns of the export; Part 0 reported the five validator omissions separately; both read lists inside the whitelist. |
| 4 | Naming only "have you considered other factors?" is a fail | **PASS.** Both items named with numbers and queries; nothing generic. |

**The run before it.** The first fixture review (interrupted by a session limit after its reviewer had reported, then resumed) reached the same substance — *"'replacing Supplier B recovers the 14.75 pts' is false by 2.85 pts: Supplier A's own rate rose 12.0% to 15.8%, a rate effect of 3.04 pts (20.6%)"*, reproduced, ceiling recomputed to 2.36 pts, plus a catch the answer key does not list (bundle returns counted twice, 1.37 pts) — but labelled the cause **wounded**, because `review.md`'s definitions let "survives smaller" cover a claim whose headline figure was false. That was the command's ambiguity, fixed in `44a52ad` ("the verdict is on the claim as written"), and the review was repeated on the fixed file rather than graded on a definition that no longer exists. Its presentation is kept verbatim at `scratch/review_run_acme_review_test_run1.md`.

## Findings from review
Tier 1, Codex (`codex exec -s read-only`, PS7), ~12 minutes, 176k tokens — it reproduced the fixture's supplier decomposition independently (+3.04 / +9.93), confirmed Supplier A absent, the validator failing on exactly five omissions, and `build.py` byte-identical. Five findings, all applied:

- **Blocker — the checker trusted Arithmetic results without computing them.** `100 = 9.93 + 3.04` whitelisted 100; the reviewer confirmed `check()` returned `[]`. **Applied** — the right-hand side is evaluated (a stdlib `ast` walk over `+ − × ÷` and parentheses, unit words stripped) and the result must be what the terms make it, at the precision written.
- **Baseline date tokens became allowed figures** — the 26 in "FY26" let "26%" pass. **Applied** — only figure-shaped numbers are taken from the baseline line.
- **The checker validated presence, not role** — a finding's 14.75-pt magnitude could be used as an option ceiling because it exists in the record. **Applied** — every `- Ceiling:` line must be a `recoverable_at_most` value or an Arithmetic result whose every term is one.
- **A query-less kill had no failure path** in `/review` Step 3. **Applied** — a `kill`/`wound` with no query is set aside under "without a query" and the verdict is taken from the findings that carry one; "counter-hypotheses empty" is Part 0 and kills nothing on its own.
- **"EVERY field" was strong prose but not auditable.** **Applied** — the reviewer must table every column of the export as `decomposed` or `skipped — <reason>`, and the main context compares that table with the CSV header before accepting the review; a missing column means re-dispatch.

Confirmed right by the reviewer: the overwrite gate and no-chaining in `/synthesize`; fresh context, pasted content, whitelist and nothing-applied in `/review`; the reviewer blocked from reading the case from disk.

## Decisions made
- **`/synthesize` runs no queries.** Its value is judgement about options and sequencing; a synthesis that produces a number the investigation did not has invented one. The checker makes that mechanical, with an Arithmetic section as the only way to derive a figure and every term of it recorded.
- **Ceilings are ceilings.** An option is worth the sum of `recoverable_at_most` of the causes it acts on — never the finding's magnitude, never `/rank`'s impact, never the whole gap.
- **`/review` writes nothing and applies nothing**, per `BUILD_PLAN.md` §4 ("critique returned inline"). The run's output is saved by whoever ran it; the engagement record stays the human's.
- **Part 0 is the main context's job, and the reviewer is told not to repeat it.** The validator already knows the fixture's counter-hypothesis list is empty; a reviewer that reports that and stops has done nothing. The gate is what it finds beyond it.
- **The bad investigation decomposes by category.** The spec says every figure must be true; a supplier table would have been true too, and would have shown Supplier A. The flaw had to live in the choice of lens as well as in the empty list, because that is how it happens in practice.
- **The fixture is built, not hand-typed**, so its query texts match the scripts byte for byte and a reviewer cannot kill it on a transcription error.

## Blocked or deferred
- **Session limits interrupted both `/review` runs mid-flight** (the fixture run after its reviewer had reported; the real-case run at Part 0). Both were resumed with their context intact once the limit reset. The fixture run's first result is kept verbatim as `scratch/review_run_acme_review_test_run1.md` — see the gate table for why it was repeated on the final command file.
- **`/review` is expensive**: one run is a main context plus a reviewer that re-derives the whole case (~120k tokens for the reviewer alone on a one-finding fixture). Budget for it.

## For the next phase
- `engagements/acme/recommendation.md` exists: Option B recommended (fix Supplier B's sizing; hold Meta at 2024 spend for one month), up to 9.4483 pts of Q1 FY26 contribution margin. `/outcome` records against its three options.
- The real-case `/review acme` is a pipeline artifact, not a phase-4 gate item; its result goes in `RUN_REPORT.md`'s engagement section on phase 5's branch.
- `/outcome` must not touch `practice/frameworks.md`; `/setup frameworks` gains the tracker-reading path and its phase-1 deferral sentence is deleted. `/rank` needs a `finding_type` per finding (from a taxonomy in `frameworks.md`) and a calibration adjustment read from the same file for the loop to close.
- `tools/check_recommendation.py` and `validate_findings.py` are the two mechanical checks `/review` runs as Part 0; extend them, do not duplicate.
