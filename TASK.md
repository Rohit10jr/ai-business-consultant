# TASK — start here

You are building **ai-business-consultant**, a Claude Code harness that runs a consulting
engagement end to end.

Nothing is built yet. You are starting from an empty repo with a plan.

---

## Your assignment

**Phases 0, 1 and 2.** Then stop.

| Phase | Branch | Delivers |
|---|---|---|
| **0** | `phase-0-skeleton` | Repo skeleton, the client-data CI guard, the synthetic fixture corpus |
| **1** | `phase-1-scope` | `/setup` and `/scope` |
| **2** | `phase-2-discover` | `/discover` and `/rank` |

**HARD STOP after phase 2's gate passes.** Do not start phase 3. The grounding checklist is
the hardest part of this project and the owner wants to read phase 2's real output before
its design is settled.

---

## Read in this order

Roughly 45 minutes. Do not skip — most design questions are already answered.

| # | File | Why |
|---|---|---|
| 1 | [`CLAUDE.md`](CLAUDE.md) | The rules you are working under. 8 hard rules, the stack, reviewer policy |
| 2 | [`BUILD_PLAN.md`](BUILD_PLAN.md) | Architecture, command surface, **the grounding contract (§3)**, state model, phases |
| 3 | [`docs/WORKED_EXAMPLE.md`](docs/WORKED_EXAMPLE.md) | One engagement end to end. **What you are building, made concrete** |
| 4 | [`docs/CONSULTING_METHOD.md`](docs/CONSULTING_METHOD.md) | The domain. What consultants actually do, as an algorithm |
| 5 | [`docs/REFERENCE_PATTERN.md`](docs/REFERENCE_PATTERN.md) | The architecture lessons this copies, distilled |
| 6 | [`RUNBOOK.md`](RUNBOOK.md) | The loop, the gate, fail-stop rules, progress-file format |
| 7 | [`AGENTS.md`](AGENTS.md) | What the reviewer will judge you on. Read it before writing, not after |

**Optional, for depth:** the reference implementation at
`D:\02_Personal\01_OpenSource\03_Applications\ai-job-search`. Read-only — never edit it,
never run git in it. `docs/REFERENCE_PATTERN.md` distils what matters, so start there and
only open the real repo if a specific question survives.

---

## The five things that matter most

If you remember nothing else:

1. **Client data never enters git.** `engagements/` is gitignored already. Phase 0's first
   deliverable is a CI guard, and its gate requires you to *prove the guard fails* by
   staging a fixture. Build the guard before anything that reads a corpus.

2. **No number without a source.** Every figure traces to a document or a query executed in
   that run, with the source shown. A figure that cannot be traced is **removed, not
   softened**. `BUILD_PLAN.md` §3 is the full contract.

3. **No Claude attribution.** No `Co-Authored-By` trailer, no crediting Claude in commit
   messages, PR text, or release notes. This is the owner's repo under the owner's name.
   Naming the file `CLAUDE.md` or saying "Claude Code harness" is fine — those are a
   filename and a platform.

4. **Prompt files are the product.** You are mostly writing markdown that an LLM executes,
   not Python. A vague rule in a `.md` file is a bug. The test is: *does this force the
   behaviour, or merely request it?*

5. **Keep shell commands short.** A command over ~400 characters cannot be security-scanned
   and escalates to human review, which stalls an unattended run indefinitely. Commit with
   `git commit -F .git/COMMIT_MSG`. Never `cat > file <<'EOF'`. Never `python - <<'PY'`.
   Use the Write tool.

---

## Phase 0 in detail

The other two are specified in `BUILD_PLAN.md` §7. Phase 0 is worth expanding because
everything depends on it.

**Deliverables:**

```
tools/check_no_client_data.py     the guard
.github/workflows/ci.yml          lint + tests + the guard
tests/                            test scaffold, unittest
fixtures/acme-d2c/                the synthetic corpus — see fixtures/README.md
.claude/                          commands/ and skills/ directories, empty
practice/                         profile scaffold, tracker.csv gitignored
```

**The guard** must fail with a non-zero exit and a clear message when any path under
`engagements/` is staged, or when a corpus-shaped file (`.xlsx`, `.csv`, `.pdf`, `.pptx`)
is staged outside `fixtures/`. Model it on `tools/security_guards.py` in the reference
repo — stdlib only, no dependencies, exits 1 with a list.

**The fixture corpus** is what makes phases 2-5 testable without a real client. Spec is in
`fixtures/README.md`. Build it in phase 0, not later — phase 2 cannot be gated without it.

**Gate:** tests pass · the guard **provably** fails on a staged fixture (stage one, confirm
exit 1, unstage) · independent review · clean tree, branch pushed.

---

## When you are done

1. `PROGRESS_PHASE_0.md`, `PROGRESS_PHASE_1.md`, `PROGRESS_PHASE_2.md` — format in
   `RUNBOOK.md`
2. `RUN_REPORT.md` — what shipped, what each gate showed, what is blocked, what the next
   runbook should cover
3. All three branches pushed. **No merge to `main`.**

Be honest in the report about what did not work. A stopped run that reports clearly is a
success; a run that pushes past a fail-stop is not, however much it produced.
