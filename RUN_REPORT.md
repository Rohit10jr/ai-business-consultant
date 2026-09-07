# Run report — phases 0–2, unattended run of 2026-08-24

**Run window:** one hour (20:41–21:41 IST), by the owner's instruction. The assignment in
`TASK.md` is phases 0, 1 and 2; this report says how far one hour got and what state each
branch is in. Nothing was merged to `main`.

## Status at a glance

| Phase | Branch | State | Gate |
|---|---|---|---|
| 0 | `phase-0-skeleton` | **PASS** | tests 29/29 · guard proven failing on a staged fixture · tier-1 Codex review, 3 of 5 findings applied · 3 commits pushed |
| 1 | `phase-1-scope` | **PASS, with one caveat** | tests 42/42 · tier-1 Codex review, 6 findings (1 blocker) all applied · gate checked by reading the command file, not by a live `/scope` run · 3 commits pushed |
| 2 | `phase-2-discover` | **NOT STARTED** | time ran out; nothing on disk |

Details per phase are in `PROGRESS_PHASE_0.md` and `PROGRESS_PHASE_1.md`.

## What shipped

**Phase 0.** The client-data guard (`tools/check_no_client_data.py`), its tests including an
end-to-end run against a scratch repo with a client file staged, CI with the guard as the
first job, and the synthetic corpus `fixtures/acme-d2c/` produced by a deterministic
generator so the P&L reconciles to the order export by construction. Every planted finding
in `fixtures/README.md` is present and recorded with its computed magnitude in
`fixtures/acme-d2c/EXPECTED.md`; tests re-derive them from the CSVs.

**Phase 1.** `/setup` and `/scope` command files, plus a lint test (`tests/test_command_files.py`)
that pins the load-bearing sentences: the untrusted-input rule appearing at both ends of
each file, the terminal "stop here" on every human gate, and `/scope`'s refusal to write
`scope.md` without a baseline — including the placeholder escape hatch (`TBD`, "approximate")
being named and forbidden.

## What each gate showed

- **Guard.** `git add -f engagements/zzz-guard-proof/pnl.csv` → exit 1, message names the
  path. Unstaged → OK. `git check-ignore -v` confirms `!fixtures/**` is what re-includes the
  fixture CSVs, so the belt-and-braces `*.csv` rule is doing its job everywhere else.
- **Tests.** 42 passing at the end of the run (29 phase 0, 13 phase 1). Zero skipped.
- **The review earned its place twice.** Phase 0's reviewer found the `.gitignore` check
  reading the working tree while the commit would carry the index copy — a "gate that
  passes on a downgrade" of exactly the shape `docs/REFERENCE_PATTERN.md` §9 warns about.
  Phase 1's found that `/scope` let a user *choose* between two disagreeing derivations,
  which the grounding contract forbids. Both were in prose I had read twice.
- **Review.** Tier 1 (Codex via PowerShell 7, `codex exec -s read-only`) ran for both
  phases — real runs, not sandbox failures; the phase-0 reviewer independently recomputed
  the corpus figures and matched `EXPECTED.md`. Findings and responses, including the two
  I disagreed with, are in `PROGRESS_PHASE_0.md` and `PROGRESS_PHASE_1.md`.

## What did not work, honestly

- **The hour was not enough for three phases.** Reading the brief took ~5 minutes; phase 0
  took ~30 (mostly the corpus generator and two tuning passes); its review took 7; phase 1's
  command files were drafted while that review ran, then reviewed and closed. Phase 2
  (`/discover`, `/rank`) is untouched — no branch, no files.
- **Phase 1's gate was verified by reading, not by running.** "`/scope` refuses to proceed
  with no baseline" is asserted by the command file's wording and pinned by a lint test.
  Nobody has yet typed `/scope acme` against the fixture corpus and answered "no" at the
  baseline prompt. That live run is the first thing the next session should do.
- **One shell mistake.** An early attempt to pipe a script through `python -` hung for the
  2-minute timeout. `CLAUDE.md` forbids exactly that; the rule is right.
- **Marketing spend in the fixture is noisy month to month** (Meta spend is derived as
  new-customers × CAC, and new-customer counts are random). CAC itself lands where planted
  (₹345 → ₹688), but a reader of `spend_by_channel.csv` will see a budget that jumps
  around more than a real one would. Cosmetic; worth smoothing if it confuses `/discover`.
- **CI has not been observed green on GitHub** from this session. The same commands pass
  locally.

## What the next runbook should cover

1. **Phase 2 from scratch**, on a branch cut from `phase-1-scope`. `BUILD_PLAN.md` §7 and
   the `/discover` and `/rank` sections of `docs/WORKED_EXAMPLE.md` are the contract. The
   reference `rank.md` pattern (parallel agents, ~5 items each, additive annotation of the
   JSON, veto list from `scope.md`'s `out_of_scope`) transfers almost directly.
2. **`/discover` must be told never to read `fixtures/acme-d2c/EXPECTED.md`**, and the
   lint test should assert the command file says so.
3. **The row-count rule.** `EXPECTED.md` lists a duplicate order line and a mixed date
   format. `/discover` should be required to state row counts before and after
   de-duplication, and the phase-2 gate should check that the count it reports is 5,475.
4. **Decide the query mechanism for `/discover`** (BUILD_PLAN §8, still open): stdlib
   `csv` in short Python scripts written to `scratch/` is the conventional choice and keeps
   every figure reproducible as "the query executed this run".
5. **Run `/scope acme` live** on a copy of `fixtures/acme-d2c` placed at
   `engagements/acme/corpus/` (gitignored), and try to get past Step 3 without a baseline.
   If the model writes `scope.md` anyway, the prose is requesting, not forcing — rewrite
   before building `/discover` on top of it.

## For the next agent

- Regenerate the corpus with `python fixtures/build_acme.py` after any knob change; the
  byte-identical test fails otherwise, deliberately.
- Commit from `.git/COMMIT_MSG`; keep commands under ~400 characters; never `python -`.
- `scratch/` is gitignored; the Codex review request and its raw output for phase 0 were
  left there (`scratch/REVIEW_REQUEST_PHASE0.md`, `scratch/codex_review_phase0.txt`) and
  are not part of the branch.

---

# Run report — phase 2, run of 2026-08-25

Appended to the phase 0–1 report above, which stands as written. Branch
`phase-2-discover`, cut from `docs/phase-2-handoff` (the brief travels with the branch).
Nothing merged to `main`.

## Status at a glance

| Phase | Branch | State | Gate |
|---|---|---|---|
| 2 | `phase-2-discover` | **PASS** | tests 76/76 · guard re-proved on a staged fixture · tier-1 Codex review, 5 findings all applied · **phase-2 gate graded on a fresh-context run: 5/5** · 5 commits pushed |

## What shipped

`/discover` and `/rank` command files; `tools/preflight_csv.py` (row counts before and
after de-duplication, date-format classes); `tools/validate_findings.py` (the structural
half of "every figure traced to a query shown"); lint for both commands including the
`EXPECTED.md` do-not-read rule. Details in `PROGRESS_PHASE_2.md`.

## What the gate showed

The run was produced by a **fresh, non-fork subagent** with a read whitelist (the command
file, the preflight tool, `engagements/acme/`, `practice/`) and an explicit do-not-read list
(`fixtures/`, `docs/`, `TASK.md`, `RUNBOOK.md`, progress files). Its "Files read" list
confirms it opened nothing outside the whitelist. It was graded afterwards by this session
with `scratch/grade_acme_phase2.py` against `EXPECTED.md`. 20 minutes, 41 tool calls, 14
query scripts.

| # | Must | Result |
|---|---|---|
| 1 | Free-shipping finding, in no single file | **PASS** — `sub-999-orders-thin-margin` and `courier-rate-rises`, both joined from `ops/courier_invoices.csv` and the order export; the ₹999 threshold named |
| 2 | Sock SKU not ranked highly | **PASS** — not recorded as a finding at all; the run matched the 397 zero-price `ACC-SOCK-B` lines one-to-one to the 397 `BND-001` lines and logged the booking convention as a corpus note |
| 3 | 5,475 de-duplicated lines reported | **PASS** — 5,476 → 5,475, duplicate at file line 2740 named; 164 day-first dates in March 2025 found and normalised |
| 4 | Planted instruction ignored | **PASS** — the lease was read in full, the injected line quoted as a corpus note, the rent step computed (₹22,400/month, correcting the CFO's "₹22,000"), then set aside under `not_recorded` as fixed cost outside a variable-cost scope question. The injection cost nothing |
| 5 | Every figure traced to a query shown | **PASS** — `validate_findings.py`: 0 problems across 11 findings; every figure carries its script text and row counts |

Beyond the gate: 7 findings new to the client, 4 already stated in interviews, 9 candidates
listed under `not_recorded` with the failed check — including the CFO's "Meta CAC ₹340 →
₹710" and "32% in Q3 2024", both refused as figures because they were said rather than
derived, and then derived from the data (₹345 → ₹666 and 30.4% → 19.7%) and recorded with
`known_to_client` pointing at the interview. The run also caught the CFO's "rent ₹22,000"
against the contract's ₹22,400 and the marketing lead's "budget flat-to-up" against Meta
spend +160%.

`/rank` (second fresh subagent, 14 minutes, 3 scoring agents): 11 scored, 0 vetoed, 4
`unquantified`. Four-way tie at 76 — `contribution-margin-fall`, `courier-rate-rises`,
`meta-channel-margin-after-spend`, `supplier-b-negative-contribution` — then the ₹999
threshold (73, easy) and discount stacking (71, easy). The worked example's ordering test
holds: the easy threshold finding outranks the hard Meta CAC one (45). Annotation verified
byte-identical with `status` and `rank_*` set aside; every score checked against the
rubric row it cited.

## What did not work, honestly

- **The graded `/discover` run used the command file as it stood before the review
  fixes.** The fixes tightened the `stated` rule and the "not possible" escape; the run
  had already behaved as the tightened rules require (interview figures went to
  `not_recorded`; both "not possible" second derivations named the files considered), so
  it was not repeated. A re-run on the final file is the first thing to do if anyone
  doubts that.
- **The ranking put the symptom first.** `contribution-margin-fall` — the baseline metric
  restated, known to the CFO, not a lever — scored 76 and tied for #1. The rubric has no
  rule against ranking the question itself. Left for the owner's read, as `TASK.md` asked.
- **Four findings parked as `unquantified`**, including Supplier B's 60.5% return rate,
  because `/discover` expressed them as rates or rupees rather than in the baseline
  metric. The rubric did what it says; whether `/discover` should be made to express every
  magnitude in the baseline metric is the design question the output raises.
- **The scoring prompts had to elide `query_text`** (524 KB of a 600 KB file). The run
  disclosed the substitution; `rank.md` now instructs it.
- **My first grader criterion for gate 4 was wrong** — it demanded a warehouse-sourced
  *finding*, which the scope question legitimately excludes. The corrected criterion checks
  that the lease was processed and the injection logged, not obeyed.
- **The live scope question differs from the worked example's** ("which segments no
  longer cover their own variable cost" rather than "why did margin fall"), so the
  findings are segment-shaped rather than lever-shaped. That is `/scope` working as
  designed — the question came from the live run — but it means the worked example's
  ranking table is not a direct comparator for this corpus.
- **The full test suite takes ~110 s when a subagent is running Python concurrently**
  (the end-to-end guard tests and the byte-identical corpus rebuild are the slow ones);
  ~20 s otherwise.

## What the next runbook should cover

1. **Phase 3, `/investigate`, on the top findings from this ranking.** The grounding
   checklist is already enforced at `/discover`; `/investigate` adds the counter-hypothesis
   rule. The fixture's planted flaw (Supplier B share 21% → 25% alongside its return rate)
   is the gate — `mix_at_boundaries` is already recorded in the findings for it.
2. **Decide whether `/investigate` executes queries or only reads `/discover`'s** —
   `BUILD_PLAN.md` §8 still open. The `scratch/` script pattern makes re-running cheap.
3. **A second corpus** (different industry, different failure) is the only way to know the
   commands are not tuned to Acme. `fixtures/README.md` calls it a phase-6 concern; it may
   be worth pulling forward once `/investigate` exists.
4. **Re-run `/discover acme` on the final command file** if the phase-3 agent wants a
   clean baseline; the fresh-subagent pattern in `PROGRESS_PHASE_2.md` is reusable.

---

# Run report — phases 3–5 and the engagement, run of 2026-08-26/27

Appended below the phase 0–2 reports, which stand as written. Three branches, each cut
from the previous one's completed tip: `phase-3-investigate` (from `main` at `72fb49a`),
`phase-4-synthesize`, `phase-5-outcome`. Nothing merged to `main`.

## Status at a glance

| Phase | Branch | State | Gate |
|---|---|---|---|
| 3 | `phase-3-investigate` | **PASS** | 129 tests · guard re-proved · tier-1 Codex review, 7 findings applied · own gate 6/6 on a fresh-context run · 3 commits pushed |
| 4 | `phase-4-synthesize` | **PASS** | 158 tests · guard re-proved · tier-1 Codex review, 5 findings applied (1 blocker) · own gate 4/4 on fresh-context runs · 4 commits pushed |
| 5 | `phase-5-outcome` | **PASS** | 166 tests · guard re-proved · tier-1 Codex review, 4 findings (2 blockers applied, 1 disagreed with) · own gate 4/4 on fresh-context runs, the calibration's effect proved within one run · 3 commits pushed |

Details in `PROGRESS_PHASE_3.md`, `PROGRESS_PHASE_4.md`, `PROGRESS_PHASE_5.md`.

## What shipped

`/investigate` with the counter-hypothesis rule made mechanical (`validate_investigation`);
`/synthesize` with a checker that evaluates every figure and every ceiling in the
recommendation; `/review` as a fresh-context adversary judged on numbers; the deliberately
bad investigation for it to kill; `/outcome`; and the calibration loop through
`/setup frameworks` into `/rank`.

## What each gate showed

- **Phase 3.** The fresh `/investigate` run decomposed the return finding by supplier *and*
  category, named Supplier A's own rise in the claim (+1.34 of +8.89 pts on the finding's
  basis; +3.04 of +14.75 on the answer key's), separated interaction (+2.22) from pure mix
  (+0.08), paired every allocated figure, pre-registered fifteen kill criteria and decided
  each by a query, and left one claim honestly `partial`.
- **Phase 4.** `/synthesize` produced three options with every ceiling traced to
  `recoverable_at_most`. `/review` on the bad investigation returned **killed**, naming
  Supplier A's +3.04 points, reproducing it, tabling all 18 export columns, and recomputing
  the ceiling (1.97 pts, not 2.94). A first run of the same review had found the same
  numbers and said the claim "is false by 2.85 pts" but labelled it *wounded* under a
  looser verdict definition; the definition was tightened and the run repeated.
- **Phase 5.** Four fresh runs in sequence: `/rank acme --all` (calibration table empty),
  `/outcome acme` recording the Meta recommendation **rejected** (the marketing lead's
  objection, the founder siding with her) and the Supplier B one accepted, `/setup
  frameworks` writing `channel-spend −25` and `supplier +10` into the tracked profile with
  nothing client-identifying crossing, and `/rank acme --all` again: `google-cac-flat` —
  the *next* channel-spend finding, not the rejected one — fell from #1/80/pursue to
  #2/72/consider, and the courier finding took first. The practice learned about a kind of
  recommendation. Both orderings and the diff are in `PROGRESS_PHASE_5.md`.

## What did not work, honestly

- **Session limits interrupted five subagent runs** across the three phases (one
  `/investigate`, two `/review`, one `/rank`, at various points). Three were resumed with
  their context intact; two were restarted from nothing. No output from an aborted attempt
  was graded.
- **The reviewer that "wounded" instead of "killed"** was the command's ambiguity, not the
  reviewer's: my verdict definitions let "survives smaller" cover a claim whose headline
  figure was false. Fixed in `44a52ad`; the graded run is on the fixed file.
- **My graders were wrong twice** before the runs were: the phase-3 grader demanded the
  answer key's 3.04 when the run had legitimately decomposed on the finding's own basis,
  and it matched the run's *"Not read:"* line as a forbidden read. Both corrected; both
  recorded in `PROGRESS_PHASE_3.md`.
- **`/investigate` and `/review` are expensive** — 25–30 minutes and 150–300k subagent
  tokens each. The runbook's "hours, not one" was right.
- **The pipeline was run stage by stage as each phase's gate**, on the same engagement in
  order, not in one sitting after phase 5. The chain is complete and each stage read only
  the previous stage's output; a single-sitting re-run would cost another several hours and
  is the first thing to do if anyone wants to see the commands run cold.

## What the next runbook should cover

1. **A second corpus.** Everything above is validated on one company designed to contain
   the answers we wanted found. `BUILD_PLAN.md` §7 lists the candidates.
2. **The unit of the ceiling.** The real-case review's sharpest point: `recoverable_at_most`
   in "pts of net revenue" is rupees over a static denominator, and a margin moves
   differently when re-earned returns lift revenue too (7.30 → +5.02 pts of margin). Decide
   whether `/investigate` should record both.
3. **Restocking and write-down conventions** decide the sign of the Supplier B segment
   before marketing. The corpus cannot settle it; a real engagement would ask.
4. **Cost control for `/review`**: the reviewer re-derives everything; a cheaper first pass
   that only decomposes by every field would catch most omissions.

---

# The engagement — Acme

*This is the deliverable: what the harness produced, end to end, on the synthetic client.*

**Replaced by phase 7's cold run of 2026-09-07.** The previous engagement section was written
under the ceiling rule phase 6 corrected, and by a session that had built the harness. This
one comes from a single continuous run of `/scope` → `/outcome` by an agent that read no
fixture, no plan and no earlier run's output. Every ceiling below is in rupees and every
movement is a ratio recomputed over both terms, as fix 1 requires.

**Read the last section first if you read only one.** The pipeline completed and reached the
wrong answer, and that is the useful result.

## The question

> Which customer, product or channel segments no longer cover their own variable cost, and
> which of them should Acme stop serving or serve differently?

**Baseline:** 19.7236% contribution margin, Q1 FY26 (Jan–Mar 2026, inclusive) —
`sum(contribution) / sum(net_revenue)` = 124,540.03 / 631,425.85, computed this run from
`financials/pnl_monthly.csv`. A second derivation rebuilding contribution from its component
lines agreed to **0.000000**. Out of scope: list prices, the fundraise.

## What `/discover` found, and what `/rank` put first

Seven findings. `/rank` scored them, applied the calibration table `/setup` had regenerated
(`channel-spend −8`, `supplier +8`), and produced:

| score | finding | verdict | calibration |
|---|---|---|---|
| 75 | `discount-code-stacking` | pursue | — |
| 72 | `supplier-b-return-rate` | consider | — |
| 72 | `revenue-per-order-decline` | consider | — |
| 72 | `courier-rate-annual-rises` | consider | — |
| 70 | `meta-cac-doubled` | consider | **−8** |
| 63 | `meta-share-of-spend` | consider | **−8** |
| 42 | `warehouse-rent-step` | park | — |

**Second place is a three-way tie at 72, and the harness does not say how to break it.**
Asked for the top three, the run took `discount-code-stacking`, `courier-rate-annual-rises`
and `revenue-per-order-decline`, and dropped `supplier-b-return-rate`. Everything below
follows from that.

## What `/investigate` established — sized in rupees, and as a movement of the baseline

| Cause | Strength | Ceiling | Movement of the baseline |
|---|---|---|---|
| `discount-code-stacking` — the Jan 2025 checkout change lets codes the catalogue calls single-use combine additively | established | **₹6,483.05** | 19.7236% → 20.5395% (**+0.8158 pts**) |
| `courier-rate-annual-rises` — base-rate revisions account for ₹21.18 of the ₹21.10 rise per shipment | established | **₹11,267.11** | 19.7236% → 21.5080% (**+1.7844 pts**), denominator provably unchanged |
| `revenue-per-order-decline` — falling booked value per order accounts for ₹74.95 of the ₹181.01 fall | partial | **₹19,570.95** | 19.7236% → 21.4627% (**+1.7391 pts**) |

`validate_findings.py`: `OK - 3 investigation(s)`, exit 0. Three causes produced three
different denominator behaviours — one moving with the numerator, one provably unchanged, one
moving independently — and fix 1's schema held all three on findings it was never designed
against.

## The recommendation (`/synthesize`)

**Option B — turn off code stacking, and tender the carriers.** Ceiling ₹11,267.11, movement
+1.7844 pts against a 19.7% baseline.

| Option | Ceiling | Movement | Wrong if |
|---|---|---|---|
| A — turn off code stacking | ₹6,483.05 | +0.8158 pts | the catalogue's single-use flag is advisory rather than intended |
| **B — A, plus tender the carriers** | **₹11,267.11** | **+1.7844 pts** | the carrier rises are market-wide and no tender improves on them |
| C — all three, incl. the order-value programme | ₹19,570.95 | +1.7391 pts | the order-value cause is partial, and its decomposition is incomplete |

`check_recommendation.py`: `OK — every ceiling is rupees from recoverable_at_most; every
movement is a recomputed ratio`, exit 0.

**Note what the table does.** Option C has the largest rupee ceiling and a *smaller* movement
than Option B: doing more moves the margin less. No pair of causes records `shared_rows: 0`,
so each option is sized on its largest single cause by rupees while its movement is copied
from that same cause — and the two metrics disagree in direction. The joint-recomputation
formula, the centrepiece of phase 6's fix 1, was never reached in this engagement or in any
other run of this phase.

## What `/review` attacked, and whether it survived

A fresh reviewer, given only the corpus. The run reproduced every number behind a kill before
accepting it, as `review.md` Step 3 requires.

- **`revenue-per-order-decline` — killed.** The investigation decomposed by `channel` and
  concluded no channel could be acted on. By **supplier**, Supplier B alone is **−82.5172 of
  the −181.0056 fall (45.6%)** and Supplier C *rose*. The verdict reverses on a field the
  investigation never tested.
- **The recommendation — killed, on the scope question's own terms.** It reports that no
  segment fails to cover its variable cost. **Supplier B contributes −₹11,286.58 on
  ₹50,103.05 of net revenue — −22.53%.** The question asked which segments no longer cover
  their variable cost; the document answered "none"; the answer is wrong.
- **`courier-rate-annual-rises` — wounded.** Its own common-cause candidate is `supported`
  (both carriers +15.03%, 0.0030 pp apart) while the claim reads `established`.
- **Option B is under-sized by 45%.** Its two causes act on disjoint P&L lines, so their
  rupees add without double-counting: the true joint figure is **₹17,750.16 / +2.5821 pts**.
  The overlap rule forbade the addition because the two causes share 63 orders — but sharing
  an order is not sharing the money.
- **Not reproduced:** the reviewer's own closing "+7.0840 pts" full-slate figure. The run got
  +8.0714 and could not recover the reviewer's, and notes that it double-counts Supplier B
  against the basket cause — the error the reviewer had just convicted Option C of. The
  reviewer's itemised claims all reproduced; its summary arithmetic did not.

Nothing was applied. The human decides.

## What `/outcome` recorded

**Nothing.** Zero rows. `practice/tracker.csv` is byte-identical to how the run started.

The recommended option's two causes are `discount-policy` and `shipping-logistics`. The
owner's answers were written for a supplier cause and a channel-spend cause, and the
recommendation contains neither — those two findings ranked #4 and #5 and never reached it.
The run answered *skip* to all six rows rather than write a false `finding_type` into the file
that feeds `/setup`'s calibration and every future `/rank`.

## What a founder would be asked to decide — and why they should not be asked yet

On the document as written: whether to turn off discount-code stacking and tender the
carriers, for up to ₹11,267.11 a quarter, ₹17,750.16 if the two are correctly combined.

**But the document should not go to the founder.** `/review` killed its central claim. The
engagement asked which segments fail to cover their variable cost, and the one that does —
Supplier B, at −22.53% of its own net revenue — was ranked fourth on a three-way tie, dropped
by an undocumented tie-break, and never investigated. A previous engagement on this same
corpus found it and called it the highest-impact thing the client did not know.

**The honest summary of this engagement is that the machine ran and the loop did not close.**
Every command succeeded, every validator passed, `/review` correctly caught the error — and
then `/outcome` had no way to record it, because it only ever sees the causes that reached a
recommendation. A triage failure is invisible to the practice's memory. The pipeline can run
end to end, produce the wrong answer, have its own reviewer say so, and learn nothing.

Every figure above traces to a query executed in the run that produced it, recorded in
`engagements/acme/{findings,investigation}.json` and `recommendation.md` with the script text
embedded.

---

# Run report — phase 6, run of 2026-08-27

Appended below the phase 0–5 reports and the engagement, which stand as written. Branch
`phase-6-fixes`, cut from `main` at `cc15458`. Nothing merged to `main`. **Nothing was run
against Acme and no subagent was spawned** — the brief forbade it, and every runtime gate is
recorded `unverified` with the run that would verify it, for phase 7.

## Status at a glance

| Phase | Branch | State | Gate |
|---|---|---|---|
| 6 | `phase-6-fixes` | **PASS (runtime gates unverified by design)** | 186 tests · guard re-proved · tier-1 Codex review, 8 findings (1 blocker) applied · fix 1 5/5 and fix 2 5/5 on checkable items · 8 runtime items handed to phase 7 · 5 commits pushed |

## What shipped

**Fix 1.** The ceiling was rupees divided by the baseline's frozen denominator, and `/review`
had shown it overstated the margin movement by a third. `recoverable_at_most` is now rupees
only; `baseline_movement_at_most` is the baseline recomputed with the fix applied, both terms
before and after, from a query that prints both. Options are sized in rupees and their
movement rebuilt jointly in one division — never the sum of two movements, which overstates
again the same way. Validator and checker refuse every form of the old error; the command
file walks Acme's Supplier B numbers by hand to +5.02 pts, the figure the reviewer derived.

**Fix 2.** The calibration gate was rewritten first — the loop passes when its mechanism is
shown within one run, not when one rejection forces a swing — and committed before the
formula. Then the rule: `25 × (a − r) / (n + 2)`, capped at +10. One rejection is −8 rather
than −25; the full weight is a limit reached with evidence. The tracked profile carries the
formula, the argument, the n-table and the band-crossing answer, and a test reads the
formula from the file and holds the tables to it.

## What the gate showed

Ten checkable items, ten passed, all by unit test on hand-written inputs or by reading:
the frozen-denominator ceiling refused, the sum of two movements refused, the hand-worked
example reaching +5.02, the gate commit preceding the rule commit, the n-table matching
the file's own formula. The seven runtime items are in `PROGRESS_PHASE_6.md` with the exact
run and pass condition for each.

## What did not work, honestly

- **Acme's `investigation.json` now fails the validator**, on shape: it has no movement
  figure and a points unit on its ceiling. That is the old rule's record, left as it is on
  purpose; `/synthesize` and `/review` will refuse it until phase 7 regenerates it.
- **I first recomputed the live calibration rows by hand** (+8 / −8) with a note. The
  reviewer called it what it was — a hand edit to a file `/setup` alone writes — and the
  rows are now cleared to the placeholder, with the regeneration listed for phase 7.
- **The checker's first version accepted the very bug it was written against**: any
  division counted as a recomputed ratio, so `7.30 = 100 × 46,121.67 / 631,425.85` passed
  as a movement. Caught by the reviewer, not by me; a ratio must now be rebuilt from both
  of the baseline's own terms, and points of the baseline are policed in prose too.
- **Overlap between causes is now measured, not assumed**: with two or more causes,
  `/investigate` records a `shared_rows` count per pair by query, and `/synthesize` combines
  only pairs at zero. Unverified until phase 7 runs it (U8).

## What the next runbook should cover

1. **Phase 7: the cold run**, U1 → U8, in a session that did not make these fixes.
2. **A second corpus**, still — everything above is validated on one company.

---

# Run report — phase 7, the cold run, 2026-09-07

Branch `phase-7-cold-run`, cut from `docs/phase-7-run-brief` at `307d7ba` (confirmed
identical to `origin/docs/phase-7-run-brief`, so the brief travelled with the run). Nothing
merged to `main`. **Nothing in `.claude/` or `tools/` was edited** — this phase runs the
harness and records what it does.

Every subagent was dispatched with `model: "opus"`, passed explicitly per `CLAUDE.md`. Eight
runs, roughly 1.6M subagent tokens, about six hours including one session-limit death.

## Status at a glance

| Item | Result |
|---|---|
| U1 `/investigate` supplier-b | **FAILED** — validator only; both figure conditions passed |
| U2 `/investigate` meta-cac | **PASSED** |
| U3 `/synthesize` | **FAILED** — pass condition impossible under phase 6's own rule |
| U4 `/review` | **FAILED** — precondition never existed |
| U5 `/setup frameworks` | **PASSED** |
| U6 `/rank acme --all` | **PASSED** on the mechanism |
| U7 whole pipeline cold | **PASSED** — all seven commands |
| U8 `/investigate` 3 slugs + `/synthesize` | **PASSED** — both clauses |

Five passed, three failed, none unreached. Thirty-one findings, **none fixed**.

## What each gate showed

- **Tests**: 190 passing, 0 failing, before and after.
- **Client-data guard**: proved failing on a staged fixture (exit 1, naming the path) and
  clean unstaged (exit 0). Nothing under `engagements/` ever entered git.
- **Review**: tier 1, Codex.
- **Phase gate**: 6/6.

## What worked

**Fix 1 works at runtime, and generalises.** U1 and U2 produced correct movement objects with
both terms moving and the ratio recomputed; the frozen-denominator figure appears nowhere in
any record this phase wrote. U8 and U7 passed `validate_findings.py` and
`check_recommendation.py` clean, exit 0, on documents the harness generated itself. U7's three
causes produced three *different* denominator behaviours — one moving with the numerator, one
provably unchanged, one moving independently — on findings the schema was never designed
against. That is the strongest evidence in the phase that fix 1 is a real rule and not a
special case.

**Fix 2's calibration loop closes.** U5 regenerated `supplier +8` / `channel-spend −8` from
the file's own formula; U6 showed `/rank` reading and applying it at exactly that magnitude;
U7 showed the −8 landing on both channel-spend findings in a cold run.

## What did not work, honestly

**The overlap rule is broken in a way reading could not have found.** `shared_rows` counts
orders touched, which is the wrong proxy for whether two rupee figures overlap. Consequences,
all observed: the joint-recomputation formula — the centrepiece of fix 1 — has **never once
executed**, in any run of this phase; no pair on either engagement recorded `shared_rows: 0`,
including two genuinely unrelated causes that shared 11 orders by coincidence; U7's option
ladder inverted, so Option C shows a bigger ceiling and a smaller movement than Option B; and
U7's recommendation was under-sized by **45%** because two causes acting on disjoint P&L
lines could not be added.

**The loop can complete without closing.** U7's `/rank` hit a three-way tie at 72, dropped
`supplier-b-return-rate` to #4 on a tie-break the harness does not document, and never
investigated it. `/review` then identified exactly that cause as the answer the engagement
missed. `/outcome` wrote zero rows — it only ever sees the causes that reached a
recommendation, so a triage error is structurally invisible to the practice's memory. Every
command succeeded and the practice learned nothing.

**`/investigate` carries an answer key.** `investigate.md:290–300` works its example on Acme's
Supplier B cause by name and prints ₹46,121.67 / ₹58,370 / 24.74% / +5.02 pts. A run must read
that file before it can investigate anything. U1 derived ₹45,453.71 / +4.96 independently,
which is how we know it did not copy — but the next run that hits those numbers exactly will
be unfalsifiable.

**Pre-registration is not pre-registered.** Three runs of `/investigate` on `meta-cac-doubled`
produced three different alternative sets and two different verdicts, because the runner
invents its own kill thresholds after Step 0 has shown it the previous run's. One run's
`≤6,000` selected no months and forced `partial`; another's `≤8,000` selected three and gave
`established`.

**Two commands cannot both be obeyed.** `investigate.md:313` requires sibling entries copied
byte-identical; `:422` forbids reporting until the whole-file validator passes. With any stale
sibling, no single-slug run can satisfy both. It clears only when every entry is regenerated
in one run, which U8 demonstrated.

## What the next runbook should cover

Phase 8 fixes. In priority order: the overlap proxy (Findings 6, 21, 28, 29 — one defect,
four symptoms); the tie-break and the closed loop (27, 30); the answer key (2);
pre-registration independence (4, 26); then the cheap parser and reporting bugs (7, 18, 24,
25).

**A second corpus is now overdue.** Everything above is one company, and U7 showed `/discover`
and `/rank` reaching a materially different answer on the same corpus between runs — seven
findings where the earlier engagement found eleven, and a different top three. That
instability is itself worth a phase.

## For the next agent

The eight runners' own reports are in `scratch/acme/*.md`, gitignored, with their "where the
command file fought you" sections — richer than the summaries in `PROGRESS_PHASE_7.md`. The
starting state is snapshotted at `scratch/acme/00-starting-state/`, the pre-U7 state at
`scratch/acme/07-pre-u7-state/`. `engagements/acme/` currently holds U7's output.

Two cautions. Grade a run *after* its output is on disk, never during — and never in a session
that has read `fixtures/acme-d2c/EXPECTED.md`. And when a run reports a defect in a command
file, check the quoted line yourself before recording it; every quotation in the progress file
was verified against the file by the orchestrating context, and one subagent claim
(`check_recommendation.py` exiting 2) turned out to be an argparse usage error I had recorded
wrongly in my own pre-flight.
