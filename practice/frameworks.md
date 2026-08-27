# Practice profile — frameworks

Written by `/setup` only. No client names, no client figures — this file is tracked in git.

<!-- /setup fills the sections below. /outcome never edits this file; it records to tracker.csv and /setup interprets. -->

## Diagnostic frameworks used

_None recorded yet._

## Ranking weights

Defaults `/rank` uses until `/setup` has calibrated them from recorded outcomes:

| Dimension | Weight |
|---|---|
| Margin impact | 40% |
| Confidence | 30% |
| Fixability | 30% |

## Finding types

The taxonomy `/rank` assigns to every finding and `/outcome` records against every outcome.
One of these, verbatim; `other` when none fits, with the reason in the rationale.

`returns-quality` · `supplier` · `channel-spend` · `discount-policy` · `shipping-logistics` ·
`unit-cost` · `fixed-cost` · `headcount` · `pricing` · `product-mix` · `other`

## Calibration

Fixability adjustments by finding type, in points, derived by `/setup frameworks` from
`practice/tracker.csv` and confirmed by the human before they are written here. `/rank`
adds the adjustment to each finding's fixability score before weighting, clamped to 0–100,
and records what it applied.

The rule, applied per finding type over every tracker row of that type (a row superseded
by a later correction row — one whose `notes` begins `supersedes <recorded_on>
<finding_slug>` — is excluded, and the correction counted once):

```
adjustment = round(25 × (accepted − rejected) / (rows + 2)), capped at +10
```

`modified` counts as neither. Rounding is half away from zero. The `+ 2` is shrinkage: two
phantom rows of no evidence sit under every real one, so a single outcome moves a finding
type by a third of the full weight and the weight arrives as rows accumulate. The full ±25
is the limit, reached only with dozens of one-sided rows. The cap at +10 is asymmetric on purpose: an
accepted recommendation is what the scoring already assumes, a rejected one is the signal.

**What it does, and why that is the right strength for a practice that has just started.**
One engagement, one afternoon, one rejection should not mark a whole kind of
recommendation down by a quarter of its fixability for every future client — that encodes
one client's politics as a type-wide prior on the strength of a single row. It should be
*visible*, so the human confirming this table sees one row and one adjustment together,
and it should grow only with evidence. Under this rule:

| rows | accepted | rejected | arithmetic | adjustment |
|---|---|---|---|---|
| 1 | 0 | 1 | 25 × (0 − 1) / 3 = −8.33 | −8 |
| 1 | 1 | 0 | 25 × (1 − 0) / 3 = +8.33 | +8 |
| 2 | 0 | 2 | 25 × (0 − 2) / 4 = −12.5 | −13 |
| 5 | 0 | 5 | 25 × (0 − 5) / 7 = −17.86 | −18 |
| 5 | 3 | 2 | 25 × (3 − 2) / 7 = +3.57 | +4 |
| 10 | 0 | 10 | 25 × (0 − 10) / 12 = −20.83 | −21 |

**Can a single row move a finding across a verdict band?** Yes, and that is accepted. One
row is ±8 fixability, which at the 30% weight is **±2.4 score points**; the verdict bands
(`pursue` 75+, `consider` 55–74) are labels on a continuous score, and a finding within 2.4
points of a boundary is a finding already on the boundary. Fresh scoring agents move raw
scores by ±1–3 between runs on their own, so a single row can tip a finding that was
already tipping, and not one that was not. `/rank` prints "Calibration moved: …" from one
run naming every finding whose position *or verdict band* changed, so a band crossing is
never silent even when the order stands.

| finding type | rows | accepted | modified | rejected | fixability adjustment |
|---|---|---|---|---|---|
| _none yet_ | | | | | |

*The rule above changed in phase 6 (from `25 × (a − r) / n`). The rows `/setup frameworks`
had written under the old rule (+10 supplier, −25 channel-spend, from two tracker rows) were
cleared rather than recomputed by hand, because `/setup` is this file's only writer. The
tracker still holds those rows; `/setup frameworks` regenerates the table from the file's
formula on its next run and the human confirms it then.*

## Lessons from past engagements

- A D2C apparel brand (under ₹5 Cr revenue), margin diagnosis, 2026: a supplier recommendation was accepted.
- A D2C apparel brand (under ₹5 Cr revenue), margin diagnosis, 2026: a channel-spend recommendation was rejected.
