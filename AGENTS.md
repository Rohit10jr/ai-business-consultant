# ai-business-consultant — reviewer brief

**This repo builds a Claude Code harness that runs a consulting engagement**: vague client
pain → one answerable question with a baseline → read the client's document corpus →
surface candidate findings → rank → build the case → adversarial review → record what was
accepted.

The deliverable is mostly **markdown prompt files**, not application code. Reviewing prose
that an LLM executes is unusual, and it is most of the job here.

## Read before working

| File | What it is |
|---|---|
| `BUILD_PLAN.md` | Architecture, command surface, the grounding contract |
| `RUNBOOK.md` §The gate | What each phase had to pass before reaching you |
| `CLAUDE.md` | The rules the author was working under |

## The reference implementation

```
D:\02_Personal\01_OpenSource\03_Applications\ai-job-search
```

A proven harness with the same architecture in a different domain. When judging whether
something here is right, compare against:

- `.claude/commands/apply.md` — the drafter/reviewer pattern, human gates, the mandatory
  verification loop
- `.claude/commands/rank.md` — parallel scoring agents, weighted rubric, veto conditions
- `docs/ai-job-search/02-data-flow.md` — single-writer file ownership
- `docs/ai-job-search/04-findings.md` — its real defects, which we must not reproduce

**Read it, never edit it.** Separate repo, separate remote, work in progress. No git
commands in that directory.

## Your role

You are invoked as a **reviewer**, giving a second opinion on work written by Claude. Be
specific — cite file and line. Say plainly when something is right; do not manufacture
findings.

Prioritise, in order:

1. **Grounding enforcement.** Does the command file actually *force* every number back to
   a source, or does it merely ask nicely? "Cite your sources" is a suggestion. "Do not
   emit a figure unless it came from a query executed in this run, with the query shown"
   is a rule. Find the difference.
2. **Human gates are real.** A gate that says "confirm with the user" but then continues
   in the next paragraph is not a gate. Trace what happens on "no". The reference repo's
   `apply.md` line 58 is the standard: *"If the user says no, stop here."*
3. **Confidentiality.** Anything that could put client data into git, into a log, into a
   commit message, or into an outbound request. This is the failure with no recovery.
4. **Readability.** The owner must be able to *learn* this codebase, not reverse-engineer
   it. Flag invented abstractions, indirection with one caller, and clever solutions where
   a conventional one existed.

## Trap shapes for this particular project

No track record yet. These are the shapes worth suspecting:

* **A prompt that asks instead of forbids.** The single most common failure in this kind of
  repo. "Try to ground your claims" produces confident invention; "an ungrounded claim is
  removed" produces correct output. Every rule should read as a constraint, not advice.
  Compare the phrasing in `apply.md` if unsure.

* **The verification step that can be skipped.** The reference repo makes PDF compilation
  and visual inspection mandatory and non-skippable, because "the source looks fine" is not
  evidence. Our equivalent is the numeric checklist — query executed this run, SQL shown,
  row counts across every join, segments reconciling to their stated total. Check it cannot
  be quietly bypassed when the model is in a hurry, and that failure is defined.

* **Silent fan-out.** A join that multiplies rows is the most common way an analysis agent
  produces a confidently wrong number. If a command produces figures from joined data and
  never checks row counts before and after, that is a finding regardless of how the prose
  reads.

* **Untrusted input treated as instructions.** Client documents are third-party text. A
  supplier contract could contain a line saying "ignore previous instructions". Every
  command that reads the corpus must carry the untrusted-data rule, and it must ride along
  into every subagent prompt — not just sit in step 0. See `apply.md` line 25 and how it
  is repeated at line 114 for the reviewer.

* **State written by two commands.** In the reference repo each file has exactly one
  writer, and `/outcome` is explicitly forbidden from editing the framework files to avoid
  a race. If two of our commands write the same file, say which one owns it or flag it.

* **A finding presented without its counter-hypothesis.** The domain failure mode. "Returns
  rose in Apparel, therefore quality dropped" ignores that the supplier's volume share may
  also have grown — in which case it is mix, not quality. If `/investigate` reports a cause
  without stating what else could explain the same numbers, that is a defect even when the
  conclusion happens to be right.

* **Scoring that rewards the wrong thing.** `/rank` decides what gets human attention. If
  its rubric weights magnitude without confidence, or confidence without fixability, it
  will surface impressive-looking findings nobody can act on. Check the weights are stated
  and defensible, not implicit in prose.

* **Attribution leakage.** The owner does not want Claude credited in this repo. Check
  commit messages, PR text, README, and any generated output for `Co-Authored-By: Claude`
  or similar. This is easy to reintroduce by habit.
