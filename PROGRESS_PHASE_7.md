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
| `recommendation.md` | carries the superseded note | present, `check_recommendation.py` exit 2 |
| — | not mentioned in the brief | **`findings.PRE-FIX-BACKUP.json`** also present (632 KB, dated 2026-08-25) |

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
| U2 | `/investigate acme meta-cac-doubled` | not yet run |
| U3 | `/synthesize acme` | not yet run |
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
