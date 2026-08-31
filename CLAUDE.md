# ai-business-consultant — agent brief

**This repo builds a Claude Code harness that runs a consulting engagement end to end:**
take a vague client pain, sharpen it into one answerable question, read the client's own
document corpus, surface candidate findings the client did not know were there, rank them,
build the case on the top few, have a second agent attack it, and record what the client
actually accepted.

It is **not** a chatbot, not a report generator, and not an autonomous agent. It is a set
of prompt-defined commands a human triggers, passing state through plain files on disk,
with a hard stop before anything leaves the building.

Phases 0 and 1 are built, reviewed and merged. Phase 2 onward is a greenfield build
from a proven pattern - see `TASK.md` for what is done and what is yours.

## Read these first

Start at [`TASK.md`](TASK.md) — it names your assignment and the reading order.

| File | What it is |
|---|---|
| **`TASK.md`** | **The assignment. Start here** |
| **`BUILD_PLAN.md`** | Architecture, command surface, **the grounding contract (§3)** |
| **`docs/WORKED_EXAMPLE.md`** | One engagement end to end. What you are building, made concrete |
| `docs/CONSULTING_METHOD.md` | The domain — what consultants do, as an algorithm |
| `docs/REFERENCE_PATTERN.md` | The architecture lessons this copies, distilled |
| `RUNBOOK.md` | The loop, the gate, fail-stop rules, progress format |
| `AGENTS.md` | The reviewer's brief — read it so you know what you will be judged on |
| `fixtures/README.md` | The synthetic corpus, and the flawed investigation `/review` must kill |

## The reference implementation

`docs/REFERENCE_PATTERN.md` distils what matters from a proven harness in a different
domain, so **you do not need to read another repo to start**. Open the real thing only if a
specific question survives that file.

```
D:\02_Personal\01_OpenSource\03_Applications\ai-job-search
```

Worth knowing if you do: `.claude/commands/apply.md` (drafter/reviewer pattern),
`.claude/commands/rank.md` (parallel scoring), `docs/ai-job-search/02-data-flow.md`
(state ownership), `docs/ai-job-search/04-findings.md` (its real defects — do not
reproduce them).

**Read for structure, not content.** Job postings and CVs have nothing to do with margin
analysis. What transfers is how a command file is written, where human gates go, how state
is owned, how grounding is enforced, and what the machine is forbidden to do.

## Read that repo, do not edit it

Separate git repo, own remote, uncommitted work in progress. **Read-only reference.** Never
`cd` into it to run git, never edit a file there, never commit there.

## Hard rules

1. **Client data never enters git.** Everything under `engagements/` is gitignored from
   the first commit — before any real corpus lands. A client's P&L in a git history is
   unrecoverable. This is the single most important rule in the repo.
2. **No Claude co-authorship on commits.** Do not add `Co-Authored-By: Claude` or any
   equivalent trailer, and do not mention Claude in commit messages. This is the owner's
   repo under the owner's name. The same applies to PR descriptions and release notes.
3. **The harness never contacts anyone.** No email, no Slack, no calendar invite, no
   sending. It drafts; a human sends. Wire it to no tool that could.
4. **No number without a source.** Every figure in any output traces to a document, a
   query that was executed in that run, or a named interview. Never to inference, never to
   memory, never carried forward from a previous run without re-running. This is the
   project's equivalent of that repo's three-source grounding union, and it matters more
   here — an ungrounded CV bullet is embarrassing, an ungrounded figure in a business case
   is a decision someone makes with money.
5. **One commit per meaningful change.** The owner reads every one. A commit too large to
   review in a sitting has failed even when the code is right.
6. **Work on a feature branch, never `main`.** No merge to `main` without the owner.
7. **Conventional beats clever.** If there are two ways and one is what a Python developer
   would expect, use that one even if the other is shorter. Anything surprising is a defect
   even when it works.
8. Comments explain **why**, not what. A comment earns its place by recording a decision or
   a trap.

## Stack

Deliberately small. The value is in the prompt files, not the code.

| Layer | Choice |
|---|---|
| Harness | Claude Code — `.claude/commands/*.md`, `.claude/skills/*/SKILL.md` |
| Scripts | Python 3.11+, standard library first |
| Deps | Only where they earn it. `openpyxl` for spreadsheets, `pypdf` for PDFs |
| Tests | `unittest` via `python -m unittest discover -s tests -t .` |
| State | Plain files — JSON for working sets, CSV for the ledger, markdown for artifacts |
| CI | GitHub Actions — lint, tests, and a guard that blocks client data |

**No database, no server, no web UI.** If a design calls for one, that is a signal the
design has drifted.

## Keep shell commands short

**A long command cannot be security-scanned, so it escalates to human review — which
stalls an unattended run indefinitely.** No permission rule can pre-approve it; the harness
refuses to approve text it could not read.

Long *content* belongs in a file. The command that uses it stays tiny.

1. **Commit from a file, never inline.** Write the message with the Write tool, then
   `git commit -F .git/COMMIT_MSG`. Not `git commit -m "$(cat <<'EOF' … EOF)"`.
2. **Never inline a script.** Write `scratch/patch.py`, then `python scratch/patch.py`.
   No `python - <<'PY' … PY`.
3. **Never write file contents through the shell.** No `cat > file <<'EOF'`. Use Write and
   Edit — nothing gets scanned.
4. **Keep any single command under ~400 characters.** Chained commands count as one.

---

# Reviewer policy — three tiers

You write it; something that does **not** share your blind spots reviews it. Try in order,
stop at the first that genuinely works, and always say which tier you used.

| Tier | Reviewer | Notes |
|---|---|---|
| **1** | Codex via PowerShell 7 | Preferred — different model, reads the repo itself |
| **2** | Codex via PowerShell 5.1 | Same reviewer, fallback shell |
| **3** | Claude subagent | **Degraded** — correlated blind spots, unless it is on a different model from yours (see below) |

## Which model a subagent runs on

**You build on whatever model the owner started you on. Every subagent you spawn to *run* a
command runs on `opus`** — pass `model: "opus"` in the Agent tool call, explicitly, every
time. Do not leave it out and let the subagent inherit: inheritance is what put the whole of
phases 3-5 on the parent's model without anyone choosing it.

The split is deliberate. Building the harness is design work and stays where the owner put
it. Running a command is graded work, and what makes those runs worth anything is that the
context is **fresh**, not that it is the strongest available model — a subagent that has not
seen the answer key is the whole point. Phase 4 is the evidence: a subagent killed the
planted bad investigation and named Supplier A's 3.04 points unprompted. Fresh context did
that, not raw capability.

Two consequences worth knowing:

- **A `fork` cannot be redirected.** Forks always inherit the parent's model and ignore
  `model`. Every subagent in this repo is `general-purpose` for the fresh-context reason
  already, so this never bites — but do not switch one to a fork for convenience.
- **Tier 3 review is less degraded than the table above says** when the reviewer is on a
  different model from the author. The table's "correlated blind spots" warning assumes
  inheritance. Say which model the reviewer ran on in the progress file, and the reader can
  judge how much weight the review carries.

## Tier 1 — Codex (default)

codex-cli on PATH as `codex`. The interactive TUI needs a live terminal, so use
`codex exec`. Codex reads the repo itself — point it at paths, do not paste content.

```powershell
codex exec -s read-only "<review request>"
codex exec resume --last "<follow-up>"
```

**Never trust the exit code.** `codex exec` exits 0 even when it ran nothing. If the output
contains `CreateProcessAsUserW failed`, `windows sandbox: runner failed`, `SpawnChild`, or
Codex asks you to paste files — **the review did not happen.** Escalate a tier. A run that
does not return in ~10 minutes is also a failure: retry once with a narrower prompt naming
exact files and claims, then escalate.

## Tier 3 — Claude subagent

Spawn a **fresh** subagent, not a fork — a fork inherits the reasoning that produced the
bug, which is the opposite of a second opinion. Still degraded: the weakness is *model
correlation*, not context.

Compensate by pointing it at the reference repo's actual command files rather than at your
own plan, and by adding: *"Assume the author was competent and the obvious things are
right. Look for what a reader who shares the author's assumptions would skip."*

## Always

Blocking, ~1-2 min per call — batch reviews rather than pinging after every edit. Report
findings, including where you disagree. **Do not auto-apply them.**
