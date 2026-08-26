# The deliberately bad investigation

**Phase 4's `/review` gate needs something to kill.** This directory specifies it.

Hand-written, not generated — which is why it lives here and not in `acme-d2c/`, where
`tests/test_fixture_corpus.py` rebuilds every file and compares byte for byte.

## Why this exists

The phase plan says `/review`'s gate is *"reviewer kills a deliberately planted bad
inference"*. That gate cannot run against a good investigation, and it is circular against
one the same agent wrote: if `/investigate` does its job there is nothing to catch, and if
the author of `/review` also authored the flaw, catching it proves nothing.

So phase 4 has two separate tests:

| Test | Input | Passes when |
|---|---|---|
| Is `/investigate` sound? | the real Acme corpus, fresh session | it separates mix from rate on its own |
| Is `/review` adversarial? | **this fixture** | it kills the recommendation |

## The flaw: a correct arithmetic, a wrong conclusion

This is the important design constraint. **Every figure in the fixture must be individually
true and individually sourced.** If `/review` can kill it by noticing a missing `query_text`
or an unsourced number, the test has measured the grounding checker, not adversarial
reasoning — and phase 2 already proved the grounding checker works.

The flaw is entirely in the **inference**: it attributes the whole apparel return rise to
one supplier's quality, when a fifth of it belongs to a supplier it never mentions.

### The real decomposition

Apparel returns (excluding `BND-001`) went **11.85% → 26.60%** between Q3 FY24 and Q2 FY26,
a rise of **14.75 points**. Decomposed at the old shares:

| Component | Points | Share of the rise |
|---|---|---|
| Supplier B's own rate rise (11.4% → 59.0%) | **+9.93** | 67% |
| **Supplier A's own rate rise (12.0% → 15.8%)** | **+3.04** | **21%** |
| Interaction — B's share grew 20.9% → 25.0% while its rate exploded | +1.82 | 12% |
| Pure mix at old rates | −0.03 | ~0% |

Two things make this a good trap:

1. **Pure mix is almost exactly zero.** In Q3 FY24 the two suppliers returned at nearly the
   same rate (12.0% and 11.4%), so a share shift on its own moves nothing. An investigator
   who checks "did the mix change?", sees −0.03, and concludes "not mix, therefore all
   quality" has done the check and still got it wrong. The mix matters only through the
   *interaction* — and that is the term people forget.
2. **Supplier A is the tell.** Its rate rose too, on the same window, and it accounts for
   3.04 points that replacing Supplier B cannot recover. If the cause is platform-wide — a
   sizing convention, a size-chart change, a photography change — then B is a symptom and
   the recommendation is worth much less than it claims.

## What the fixture must claim

The investigation asserts, with correct arithmetic throughout:

- Apparel returns rose 14.75 points ✅ *true*
- Supplier B's return rate went 11.4% → 59.0% ✅ *true*
- Supplier B's share of apparel lines grew 20.9% → 25.0% ✅ *true*
- **"The rise is driven by Supplier B's quality"** ❌ *the flaw — 21% is Supplier A*
- **"Replacing Supplier B recovers the 14.75 points"** ❌ *at most ~11.75, and less if the
  cause is platform-wide*
- A rupee saving computed from the full 14.75 points ❌ *overstated by roughly a quarter*

It must **not** mention Supplier A's rate movement anywhere. Omission is the flaw; a fixture
that mentions it and dismisses it is testing something easier.

It should be *well written*. A sloppy fixture gets killed for being sloppy. This one should
read like competent work, because that is the kind that actually ships.

## What `/review` must catch

The gate passes only if the review names **both**:

1. **The counter-hypothesis was never stated.** The investigation asserts a cause without
   saying what else would produce the same numbers.
2. **Supplier A's 3.04 points.** The specific, checkable omission — not a general "have you
   considered other factors?", which any reviewer emits for free.

Naming only (1) is a **fail**. Generic scepticism is not adversarial review; the gate is
whether the reviewer went to the data and found the thing that was left out.

Credit if it also catches the overstated saving, but that follows from (2).

## Shape

Build the JSON against whatever schema phase 3 settles for
`engagements/<client>/investigation.json` — it does not exist yet, so it is not fixed here.
Illustrative only:

```json
{
  "client": "acme",
  "investigated_on": "YYYY-MM-DD",
  "finding": "return-rate-doubled",
  "claim": "Supplier B's product quality drove the apparel return rise",
  "evidence": [
    {"label": "apparel return rate Q3 FY24", "value": 11.85, "unit": "%",
     "query": "...", "query_text": "...", "rows_in": 0, "rows_out": 0},
    {"label": "Supplier B return rate Q2 FY26", "value": 59.0, "unit": "%", "...": "..."}
  ],
  "counter_hypotheses": [],
  "recommendation": "Replace Supplier B",
  "quantified_benefit": {"value": 14.75, "unit": "pts of apparel return rate"}
}
```

`counter_hypotheses: []` is the visible half of the flaw. The invisible half is that
Supplier A appears nowhere in `evidence`.

## Running the gate

`/review` must never read this directory — `fixtures/` is on every command's do-not-read
list, and for the same reason the corpus is copied rather than read in place. So:

```
copy  fixtures/bad-investigation/<file>.json
  to  engagements/acme-review-test/investigation.json
```

then run `/review acme-review-test` in a **fresh session**. `engagements/` is gitignored, so
the copy costs nothing and leaves no trace.

Record what the review said in `PROGRESS_PHASE_4.md`, verbatim, whether it passed or not.
