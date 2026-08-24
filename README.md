# ai-business-consultant

A Claude Code harness that runs a consulting engagement end to end.

Take a vague client pain, sharpen it into one answerable question with a measurable
baseline, read the client's own document corpus, surface candidate findings they did not
know were there, rank them, build the case on the top few, have a second agent attack it,
and record what the client actually accepted.

**Status: greenfield.** Nothing is built yet. The plan is.

## What it is not

- Not a chatbot
- Not a report generator
- Not an autonomous agent — a human triggers every command
- Not a thing that talks to your client. It drafts; you present

## The pipeline

```
/setup       practice profile — domains, frameworks, past engagements
/scope       vague pain -> ONE answerable question + a recorded BASELINE
/discover    read the client corpus -> surface candidate findings
/rank        score findings: impact × confidence × fixability
/investigate build the case on the top N, with evidence shown
/synthesize  the "so what" -> recommendation with 2-3 options
/review      adversarial agent tries to kill the recommendation
/outcome     accepted / modified / rejected -> calibrates the next engagement
```

Nothing chains automatically. Each command finishes, reports, and suggests the next one.

## The idea

The client hands over forty files — P&L, order exports, contracts, interview transcripts —
and does not know what is in them. That is why they hired someone.

An agent that reads all of it and surfaces *"discount codes are stacking on 8% of orders"*
is doing real discovery. The client could not have listed that upfront, which is the test.

## Two rules that shape everything

**No number without a source.** Every figure traces to a document or a query executed in
that run, with the source shown. A figure that cannot be traced is removed, not softened.
An ungrounded line in a CV is embarrassing; an ungrounded figure in a business case is a
decision someone makes with money.

**Client data never enters git.** `engagements/` is gitignored from the first commit, before
any real corpus exists, and CI fails if anything under it is ever staged.

## Documentation

| File | What it is |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Agent brief — rules, stack, reviewer policy |
| [`BUILD_PLAN.md`](BUILD_PLAN.md) | Architecture, command surface, the grounding contract |
| [`RUNBOOK.md`](RUNBOOK.md) | Phase plan and the gate each phase must pass |
| [`AGENTS.md`](AGENTS.md) | Reviewer brief — what to check, and the trap shapes |

## Prior art

The architecture is lifted from a working harness in a different domain, not invented:

```
D:\02_Personal\01_OpenSource\03_Applications\ai-job-search
```

A job-application framework built on Claude Code — same shape, different nouns. Its
`docs/` folder holds an architecture write-up, a data-flow map, and a catalogue of its own
defects, all of which informed this plan. Read-only reference; see `CLAUDE.md`.

## License

TBD.
