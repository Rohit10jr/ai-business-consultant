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
