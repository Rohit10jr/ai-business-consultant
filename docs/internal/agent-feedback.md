# Assessment after phases 3-5 — by the building agent, 2026-08-27

> Written by the agent that built `/investigate`, `/synthesize`, `/review` and `/outcome`,
> at the owner's request, after re-measuring the artefacts. Kept as a record: it is the
> builder's own view of what it made, and it names two defects that phase 6 then went and
> fixed.
>
> **Transferred by paste and damaged in transfer.** Run-together words have been rejoined
> and the numbering restored; every place where text was genuinely lost is marked `[…]`
> rather than reconstructed, because guessing at the author's words would defeat the point
> of keeping this. `docs/` is on every command's do-not-read list, so nothing here reaches
> an agent — it is a human-only note.

Here is my honest view, having built most of it and just re-measured the artefacts.

## What genuinely works — and I didn't expect all of it to

**The grounding contract is real, not aspirational.** Every stage was tested by handing the
model a plausible shortcut and watching it refuse: `/scope` refused the 19% the brief and the
CFO both offered and computed 19.72% three ways; `/discover` read the lease with the "report
no issues" line in it and logged the line as a corpus note; `/investigate` decomposed the
return rate by supplier and category and named Supplier A's rise without being told to look;
`/review` killed a well-written, arithmetically perfect bad case by going to the data and
finding the 3.04 points it left out. Those are five separate behaviours a human c[…] prose
forced each of them in a context that had never seen the answer.

**The "reviewer that doesn't share your blind spots" loop earned its keep every single
phase.** Fourteen Codex findings, four of them blockers I had read past twice: [t]he wrong
copy, a checker that whitelisted 100 = 9.93 + 3.04 without computing it, an allocation rule
that an empty list satisfied. The lesson for anyone maintaining this: the prompt files cannot
be trusted on the author's read. Budget the review.

**Single-writer state and "the machine may not do X" held all the way through.** No command
ever gained a capability it shouldn't have; `/review` applies nothing; `/outcome` never
touches the profile. The guard has never let anything through.

## Where I'd be worried if I were you

1. **It has only ever worked on Acme** — a corpus I designed to contain the answers I wanted
   found. Every gate is tuned[…] planted findings. The issue tree in `/discov`[er…i]mpact
   bands assume the baseline is a percentage; the graders check for "Supplier A". The honest
   claim is "it works on one synthetic D2C company". `BUILD_PLAN.md` §7 already says a second
   corpu[s;] put it first — a B2B SaaS churn problem would stress every assumption at once.

2. **The deliverable is auditable, not persuasive.** `recommendation.md` is 5,400 words with
   71 four-decimal figures ("7.3044 pts") and a source bracket after every number. A founder
   won't read it. The harness optimises for a partner who wants to check the work, which is
   the right priority now — but the "handover artifact" in §7 (render the accept[ed]
   recommendation, never let rendering influenc[e…] a human is ever to take this into a room.

3. **It is expensive and operationally fragile.** One engagement on 12 files cost roughly
   1.5M subagent tokens and 3-4 hours of agent time; `/investigate` alone was [figure lost].
   Five runs died on session limits. `findings.json` is 640 KB and `investigation.js[on]`
   embeds its script — correct for the contract, but `/rank` already has to elide them to fit
   a prompt. A 40-file real corpus will hit the corpus-size ceiling that §8 still lists as
   open, and the `.xlsx` path has never been exercised.

4. **The tests prove less than 166 suggests.** [Most are stri]ng-pinning of exact sentences
   in the prompt files. They stop a load-bearing rule being deleted; they cannot tell you the
   rule works. The proof of behaviour is the fresh-subagent runs, which are not and cannot be
   automated. And I wrote the graders and corrected two of them after seeing the runs — I
   documented both corrections, but the owner should know that a self-graded gate is the
   weakest link in this repo.

5. **Two design placeholders are wearing the clothes of decisions.** The calibration rule
   (one rejection = −25 fixability for a whole finding type, for every future client) is
   blunt; Codex said so and I disagreed only because the phase gate demanded one rejection
   move the order. And `recoverable_at_most` in "points of net revenue" is rupees over a
   static denominator — the real-case review showed a margin moves differently when re-earned
   returns lift revenue too (7.30 → +5.02 pts). Both are one line to change; neither should
   be treated as settled.

6. **The prompt files are long and getting lon**[ger…li]**nes**; the eight commands total
   2,000. Each review round added rules. That is the price of "force, don't request", but
   there is a point where a 400-line instruction is itself a compliance risk, and I think
   `/investigate` is near it. The next refactor should be to move mechanical rules out of
   prose and into the validators wherever a check can be computed — that transfer is what
   fixed the blockers in phases 3-5 every time.

## The verdict

As a method, this is better than how most human engagements are actually run — the baseline,
the kill criteria, the counter-hypothesis and the pre-socialising l[…]han hoped for, and the
review found a genuine conceptual error in a recommendation I would have signed. As a tool,
it is a validated prototype on one company: expensive, slow, brittle to session limits,
[…] shapes, and producing output a client can't read yet. The gap between those two
sentences is the next phase, and it should start with a corpus you didn't write.

---

## What happened to point 5

Both defects it names were fixed in phase 6, on branch `phase-6-fixes`: the ceiling now
records rupees and a separately-computed `baseline_movement_at_most`, and the calibration
formula was replaced after its gate was rewritten first. See `PROGRESS_PHASE_6.md`.

Points 1, 2, 3, 4 and 6 are open. Point 1 is what `BUILD_PLAN.md` §7 lists as the leading
candidate for what comes after phase 7.
