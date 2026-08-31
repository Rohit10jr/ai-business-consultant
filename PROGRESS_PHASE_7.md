# Phase 7 — IN PROGRESS   [branch: `phase-7-cold-run`]

> **Did the pipeline run end to end?** — answered at the end of the run, in this paragraph.
> The run is still going; this file is written item by item as each lands, and committed as
> it is written, so a session that dies mid-run leaves a usable record rather than a claim.

**Every subagent in this phase was dispatched with `model: "opus"`**, passed explicitly in
the Agent tool call per `CLAUDE.md` §"Which model a subagent runs on". Their own children
inherit it. The orchestrating context (this file's author) is Opus 5 (1M context).

---

## Pre-flight

| Check | Result |
|---|---|
| Brief is current | `git fetch origin`; local tip `307d7ba` == `origin/docs/phase-7-run-brief`. `origin/main` is at `49e2841`, an ancestor. Branch cut from `307d7ba`, so `TASK.md`, `RUNBOOK.md` and `fixtures/` travel with the run |
| Tests | **190 passing**, 0 skipped, 0 failing (16.4s) |
| Client-data guard | `check_no_client_data: OK (70 staged+tracked paths, 70 paths ever added across all refs, .gitignore rules intact)`, exit 0. Staged-fixture proof recorded under the gate below |
| `codex` on PATH | `codex-cli 0.151.0` — tier 1 available |
| `git status` | clean |

### Starting engagement state — as `TASK.md` describes it, with one addition

| File | Expected | Found |
|---|---|---|
| `scope.md` | present | present — baseline 19.7%, Q1 FY26, two derivations |
| `corpus/` | present | 12 files, no `EXPECTED.md` anywhere under `engagements/` |
| `findings.json` | passes the validator | `validate_findings: OK - 11 findings(s), every figure carries its query and row counts`, exit 0 |
| `investigation.json` | **fails** on shape | fails, exit 1 — 6 problems (3 × `missing keys ['baseline_movement_at_most']`, 3 × missing `overlaps` pair) |
| `recommendation.md` | carries the superseded note | present; `check_recommendation.py` reports **74 figures from nowhere**, exit 1 |
| — | not mentioned in the brief | **`findings.PRE-FIX-BACKUP.json`** also present (632 KB, dated 2026-08-25) |

**Correction to this table, made during U3.** My first pre-flight pass ran
`check_recommendation.py` with one argument and recorded "exit 2" as though it were a
content failure. It is not: the checker takes three arguments and exit 2 was argparse
rejecting the call. Run properly —
`check_recommendation.py engagements/acme/recommendation.md engagements/acme/investigation.json engagements/acme/scope.md`
— it reports **74 figures from nowhere, exit 1**, the first three being
`- Rs 46,121.67 = 42.3255 * Rs 1,089.69`, `- 9.4483 pts = 7.3044 pts + 2.1439 pts` and
`- Rs 59,658.78 = Rs 46,121.67 + Rs 13,537.11`. The starting state is worse than my
pre-flight said, not better. The table above now carries the corrected figure.

`findings.PRE-FIX-BACKUP.json` is a state deviation, recorded rather than repaired: the
brief names four files and this is a fifth. It is gitignored like everything under
`engagements/`, no command reads it, and it did not affect any item below.

### Scratch reset

`scratch/acme/` and the loose `*_run_acme*.md` reports from phases 3–6 were moved to
`scratch/acme-phase3-6-archive/` — moved, not deleted, so the earlier evidence survives but
cannot be mistaken for this run's. This run writes only under a fresh `scratch/acme/`. The
starting engagement files were snapshotted to `scratch/acme/00-starting-state/` before any
item ran, so every before/after in this file is against a copy taken cold.

### How each item was run

A fresh `general-purpose` subagent per command — never a fork — carrying: the invocation
verbatim; a read whitelist (the command file, the files it names, `engagements/acme/**`,
`practice/**`, `tools/**`); an explicit ban on `fixtures/**`, `TASK.md`, `RUNBOOK.md`,
`BUILD_PLAN.md`, `docs/**`, `PROGRESS_PHASE_*.md`, `RUN_REPORT.md` and reading anything
pre-existing under `scratch/`; no git; the 400-character shell limit; the human's answers
scripted from `TASK.md`; and a required report with a **Files read** audit list. Grading
happens afterwards, here, against the pass conditions in `PROGRESS_PHASE_6.md`.

The items are run sequentially, not in parallel. U1–U4 all write `engagements/acme/`, and a
race between two of my own subagents would manufacture a failure that is mine and not the
harness's.

---

## Results — U1 to U8

| # | Item | Result |
|---|---|---|
| U1 | `/investigate acme supplier-b-returns-negative-contribution` | **FAILED** — on the validator condition only; the two figure conditions passed |
| U2 | `/investigate acme meta-cac-doubled` | **PASSED** |
| U3 | `/synthesize acme` | **FAILED** — pass condition unreachable; `/synthesize` itself refused correctly |
| U4 | `/review acme` | not yet run |
| U5 | `/setup frameworks` | not yet run |
| U6 | `/rank acme --all` | not yet run |
| U7 | the whole pipeline cold | not yet run |
| U8 | `/investigate acme` with 2+ slugs | not yet run |

---

## U1 — `/investigate acme supplier-b-returns-negative-contribution` — **FAILED**

Model: Opus. 78 tool calls, 233k tokens, 27 minutes. Report:
`scratch/acme/U1-investigate-supplier-b.md`. Cold: the **Files read** list contains no
`fixtures/`, no `docs/`, no `TASK.md`, no `RUNBOOK.md`, no `BUILD_PLAN.md`, no progress file,
and nothing pre-existing under `scratch/`.

The pass condition has three parts. Two passed, one failed.

| Pass condition | Result |
|---|---|
| `baseline_movement_at_most` ≈ 19.72% → 24.74% (+5.02 pts), `numerator_delta` ≈ 46,121.67, `denominator_delta` ≈ 58,370 | **PASS, off by ~1.5%** — 19.72% → 24.68%, **+4.96 pts**; `numerator_delta` 45,453.71, `denominator_delta` 57,331.76. Shape exactly right; see below on why the value differs and why that is the good news |
| `recoverable_at_most` in rupees | **PASS** — `{"value": 45453.71, "unit": "rupees", ...}`, with its query and query text carried |
| validator clean | **FAIL** — exit 1 |

### What was written

```json
"recoverable_at_most": {"value": 45453.71, "unit": "rupees", "period": "Q1 FY26, 2026-01-01..2026-03-31 inclusive (fiscal year = calendar year, per brief.md)", ...}

"baseline_movement_at_most": {
 "numerator_from": 124540.03, "numerator_to": 169993.74, "numerator_delta": 45453.71,
 "denominator_from": 631425.85, "denominator_to": 688757.61, "denominator_delta": 57331.76,
 "from": 19.72, "to": 24.68, "delta": 4.96,
 "unit": "pts of the baseline (contribution / net revenue, Q1 FY26)",
 "rows_in": 5475, "rows_out": 86
}
```

Both terms move, the ratio is recomputed rather than copied (169,993.74 / 688,757.61 =
24.68%), and `delta = to − from`. The frozen-denominator figure phase 6 exists to kill —
45,453.71 ÷ 631,425.85 = 7.20 pts — appears nowhere in the record. **That is fix 1 working
at runtime**, which is what U1 was for.

Seventeen figures re-derived, three decomposition tables (sku, supplier, customer_type)
reconciling to 1e-10, seven pre-registered counter-hypotheses — five `ruled_out`, two
`supported`, none `not_ruled_out`. `claim_strength: established`. `overlaps` recorded
`shared_rows: 52` against `return-rate-doubled` and `11` against `meta-cac-doubled`.

### The failure, verbatim

```
$ python tools/validate_findings.py engagements/acme/investigation.json
validate_findings: 3 problem(s) in engagements\acme\investigation.json
  - investigation return-rate-doubled: missing keys ['baseline_movement_at_most']
  - investigation meta-cac-doubled: missing keys ['baseline_movement_at_most']
  - overlaps: no entry for return-rate-doubled / meta-cac-doubled - the rows the two fixes touch must be compared by a query before /synthesize may combine them
exit=1
```

Reproduced by this context after the run. Before the run the same command reported **6**
problems; this run cleared exactly the 3 that were its own. Not one of the 3 remaining
belongs to the slug U1 investigated.

### Finding 1 — a single-slug `/investigate` can no longer make the validator pass

`.claude/commands/investigate.md:313`:

> an entry is replaced only for the slugs investigated this run, **every other entry is
> copied through byte-identical**

`.claude/commands/investigate.md:422`:

> **If it reports problems, fix the record or weaken the claim; do not report until it
> passes.**

The validator's scope is the whole file; Step 7's mandate is one entry. Once any sibling
entry is stale — which is precisely the starting state `TASK.md` describes and U1 was sent
into — the two instructions cannot both be obeyed. Either the run edits entries it was
forbidden to touch, or it reports with a failing validator.

The subagent took the second, which is the correct choice under this phase's rules, and
proved its own entry is sound by validating a scratch copy containing only it: `OK`. The
deadlock clears itself once every entry has been regenerated (U8 does this), so it is a
transitional-state defect rather than a permanent one — but the transitional state is the
one a real engagement is in every time the schema changes, and the command file offers no
way through it. Not fixed. Phase 8's business.

### Finding 2 — the command file contains the answer key for this exact slug

`.claude/commands/investigate.md:290–300` works the example **on Acme's Supplier B cause by
name**, and prints the result:

```
290: **Worked, by hand, on Acme's Supplier B cause** — the numbers `/review` derived on the
296: | fix applied: Supplier B's excess returns stop | +₹46,121.67 (…) | +₹58,370 (…) |
297: | Q1 FY26 with the fix | ₹170,661.70 | ₹689,795.85 | **24.74%** |
299: `recoverable_at_most` = ₹46,121.67. `baseline_movement_at_most` = 19.72% → 24.74%,
300: **+5.02 pts**.
```

`/investigate` must read this file before it can investigate anything, so every run of this
slug is handed its own expected numerator, denominator, ratio and delta before it opens the
corpus. The repo bans `fixtures/*/EXPECTED.md` from a run for exactly this reason; the same
information for one client sits inside the command file.

**This makes U1's own pass condition partly self-fulfilling** — the "≈ 46,121.67 / ≈ 58,370"
it is graded against are printed in the file the runner is required to read. Which is why
the ~1.5% miss is the reassuring result and not the worrying one: a run that copied would
have returned 46,121.67 exactly. This one derived 45,453.71 at SKU grain, and reports that
its coarser segment-grain second derivation gave 46,014.76 / 58,234.21 — evidently the grain
the worked example used. The arithmetic is independent; the difference is a grain choice the
command file does not pin down.

### Finding 3 — `established` survives an alternative that flips the segment's sign

The measurement counter-hypothesis came back `supported`, not `ruled_out`: Supplier B's
Q1 FY26 return handling carries a **₹15,231.61** write-down booked at a 40% rate that the
head of ops gave as an estimate. Under the pickup-fee-only convention the segment is
**+₹2,404.03** before marketing rather than −₹12,827.58 — the sign of the headline claim
depends on an unverified booking convention.

Step 5 forces `partial` only on a `not_ruled_out` candidate or an allocation pair that
changes the conclusion. A `supported` alternative that inverts the sign is neither, so the
rule as written yields `established`. The run complied, pushed the qualification into the
claim, the mechanism and the open questions, and flagged it. The grading rule and the
claim-strength label disagree about what "established" should mean.

Also recorded: preventing the excess returns still leaves **₹6,366.42** of Supplier B's fall
in contribution per order unexplained.

### Nothing was fixed

No file in `.claude/` or `tools/` was touched by U1 or by this context.

---

## U2 — `/investigate acme meta-cac-doubled` — **PASSED**

Model: Opus. 72 tool calls, 260k tokens, 26 minutes. Report:
`scratch/acme/U2-investigate-meta-cac.md`, entry JSON alongside at
`scratch/acme/U2-investigate-meta-cac.entry.json`. Cold — same audit as U1.

Pass condition: *the movement carries `denominator_unchanged_because`, or a denominator
delta with its reason.* It carries the former, and argues it structurally rather than
asserting it:

```json
"numerator_from": 124540.03, "numerator_to": 138077.14, "numerator_delta": 13537.11,
"denominator_from": 631425.85, "denominator_to": 631425.85, "denominator_delta": 0.0,
"denominator_unchanged_because": "the fix buys the same 43 new Meta customers for less
  money. No order is added, cancelled or refunded, so gross_revenue and refunds - the two
  columns pnl_monthly.csv builds net_revenue from - are untouched; the whole saving lands
  in the marketing_spend column, which that file subtracts inside contribution. Unlike a
  returns fix, nothing is re-earned as revenue, so only the numerator moves",
"from": 19.7236, "to": 21.8675, "delta": 2.1439,
"rows_in": 5475, "rows_out": 43
```

`recoverable_at_most` = `{"value": 13537.11, "unit": "rupees"}`. The previous run recorded
this same cause as `{"value": 2.1439, "unit": "pts of Q1 FY26 contribution margin (Rs
13,537.11 / net revenue 631,425.85) …"}` — the frozen-denominator division phase 6 exists to
kill, in the ceiling field itself. **Fix 1 corrected it at runtime.** Here the two coincide
numerically because the denominator genuinely does not move; the point is that the record
now distinguishes them.

Validator, verbatim, after the run:

```
$ python tools/validate_findings.py engagements/acme/investigation.json
validate_findings: 1 problem(s) in engagements\acme\investigation.json
  - investigation return-rate-doubled: missing keys ['baseline_movement_at_most']
exit=1
```

Three problems before this run, one after; the remaining one is the third entry, which U2
was forbidden to touch — the same `:313`/`:422` deadlock recorded under U1. U2's condition
does not mention the validator, so this does not fail the item. The subagent proved
confinement by validating a copy with that entry removed: `OK - 2 investigation(s)`, and
verified byte-identity of both untouched entries against a pre-write snapshot.

### Finding 4 — two runs of the same command, on the same data, disagree on claim strength

The previous run recorded `meta-cac-doubled` as **`partial`**. This one records
**`established`**. `RUNBOOK.md` §"Judgment calls" says a disagreement between two runs is a
finding about the command, so here it is, and the cause is exact and narrow.

Both runs pre-registered the same `other` candidate — that the CAC rise is Acme's own
scaling rather than Meta's auction — and each invented its own kill threshold:

| | previous run | this run |
|---|---|---|
| pre-registered test | months from 2025-07 with Meta spend **≤ 6,000** | months from 2025-07 with Meta spend **≤ Rs 8,000** |
| months qualifying | **0** — "the pre-registered test cannot be run" | **3** — 2025-09, 2025-10, 2026-01 |
| result | — | pooled CAC **539.20** vs a Rs 500 kill threshold |
| status | **`not_ruled_out`** | **`ruled_out`** |
| claim strength | **`partial`** | **`established`** |

The 2024 monthly Meta spend range is 2,341.80..7,946.86. A cut at 6,000 selects nothing; a
cut at 8,000 selects three months. Nothing in the command file pins the threshold, so the
runner's own choice of it decides whether the claim is `established` or `partial` — and the
claim strength is what `/synthesize` and the founder read.

This is compounded by the second thing the run reported: **Step 0 has the runner read the
previous run's entire pre-registration — thresholds and outcomes — before Step 2 asks it to
pre-register its own.** A re-investigation therefore cannot demonstrate that its hypotheses
were chosen independently of the answers it already saw. Pre-registration whose thresholds
are chosen by the runner, after being shown which threshold failed last time, is not
pre-registration. Not fixed.

To be fair to this run: its ≤8,000 cut is the better test — it is the one that actually
selects months inside the 2024 range and can be executed, and it ruled the candidate out on
a number rather than on an inability to test. The defect is that the command file permits
either, not that this run chose wrongly.

### Finding 5 — Step 3's decomposition base is unspecified, and it moves the figures ~1.7×

`meta-cac-doubled` is a per-customer cost, not a rate with a denominator the corpus defines,
and Step 3 does not say which aggregate to decompose. The previous run used paid channels
only; this run used all new customers, blended.

| | previous run (paid only) | this run (all channels) |
|---|---|---|
| total change in blended CAC | +71.1308 | +35.2845 |
| Meta's own rate effect | **+127.2315** (178.87%) | **+76.2599** (216.13%) |
| pure mix | −3.5794 | −8.2088 |
| interaction | −19.1681 | −12.7754 |

Both decompositions reconcile to their own total exactly, both clear the 50% threshold, and
the verdict is stable — but the reported magnitudes differ by about 1.7×, and a reader of
one record cannot tell which base produced it without recomputing. Not fixed.

Unchanged across both runs and worth recording as the harness working: Meta CAC
351.6736 → 666.4900 (+89.52%), Google −5.52%, Email −22.86%, spend ties to
`pnl_monthly.csv` at max |difference| 0.00 over 36 months.

---

## U3 — `/synthesize acme` — **FAILED**

Model: Opus. 14 tool calls, 79k tokens, 5.5 minutes. Report: `scratch/acme/U3-synthesize.md`.
Nothing under `engagements/` was touched — mtimes and sizes identical to the pre-run listing.

**The command refused, and the refusal was correct.** It stopped at its Step 0 gate:

```
$ python tools/validate_findings.py engagements/acme/investigation.json
validate_findings: 1 problem(s) in engagements\acme\investigation.json
  - investigation return-rate-doubled: missing keys ['baseline_movement_at_most']
exit=1
```

`synthesize.md` requires the stop — *"If it reports problems, stop … Say 're-run
`/investigate <client> <slug>` for the entries it names'."* Step 2 was never reached, so no
option, no `Ceiling:` line and no `Movement:` line exists. The item's pass condition —
*Option B's `Movement:` line is one joint division over both terms (≈ 26–27%);
`check_recommendation.py` clean* — is therefore unmet, and U3 is recorded FAILED.

The failure is upstream of `/synthesize`, in the third investigation entry no item has yet
regenerated. But the item would have failed anyway, for a reason that has nothing to do with
that entry:

### Finding 6 — U3's pass condition is forbidden by phase 6's own overlap rule

`.claude/commands/synthesize.md:103`:

> Two causes may be **combined only if their pair is recorded with `shared_rows: 0`.**

The record, written by U1 and U2 from executed queries:

| pair | `shared_rows` | combinable? |
|---|---|---|
| supplier-b-returns-negative-contribution / return-rate-doubled | **52** | no |
| supplier-b-returns-negative-contribution / meta-cac-doubled | **11** | no |
| return-rate-doubled / meta-cac-doubled | **24** | no |

Option B *is* the combination of the Supplier B cause and the Meta cause. Their pair shares
11 rows, so the rule forbids combining them, so no joint movement figure may be written, so
the ≈26–27% the pass condition demands **cannot legally exist on this record**. Every option
would have to be sized on its larger cause alone.

Phase 6 shipped the overlap rule and this pass condition in the same phase, and ran neither.
Step 2's longest passage — the joint-recomputation formula
`to = 100 × (n₀ + Δn₁ + Δn₂) / (d₀ + Δd₁ + Δd₂)`, the centrepiece of fix 1 — has **no
licensed use on this engagement at all**. Not fixed. This is the clearest example so far of
what running cold catches that reading cannot.

### Finding 7 — the validator's refusal message is an incomplete work order

`tools/validate_findings.py:320` does `continue` immediately after a missing-keys error,
suppressing every remaining check on that entry:

```python
        if miss:
            errors.append(f"{where}: missing keys {sorted(miss)}")
            continue
```

So the message says `1 problem(s)` and names one missing key. On an in-memory copy (nothing
written) the run confirmed `return-rate-doubled` carries a **second**, independent violation:

```
recoverable_at_most.value = 5.212
recoverable_at_most.unit  = "pts of Q1 FY26 contribution margin (Rs 32,910.11 /
                             net revenue 631,425.85); Supplier B's own rate effect only…"
```

That is a ceiling in points, computed as rupees over a frozen denominator — the precise
thing fix 1 exists to forbid, sitting in the entry no run has regenerated. The two defects
are one mistake seen twice: the movement was written into the ceiling's unit string instead
of into its own key.

The consequence is operational, not cosmetic. A human who does exactly what the refusal tells
them — re-run `/investigate acme return-rate-doubled` to add the missing key — gets a second
refusal naming a defect the first message could have named. The count in the header is wrong
too: `1 problem(s)` where there are at least two. Not fixed.

### Finding 8 — the stale, failing `recommendation.md` is left in place unflagged

`/synthesize` exits before its Step 4 hand-off, correctly. But it leaves
`engagements/acme/recommendation.md` on disk — a document that fails its own checker on 74
figures and whose headline `7.3044 pts` contradicts the `5.212` now in the record. Nothing
in the command file covers this state, and nothing stops a human running `/review acme`
against it. U4 is about to do exactly that. Not fixed.
