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

## The question

> Which customer, product or channel segments no longer cover their own variable cost, and
> which of them should Acme stop serving or serve differently?

**Baseline:** 19.7% contribution margin, Q1 FY26 (Jan–Mar 2026, inclusive) — computed by
`/scope` from `financials/pnl_monthly.csv` three ways after refusing the 19% the brief and
the CFO both offered, because a round number said in conversation is not a source.
Out of scope: list prices, the fundraise.

## What `/discover` found, and what `/rank` put first

Eleven findings from twelve files and 5,475 de-duplicated order lines. `/rank` vetoed the
one that restated the baseline (the margin bridge — the question, not an answer) and put
first, by score: Meta cost per new customer doubled (80), the return rate doubled (79),
Google CAC flat while Meta's doubled (79), courier base rates +6% / +7% / +7.5% every
January (76), and — the highest-impact finding the client did **not** already know —
Supplier B's segment below its own variable cost (74).

## What `/investigate` established — sized in the baseline's unit

| Cause | Strength | What the data says | Ceiling |
|---|---|---|---|
| **Supplier B's three SKUs no longer cover their variable cost, because their size block changed** | established | Supplier B's own return rate 11.36% → 60.47% of its orders (Q3 2024 → Q1 FY26), 77% coded sizing, on all three SKUs; the segment went from ₹15,384 of contribution to −₹12,762 before marketing (−₹21,752 after). The client did not know this | 7.30 pts of Q1 FY26 net revenue (₹46,122) |
| The doubling of the return rate is the same cause, seen wider | established | Supplier B's own rise accounts for 5.66 of the 8.89 points; **Supplier A's own rise for 1.34**, the interaction of B's growing share with its worsening rate for 2.22, pure mix 0.08 — nothing unexplained | 5.21 pts — never added to the row above |
| Meta's cost per new customer nearly doubled, and the rise is Meta-specific | **partial** | ₹352 → ₹666 per new customer; Google and Email fell. What the corpus cannot decide: Meta spend was scaled 2.6× while new Meta customers rose 1.3×, and no month since July 2025 has spent at 2024 levels — so the rise may be Acme's own scaling | up to 2.14 pts (₹13,537) |

## The recommendation (`/synthesize`)

**Option B — fix Supplier B's sizing at the source and, in the same month, hold Meta at its
2024 spend for one month to learn whether its cost per new customer follows.** Ceiling up to
9.45 pts of Q1 FY26 contribution margin (7.30 established + up to 2.14 partial), against a
19.7% baseline.

| Option | Ceiling | Effort | Wrong if |
|---|---|---|---|
| A — fix Supplier B's sizing, nothing else (do-less) | 7.30 pts | medium | the 40%-of-cost write-down is a booking convention and returned garments are restocked — then the ceiling is 5.34 pts |
| **B — A, plus hold Meta at 2024 spend for one month** | up to 9.45 pts | medium | as A; and if the Meta rise is Acme's own scaling, the hold returns nothing and costs a month of growth |
| C — pull Supplier B's three SKUs now | at most the segment's recorded loss | easy | under the pickup-only convention the segment earns ₹2,404 before marketing and exit throws away the product's Q3 2024 contribution of ₹15,384 |

**First:** two questions to ops and finance before any option is chosen — the date(s)
Supplier B changed its size block, and whether returned Supplier B garments are restocked
or written off. The second decides between repairing the segment and pulling it.

## What `/review` attacked, and whether it survived

A fresh reviewer, given the case inline and only the corpus to read, re-derived every
figure and decomposed every rate by all eighteen export columns. No cause was killed:

- **Supplier B — wounded.** The segment is negative under both allocations and is the only
  such segment; but the 7.30-pt ceiling is rupees over a static denominator — as a
  movement of the margin it is **+5.02 pts (19.72% → 24.74%)**, because re-earned returns
  lift net revenue too; sizing-coded returns alone give ₹32,938 (5.22 pts); and the rise's
  first step is Q4 2024, before the window the mechanism names. Reproduced by the main
  context.
- **Return rate — survives; ceiling wounded** on the same denominator point (+3.67 pts of
  margin, not 5.21).
- **Meta — survives; partial stands.** Marginal CAC ₹1,763 per extra new customer against
  ₹720–988 of twelve-month contribution per Meta-acquired customer: the one-month hold is
  right under either hypothesis, and the recommendation *understates* its floor.
- **Its sharpest point:** in margin terms, Option C's exit reaches 23.6–25.2%, so the
  argument for repairing the segment over exiting it holds in rupees but not in margin
  points. Nothing was applied; the human decides.

## What the founder is asked to decide

1. **Answer two questions first** — when Supplier B's size block changed, and whether its
   returns are restocked. Both are in ops' and finance's hands, not in the data.
2. **Repair or exit Supplier B's segment.** Repair (Option A/B) is worth up to +5.0 pts of
   margin if the write-down is real, +3.7 if garments are restocked; exit (Option C) reaches
   a similar margin faster by giving up ₹15,384 a quarter of product that was profitable
   eighteen months ago. The choice turns on the restocking answer.
3. **Whether to test Meta at 2024 spend for one month.** The evidence says its cost per new
   customer is Meta-specific but cannot separate Meta's auction from Acme's own scaling; the
   hold settles that at the cost of one month's growth. *Recorded outcome (`/outcome`):
   rejected — "Don't tell me to cut Meta. Tell me what to do instead." The founder sided
   with the marketing lead; the hold was read as a cut in the run-up to the October sale.
   The practice recorded it, and the next channel-spend finding ranks lower for it.*
4. **What is not on the table:** list prices and the fundraise, as the brief asked; and the
   warehouse, headcount and courier findings, which are real but below contribution or
   outside a variable-cost question.

Every figure above traces to a query executed in the run that produced it, recorded in
`engagements/acme/{findings,investigation}.json` and `recommendation.md` with the script
text embedded.
