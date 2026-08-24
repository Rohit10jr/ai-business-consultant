# Worked Example — one engagement, end to end

**What you are building, made concrete.** Read this before writing any command file.

The client is fictional and matches the synthetic fixture corpus specified in
`fixtures/README.md`. Every output shape below is the shape the real commands must produce.

---

**Client:** Acme, a D2C brand. ₹40 Cr revenue.
**Pain, as stated:** *"Revenue is up 20% but we're making less money."*

That sentence is not a question. Turning it into one is step one.

---

## `/setup` — the practice profile

Run once, not per engagement. Domains worked, frameworks used, past engagements and how
they landed. This is the durable profile the rest grounds against.

---

## The corpus

The client hands over what they have:

```
engagements/acme/corpus/
├── financials/     3 years P&L, monthly
├── orders/         order-level export, 400k rows
├── marketing/      ad spend by channel by month
├── ops/            warehouse contracts, shipping invoices
├── org/            headcount and org chart
└── interviews/     6 transcripts — CFO, head of ops, marketing lead
```

**They do not know what is in it.** That is why they hired someone. This is the whole
premise of the project: the corpus is the discovery surface.

---

## `/scope` — sharpen, and record the baseline

Vague pain becomes one answerable question:

> **"Why did contribution margin fall from 32% to 19% over 8 quarters, and which lever
> recovers the most?"**

```markdown
# Scope — Acme

question:   Why did contribution margin fall 32% -> 19% over 8 quarters,
            and which lever recovers the most?
baseline:   19.0% contribution margin, Q2 FY26
            source: financials/pnl_monthly.xlsx, derived — see scope_baseline.sql
done_when:  ranked levers with quantified margin impact, top 3 investigated
out_of_scope: pricing strategy (client ruled out), fundraising
```

**`/scope` refuses to proceed without `baseline`.** Not a warning — a stop. The client
wanting to get moving is exactly when this gets skipped, and without it nobody can prove
the engagement helped.

---

## `/discover` — read everything, surface candidates

Reads all 40 documents. Produces 14 candidate findings:

```
1.  Returns in Apparel: 12% -> 27%                    (orders)
2.  Meta CAC: ₹340 -> ₹710                            (marketing vs orders)
3.  Warehouse contract renewed at +40%/sqft           (ops/contracts)
4.  Discount codes stacking on 8% of orders           (orders)
5.  3 SKUs shipping at negative margin                (orders + COGS)
6.  Headcount +31% against revenue +20%               (org + financials)
7.  Free-shipping threshold unchanged since 2023,
    courier rates +22%                                (invoices + orders)
...7 more
```

The CFO already knew about #2 — it is in his transcript. **Nobody had noticed #4 or #7.**

That gap is the test of whether `/discover` is earning its place. If everything it surfaces
was already on the client's radar, the command is decoration.

**Output** — `engagements/acme/findings.json`:

```json
{
  "findings": {
    "apparel-returns": {
      "title": "Apparel return rate 12% -> 27%",
      "sources": ["orders/orders_export.csv"],
      "evidence": "returns_by_category.sql",
      "first_seen": "2026-08-24",
      "status": "new"
    }
  }
}
```

Same shape as the reference repo's `seen_jobs.json`: keyed dict, additive, one writer.

---

## `/rank` — score and triage

| # | Finding | Margin impact | Confidence | Fixable | Score |
|---|---|---|---|---|---|
| 1 | Apparel returns | −4.2 pts | high | medium | **88** |
| 7 | Shipping threshold | −3.1 pts | high | **easy** | **85** |
| 2 | Meta CAC | −2.8 pts | high | hard | 71 |
| 4 | Discount stacking | −1.4 pts | medium | easy | 64 |
| 6 | Headcount | −1.1 pts | low | political | 38 |

Fans out parallel scoring agents, ~5 findings each. Annotates `findings.json` **in place**
— adds `rank_score`, `rank_verdict`, `rank_date`. Never rewrites what `/discover` wrote.

**Veto conditions.** Anything the client put out of scope is vetoed regardless of score —
pricing here. The reference repo vetoes on location the same way.

Then it stops and asks which to pursue. It does not auto-chain into `/investigate`.

---

## `/investigate` — build the case

Top 3 only. Each figure carries its source.

> **Apparel returns**
>
> Return rate rose 12% → 27% between Q3 FY25 and Q2 FY26.
> **91% of the increase traces to one supplier's sizing.**
> 4,200 excess returns · ₹1.8 Cr reverse logistics and writedown · **−4.2 pts of margin**
>
> ```sql
> -- returns_by_supplier.sql, run 2026-08-24
> -- rows before join: 412,880   after: 412,880   (no fan-out)
> -- category sum reconciles to total returns: 38,204 = 38,204 ✓
> ```
>
> **Counter-hypothesis considered:** did this supplier's volume share grow over the same
> window? Checked — share moved 22% → 24%, which accounts for ~0.4 pts of the 4.2. The
> remainder is rate, not mix.

That last paragraph is not optional. A cause without its rejected alternatives is a guess
that happened to be written down.

---

## `/synthesize` → `/review`

`/synthesize` produces 2-3 options with trade-offs, a business case, and a risk register.

`/review` then attacks it in fresh context, before the client sees anything:

> *"You attribute 91% to one supplier but the reconciliation only covers Apparel. Returns
> in Footwear also rose 4 pts in the same window and are excluded without explanation. If
> the cause is a platform-wide sizing-chart change, replacing the supplier fixes nothing."*

Findings are **reported, never auto-applied.** The human decides.

This is the reference repo's `apply.md` reviewer with the nouns changed — fresh context,
content passed inline, a whitelist of readable files, a two-part output contract of
structured edits plus prose critique.

---

## `/outcome` — close the loop

```
accepted:  shipping threshold      implemented within 2 weeks
modified:  supplier                client asked for a pilot, not termination
rejected:  headcount               "not now"
pushback:  CFO wanted per-cohort figures, not aggregate
```

**Fast loop, three weeks.** Next engagement: `/synthesize` leads with cohort breakdowns for
finance audiences, and `/rank` down-weights headcount-shaped findings as politically dead.

The slow loop — did margin actually recover — takes 6-18 months and is contested. Record it
when it arrives, but do not wait for it.

---

## What this example is testing

Build against these, in order:

1. **`/scope` stops without a baseline.** Try to skip it; it must refuse.
2. **`/discover` surfaces something the client did not know.** #4 and #7 above. If it only
   finds what is already in the interview transcripts, it is not working.
3. **`/rank` puts an easy-to-fix medium finding above a hard-to-fix large one.** #7 over
   #2. A ranker that only weights magnitude will get this backwards.
4. **`/investigate` refuses to emit a figure it cannot source**, and always states the
   counter-hypothesis.
5. **`/review` catches the planted flaw.** The fixture corpus contains one deliberate trap
   — see `fixtures/README.md`. A reviewer that misses it is not adversarial enough.
