# Consulting Method — the domain this harness encodes

You are building a tool for a job you may not have done. This is that job.

Read it once before writing any command file. Every command in `BUILD_PLAN.md` §4 is a
step from the algorithm below, and the rules that look arbitrary are usually a hard-won
lesson from real engagements.

## What a consultant is

**Outside** the organization, engagement-based. Diagnoses a problem, recommends what to do
about it, then leaves.

A consultant optimizes for **quality of decision**.
A business analyst optimizes for **correctness of specification**.

That difference decides everything downstream. A BA elicits requirements and must not
pre-judge. A consultant writes the likely answer down *first* and spends the engagement
trying to kill it.

## What the work actually is

| Area | Work |
|---|---|
| **Scoping** | Define the question, timeline, access, fee, success criteria |
| **Structuring** | Issue trees, MECE decomposition, hypothesis formulation |
| **Research** | Interviews, financial analysis, market sizing, competitor benchmarking |
| **Analysis** | Cost and margin models, scenarios, org design, operating-model review |
| **Synthesis** | The "so what" — quantified, defensible, one page |
| **Recommendation** | Options with trade-offs, business case, risk register |
| **Roadmap** | Phased plan, owners, dependencies, quick wins vs structural change |
| **Delivery** | Steering-committee decks, workshops, sometimes implementation support |

**Deliverable:** a decision, with reasoning that survives challenge.

Note what is *not* on that list: writing reports. The report is a byproduct. The product is
a decision someone can defend to their board.

## The algorithm

```
1.  Client states a pain or asks a question
2.  Scope: sharpen it into ONE answerable question
    define timeline, data access, fee, and what "done" means
    RECORD THE BASELINE — needed at step 15
3.  Hypothesis-first: write candidate answers BEFORE analysing
4.  Structure: break the question into MECE branches (issue tree)
5.  Per branch, decide what evidence would kill or confirm it
6.  Collect: interviews, financials, market data, benchmarks
7.  Analyse each branch -> kill or confirm each hypothesis
        any hypothesis survive? -> no -> reframe -> go to 3
8.  Synthesize the "so what", quantified
9.  Build recommendation: 2-3 options, trade-offs, business case, risks
10. Pressure-test internally (partner review / red team)
        holds up? -> no -> go to 7
11. Socialise with key stakeholders BEFORE the formal readout
        (never surprise the client in the room)
12. Present
        accepted? -> no -> address objections -> go to 9
13. Roadmap: phases, owners, dependencies, quick wins first
14. (optional) implementation support
15. Measure impact against the step 2 baseline
```

## How the algorithm maps to commands

| Algorithm step | Command | Note |
|---|---|---|
| 2 | `/scope` | **Hard gate on the baseline.** Refuses to continue without one |
| 3, 4, 5 | `/discover` | Hypotheses become candidate findings from the corpus |
| 6, 7 | `/rank` then `/investigate` | Rank first so evidence-gathering is spent on what matters |
| 8, 9 | `/synthesize` | |
| 10 | `/review` | Adversarial agent. The partner review, automated |
| 11, 12, 13, 14 | **human only** | The machine never presents and never contacts anyone |
| 15 | `/outcome` | Against the step 2 baseline |

Steps 11-14 have no command deliberately. See `BUILD_PLAN.md` §5.

## Four craft concepts you need to encode

### MECE

**M**utually **E**xclusive, **C**ollectively **E**xhaustive. Breaking a question into
branches that do not overlap and do not leave gaps.

> *"Why did margin fall?"* → price / volume mix / unit cost / operating cost.
> Every rupee of the fall lands in exactly one branch.

**Most bad consulting is a bad issue tree.** If branches overlap you double-count; if they
leave a gap you miss the actual cause. When `/discover` groups findings, it should group
them MECE, and when it cannot, it should say so rather than pretending.

### Hypothesis-first

Write the candidate answers *before* looking at the data, then try to kill them. This
sounds backwards and is not. It stops you from wandering through 40 files hoping something
jumps out, and it makes disconfirmation cheap — you know in advance what evidence would
prove you wrong.

The trap it creates: confirmation bias. Hence step 5 — decide what would *kill* the
hypothesis, not what would support it.

### The counter-hypothesis

**The single most important rule for `/investigate`.**

Every proposed cause must state what else would produce the same numbers.

> *"Returns rose in Apparel, therefore supplier quality dropped."*

Incomplete. Did that supplier's **volume share** also grow? If it did, this is mix, not
quality, and the recommendation to replace them is wrong.

A cause without its rejected alternatives is not a finding. It is a guess that happened to
be written down. Bake this into the command file as a requirement, not a suggestion.

### Pre-socialising

Step 11, and the most important unwritten rule in the profession. You show the
recommendation to key stakeholders *individually, before* the formal readout.

Surprising a client in a steering committee kills recommendations that were analytically
correct. People defend positions in public that they would have discussed in private.

The harness cannot do this — it is human work — but `/synthesize` should **output in a form
that supports it**: a one-page summary per stakeholder concern, not only a single deck.

## Where the value actually is

Two steps are skipped constantly in real engagements, and forcing them is where this
harness beats a human, rather than merely matching one:

**Step 2's baseline.** Without a number recorded at the start, nobody can prove the
engagement helped. Consultants skip it because the client wants to get moving. `/scope`
refusing to proceed without it is a genuine improvement over the human process.

**Step 5's kill criteria.** Deciding what would disprove a hypothesis *before* gathering
evidence. Skipped because it feels like delay. It is the difference between analysis and
motivated reasoning.

## What the machine must never do

The reference implementation's best design decision is that its command named `/apply`
**cannot apply**. Ours:

1. **Never presents to the client.** Drafts; a human runs the room.
2. **Never contacts client stakeholders.** Interviews are human work.
3. **Never sends anything outward.** No email, Slack, or calendar — and it is wired to no
   tool that could.
4. **Never asserts a number without its source.**

The fourth matters more here than in most domains. An ungrounded line in a CV is
embarrassing. An ungrounded figure in a business case is a decision someone makes with
money.
