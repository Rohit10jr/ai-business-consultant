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

The rule, applied per finding type over every tracker row of that type:

```
adjustment = round(25 × (accepted − rejected) / rows), floored at −40, capped at +10
```

`modified` counts as neither. One rejection of one recommendation is −25: the practice
learns fast and forgets slowly, and the human sees the table before it takes effect.

| finding type | rows | accepted | modified | rejected | fixability adjustment |
|---|---|---|---|---|---|
| _none yet_ | | | | | |

## Lessons from past engagements

_None recorded yet._
