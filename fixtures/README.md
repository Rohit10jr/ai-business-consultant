# Fixtures — the synthetic corpus

**Build this in phase 0.** Phases 2-5 cannot be gated without it, and a real client corpus
must never be used for testing.

Everything here is fictional and **tracked in git** — the one negation in `.gitignore`.
Nothing real ever goes in this directory.

## `acme-d2c/` — the reference corpus

A fictional D2C brand with a margin problem. ~20 files. Matches
[`../docs/WORKED_EXAMPLE.md`](../docs/WORKED_EXAMPLE.md) exactly, so that document doubles
as the expected-output spec.

```
acme-d2c/
├── brief.md                     the client's vague pain, in their words
├── financials/
│   ├── pnl_monthly.csv          36 months, contribution margin 32% -> 19%
│   └── cogs_by_sku.csv
├── orders/
│   └── orders_export.csv        ~5,000 rows (not 400k — keep it testable)
├── marketing/
│   └── spend_by_channel.csv     monthly, by channel
├── ops/
│   ├── warehouse_contract.md    renewed at +40%/sqft
│   └── courier_invoices.csv     rates +22% since 2023
├── org/
│   └── headcount.csv            +31% against revenue +20%
└── interviews/
    ├── cfo.md                   mentions Meta CAC — the already-known finding
    ├── head_of_ops.md
    └── marketing_lead.md
```

## What must be planted

The corpus is a test, so it needs known answers at known difficulty.

### Three findings, graded

| Difficulty | Finding | Discoverable from |
|---|---|---|
| **Easy** | Meta CAC ₹340 → ₹710 | Stated outright in `interviews/cfo.md` |
| **Medium** | Apparel returns 12% → 27% | One aggregation over `orders_export.csv` |
| **Hard** | Free-shipping threshold unchanged while courier rates rose 22% | Requires joining `courier_invoices.csv` to order values — in no single file |

**The hard one is the real test.** If `/discover` only surfaces the easy finding, it is
reading interview transcripts and calling it discovery. The point of the whole project is
finding what the client did not already know.

### One red herring

A finding that looks large and is not real. **Suggested:** a SKU with apparently negative
margin that is actually a bundle component — its revenue is booked against the parent SKU.
Anything ranking it highly has not checked how bundles are recorded.

### One planted flaw for `/review`

Phase 4's gate requires `/review` to catch a deliberately bad inference. **Suggested:** make
the Apparel returns rise coincide with that supplier's volume share growing 22% → 24%, so a
naive `/investigate` attributes the whole 4.2 points to quality when ~0.4 is mix.

`/review` must catch it. If it does not, the reviewer prompt is not adversarial enough.

## Rules for building it

1. **Internally consistent.** The P&L must reconcile to the order export. If they disagree,
   every downstream test is measuring the wrong thing.
2. **Small enough to read.** ~5,000 order rows, not 400,000. You must be able to verify the
   expected answer by hand.
3. **Realistically messy.** Some blank cells, one inconsistent date format, a duplicated
   order id. A corpus that is too clean tests nothing — real ones never are.
4. **Answers recorded separately.** Put the expected findings, their magnitudes, and the
   red herring in `acme-d2c/EXPECTED.md`. Tests assert against that file; `/discover` must
   never read it.
5. **Obviously fake names.** "Acme", "Supplier A". Nothing that could be mistaken for a
   real company.

## Adding more

One corpus is enough for phases 0-5. A second one — different industry, different failure
mode — is the right way to check the commands are not overfitted to Acme. That is a phase 6
concern, not now.
