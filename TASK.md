# TASK — start here

**ai-business-consultant** is a Claude Code harness that runs a consulting engagement end to
end. It is built, and it has had its cold run. Phase 7 watched it run start to finish for the
first time — and watched it produce the wrong answer. Phase 8 is the mechanic's turn.

---

## Already on `main` — the machine, and the record of what it did

Eight commands, 190 tests, CI green, plus the client-data guard, the synthetic corpus and
three validators. And now [`PROGRESS_PHASE_7.md`](PROGRESS_PHASE_7.md): all seven pipeline
commands ran in order on a reset engagement, both validators exited 0 on artifacts the
harness generated — and `/review` killed the recommendation on the scope question's own
terms, because `/rank` had dropped the decisive finding on an undocumented tie-break and
`/outcome` could not record that anything had gone wrong. **Thirty-one findings, none fixed,
by instruction.** Fixing them is this phase.

## Your assignment

**Fix what the cold run found. Account for all 31 findings — none silently absent.**

The findings are recorded in full in `PROGRESS_PHASE_7.md`, and its §"For the next phase"
groups the ones that matter into five clusters, because several are one defect seen
repeatedly. The clusters are the work; the disposition table (below) is the proof nothing
was dropped.

### The five clusters

| # | Findings | Where | The defect |
|---|---|---|---|
| 1 | 24, 25, 7, 18 (root: 17) | `tools/check_recommendation.py`, `tools/validate_findings.py`, `rank.md:37` | The cheap ones. The checker strips signs before matching signed values, so a recorded `-0.3390` is rejected; a comma-grouped rupee figure without a `₹` mark parses as its tail (`46,014.76` → `014.76`); the validator `continue`s after a missing-keys error and reports an incomplete work order; calibrated and uncalibrated scores share the `rank_score` key and sort against each other — because `rank.md:37`'s selection rule can never reach a `status: ranked` finding that has an investigation entry, so it is never re-typed or calibrated |
| 2 | 2 | `investigate.md:290–300` | The command file works its example **on Acme's Supplier B cause by name** and prints the answer — numerator, denominator, ratio, delta. Every run of that slug is handed its own expected result before it opens the corpus. A cold run on this corpus is not achievable while this stands |
| 3 | 6, 21, 28, 29 | `synthesize.md:103` and the overlap recording in `investigate.md` | One defect, four symptoms: the joint-recomputation formula — fix 1's centrepiece — has never had a licensed use, because no pair of causes has ever recorded `shared_rows: 0`; the option ladder inverts (doing more moves the margin less); and Option B was under-sized by 45% on causes whose rupees provably add. **`shared_rows` counts orders touched, which is the wrong proxy for whether two rupee figures overlap.** Fix the proxy, not the rule — the rule correctly stopped U8's identical-twin causes from double-counting |
| 4 | 27, 30 | `rank.md`, `outcome.md` | The tie-break and the loop that does not close. A three-way tie at 72 silently dropped `supplier-b-return-rate` — the finding `/review` later identified as the answer — and `/outcome` structurally cannot record that the wrong thing was investigated: it only sees causes that reached a recommendation. These two together are why U7 completed and taught the practice nothing |
| 5 | 4, 26 | `investigate.md` Step 0 / Step 2 | Pre-registration the runner writes after seeing last run's answers. Step 0 has it read the previous entry's thresholds and outcomes before Step 2 asks it to pre-register its own; nothing pins how a kill threshold is derived. Three runs, three alternative sets, two verdicts on the same cause |

### Work order, and why

1. **Cluster 1 first.** The tools it fixes are the instruments every later gate run is
   measured with; a gate run graded through a checker that rejects signed figures proves
   nothing.
2. **Cluster 2 before any gate run of `/investigate`.** A gate run made while the answer key
   sits in the command file is contaminated by construction. The worked example is fix 1's
   best teaching and should survive — moved out of the runner's required reading, or re-cut
   on a fictional client whose numbers appear in no fixture.
3. **Then 3, 4, 5** — the order the record gives. Cluster 3 is the highest-value; 4 is the
   structural one; 5 is the subtlest, and its fix will be judged on whether it *forces*
   independence rather than requesting it.

### The findings outside the clusters

The clusters cover 13 findings. The other 18 range from real-but-small (19: rounding
unspecified at a tie; 23: no rule when two causes tie in every figure) to observations that a
cluster fix resolves in passing (22 falls with cluster 3) to records of things working. None
requires heroics; each requires a **disposition**: fixed (name the commit), resolved-by
(name the cluster), or deferred (say why, and what would revive it). The disposition table
in `PROGRESS_PHASE_8.md` lists all 31. An empty row is a gate failure.

### What "fixed" means

The phase-6 standard, unchanged:

- **A tool fix carries a test** that fails on the old code and passes on the new — the
  exact construction from the finding, not a neighbour of it.
- **A command-file fix carries a fresh-context gate run**: a blank `general-purpose`
  subagent (never a fork), `model: "opus"`, read whitelist and scripted answers in the
  prompt, report saved to `scratch/`, graded afterwards in your own context. Record which
  model ran. The question the fix is graded on is the repo's oldest one: **does the file
  force the behaviour, or merely request it?**
- **A fix that changes what a correct run produces** updates `fixtures/*/EXPECTED.md` to
  match — with every changed figure derived from a query executed in this phase, not edited
  by hand. Graders read that file; runners never do.

### Design calls this phase must make

Two of the clusters need a design decision, not just a patch. Decide, record the reasoning
in the progress file, and keep the commits small enough that the owner can veto one without
unwinding the rest:

- **Cluster 3**: what replaces `shared_rows` as the overlap test. The record's own evidence
  points at rupee overlap on P&L lines rather than orders touched — U7's Option B causes
  landed on disjoint lines and their rupees added cleanly — but the choice is yours to make
  and defend.
- **Cluster 4**: how the loop records a triage error. Whatever you design, respect
  single-writer state — every file under `engagements/` and `practice/` has exactly one
  writing command — and remember `practice/tracker.csv` feeds `/setup`'s calibration:
  a false row there poisons every future `/rank`.

---

## Read in this order

| # | File | Why |
|---|---|---|
| 1 | [`CLAUDE.md`](CLAUDE.md) | The rules you work under, including **which model a subagent runs on** |
| 2 | [`PROGRESS_PHASE_7.md`](PROGRESS_PHASE_7.md) | **The assignment.** The opening paragraph, then §"For the next phase", then every finding a cluster names |
| 3 | [`RUNBOOK.md`](RUNBOOK.md) | The build loop, the gates, fail-stop rules |
| 4 | `BUILD_PLAN.md` §3 and §7 | The grounding contract, and where this phase sits in the road |
| 5 | [`AGENTS.md`](AGENTS.md) | What a reviewer judges this on |

**On this machine only**: `scratch/acme/*.md` holds the phase-7 runners' own reports,
including their "where the command file fought you" sections — the closest thing to a user
interview this product will ever get. `scratch/` is gitignored, so these exist here and
nowhere else; read them before touching a command file they name.

**You will read `fixtures/*/EXPECTED.md` in this phase** — updating it is in scope. That
disqualifies your context from *running* the pipeline commands, which is why every gate run
goes out to a fresh subagent and is graded after it returns. The contamination rule is
unchanged; you are on the grader's side of it.

---

## What this phase does not do

- **No second corpus.** That is phase 9, and it exists partly because this corpus's numbers
  are now in three progress files and a dozen scratch reports — no future run on Acme is
  fully cold. Do not start it early.
- **No full pipeline re-run.** Targeted gate runs prove each fix; a fresh end-to-end run
  only means something on a corpus nobody has memorised, which is phase 9's business.
- **No new state files unless a cluster forces one**, and no database, server, or web UI
  under any reading.

## Starting state

`engagements/acme/` holds what U7 left: `scope.md`, `corpus/`, `findings.json`,
`investigation.json`, `recommendation.md` — a validator-clean record of the engagement that
got the wrong answer. It is the test bed for clusters 3 and 4: the under-sized Option B and
the dropped `supplier-b-return-rate` are sitting in those files. Reset pieces as gate runs
need, and say in the progress file exactly what you reset and why.

Before anything: `git fetch origin`, then confirm this file is at the tip of
`origin/docs/phase-8-brief` — or of `origin/main` once that branch is merged; either is
fine, and the tip you find is the commit to cut `phase-8-fixes` from. Then run
`python -m unittest discover -s tests -t .` and `python tools/check_no_client_data.py`.
This is a build phase: if either fails, fixing it is the first commit, not a fail-stop.

## The rules that have not changed

1. **Client data never enters git.** `engagements/` is gitignored; the guard scans staged,
   tracked and every path ever added to history. Re-prove it this phase.
2. **No number without a source** — `BUILD_PLAN.md` §3, including every figure you edit
   into `EXPECTED.md`.
3. **Keep shell commands short.** Commit with `git commit -F .git/COMMIT_MSG`. Never
   `cat > file <<'EOF'`. Never `python - <<'PY'`.
4. **Work on `phase-8-fixes`, never `main`.** One commit per meaningful change — the owner
   reads every one, and this phase in particular is a sequence of small vetoes waiting to
   happen. The owner merges.
5. The full rule set is `CLAUDE.md`. It wins over this file where they differ.

## When you are done

1. `PROGRESS_PHASE_8.md` — format in `RUNBOOK.md`, plus the **disposition table: all 31
   findings**, each fixed / resolved-by / deferred, no empty rows.
2. `RUN_REPORT.md` — append the phase. The engagement section stays as U7 wrote it; it is
   the before picture, and phase 9 takes the after.
3. Tests green, guard proven, tier-1 review run and its findings dispositioned too.
4. Branch pushed. **No merge to `main`.**

Then say plainly, in one paragraph at the top of the progress file: **of the 31, how many
are fixed, how many deferred, and would the tie-break still have dropped Supplier B?** That
last question is the phase in one sentence — answer it with a gate run, not an opinion.
