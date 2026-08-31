# TASK — start here

**ai-business-consultant** is a Claude Code harness that runs a consulting engagement end to
end. It is built. Phase 7 is the first time anyone runs the whole thing cold.

---

## Already on `main` — do not rebuild, do not fix

Eight commands, 190 tests, CI green. `/setup`, `/scope`, `/discover`, `/rank`,
`/investigate`, `/synthesize`, `/review`, `/outcome`, plus the client-data guard, the
synthetic corpus, and three validators.

Phases 0-6 are recorded in `PROGRESS_PHASE_0.md` through `PROGRESS_PHASE_6.md`.

## Your assignment

**Run the pipeline. Report what happens.**

The harness has only ever run in pieces — one command at a time, on different days, as each
phase's gate, with the harness being changed between them. **Nobody has watched it run start
to finish.** Until that happens, "it works" is a claim about seven separate afternoons.

Phase 6 changed two rules and, by the owner's instruction, ran nothing. It left a list of
exactly what needs running, as **U1 through U8** in
[`PROGRESS_PHASE_6.md`](PROGRESS_PHASE_6.md) §"Runtime gates". **That table is your
assignment.** Each row names the command and what it must produce. Work it in order.

U7 is the whole pipeline cold, `/scope` → `/outcome`. The other seven are its parts, and
running them first tells you where it will break before you commit to the long run.

### The rule that matters more than the list

**If it breaks, let it break, and write down exactly where.**

Do not fix the harness mid-run. Do not re-run a command "properly" after seeing the output.
Do not repair a prompt file and continue. A run that was repaired halfway through is what
this repo already has seven of, and it is precisely the thing phase 7 exists to stop being
the only evidence.

A phase 7 that gets to U4, fails, and reports the failure in detail is **worth more** than
one that quietly patched `/investigate` and reached U8. Fixes are phase 8's business; you are
the instrument, not the mechanic.

The single exception: something that stops the run being *possible* rather than *correct* — a
crashing tool, a missing file. Fix that, say you did, and say why it was not a finding.

---

## Read in this order

| # | File | Why |
|---|---|---|
| 1 | [`CLAUDE.md`](CLAUDE.md) | The rules you work under, including **which model a subagent runs on** |
| 2 | [`PROGRESS_PHASE_6.md`](PROGRESS_PHASE_6.md) | **Your assignment is the U1-U8 table.** Read the whole file: it says what changed and what was never run |
| 3 | [`RUNBOOK.md`](RUNBOOK.md) | The loop, the gates, the fail-stop rules |
| 4 | [`RUN_REPORT.md`](RUN_REPORT.md) — the engagement section | What the pipeline produced last time, under the old ceiling rule. Your run replaces it |
| 5 | [`AGENTS.md`](AGENTS.md) | What a reviewer judges this on |

You should not need the command files. If you find yourself reading `/investigate` to work
out why its output is wrong, stop — that is a finding, and writing it down is the job.

---

## Two things that make this run mean something

**Dispatch your subagents with `model: "opus"`**, per `CLAUDE.md` §"Which model a subagent
runs on". That is this repo's development convention and it applies to you. It is **not** in
the command files, deliberately — whoever runs this harness on a real client picks their own
model on their own budget. You pass it at the top and inheritance carries it down: a graded
`/discover` dispatched on Opus spawns per-branch children that inherit Opus from it.

**Record which model each run used** in the progress file. Not to justify it — so a reader
can weigh the result. A gate passed on one model is weaker evidence about another, and the
original failure here was not the wrong model but that nobody chose and nobody could tell
afterwards.

If you find a command file naming a model, **that is a finding** — the lint forbids it.

**Fresh context is the whole point.** You did not write these fixes, and that is what makes
your run evidence rather than a demonstration of the author. Do not read
`fixtures/*/EXPECTED.md` — the commands forbid it, and so does this brief. Grade against it
afterwards, once the output is written down and cannot be influenced.

---

## The human's answers

Several commands stop and ask the human. The human is not in the run, so their answers are
fixed here in advance — script them into each subagent's prompt verbatim, and require an
"Answers applied" section in its report. These are the owner's answers; do not improvise
others, and record faithfully anything a command does that these do not cover.

- **`/scope acme`** (U7 only): overwrite the existing scope — **yes**. Keep the same
  question and the same baseline if the command re-derives them; confirm the baseline when
  the derivation is shown and agrees. `done_when` and `out_of_scope` as currently in
  `scope.md`.
- **`/rank acme`** — "which findings should `/investigate` pursue?": **the top three by
  score**.
- **`/investigate acme`**: the slugs are the three `/rank` named. Any re-investigate
  prompt: **yes**.
- **`/outcome acme`**: sector `D2C apparel`, size band `under ₹5 Cr revenue`, engagement
  type `margin diagnosis`. For the recommended option's rows: the supplier/returns cause —
  **accepted**, finding type `supplier`, pushback "Ops wants the size chart on the store
  re-cut before any conversation with Supplier B about corrected stock"; the channel-spend
  cause — **rejected**, finding type `channel-spend`, pushback "The marketing lead: 'Don't
  tell me to cut Meta. Tell me what to do instead.' The founder sided with her.", reason
  "the hold was read as a cut in the run-up to the October sale". Other options: **skip**.
  Confirm every row shown as written.

## Starting state

`engagements/acme/` holds `scope.md`, `corpus/` and a `findings.json` from the previous run.
Two things about it, both intentional:

- `investigation.json` **fails the validator** on shape — it predates phase 6's movement
  figure. `/synthesize` and `/review` will refuse it until `/investigate` regenerates it,
  which is U1.
- `recommendation.md` carries a note saying its ceilings are superseded. Your run replaces
  the file; do not edit the note.

`scratch/` still holds every phase 3-6 run's reports and query scripts. **Start from a clean
`scratch/acme/`** so nothing from a previous run can be mistaken for this one's.

Before anything: `git fetch origin`, confirm you are cut from `origin/main`, run
`python -m unittest discover -s tests -t .` and `python tools/check_no_client_data.py`. If
either fails, that is a finding and the run stops there.

---

## The rules that have not changed

1. **Client data never enters git.** `engagements/` is gitignored; the guard scans staged,
   tracked and every path ever added to history.
2. **No number without a source.** `BUILD_PLAN.md` §3.
3. **No Claude attribution** — no `Co-Authored-By`, no mention in commit messages or PR text.
4. **Keep shell commands short.** Commit with `git commit -F .git/COMMIT_MSG`. Never
   `cat > file <<'EOF'`. Never `python - <<'PY'`.
5. **Work on `phase-7-cold-run`, never `main`.** The owner merges.

## When you are done

1. `PROGRESS_PHASE_7.md` — format in `RUNBOOK.md`, and one row per U-item: passed, failed, or
   not reached, with what actually came out. A failed item needs the output that failed, not
   a description of it.
2. `RUN_REPORT.md` — append the run, and **replace the engagement section** with what this
   run produced. The old one was written under the ceiling rule phase 6 corrected.
3. Branch pushed. **No merge to `main`.**

Then say plainly, in one paragraph at the top of the progress file: **did the pipeline run
end to end, or not?** That sentence is what the owner is waiting for. Everything else is
supporting detail.
