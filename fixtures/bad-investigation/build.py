#!/usr/bin/env python3
"""Assemble the deliberately bad investigation from its query scripts.

    python fixtures/bad-investigation/build.py      # rewrites investigation.json here

Every figure below was produced by the script it names, run against a copy of the
acme-d2c corpus at engagements/acme-review-test/corpus/ (README.md, "Running the
gate"). The scripts are embedded verbatim so the record stands alone, exactly as
/investigate does. The arithmetic is correct throughout. The flaw is the inference:
the whole apparel return rise is attributed to Supplier B, the counter-hypothesis
list is empty, and Supplier A - whose own return rate rose in the same window and
accounts for a fifth of the rise - appears nowhere. See README.md for the numbers
/review must find.

Why a builder rather than a hand-typed JSON: the query texts are several thousand
characters each and must match the scripts byte for byte, or the first thing
/review finds is a transcription error rather than the omission.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUERIES = HERE / "queries"
# Where /review will find them once the JSON is copied into an engagement; the
# validator requires query paths under scratch/.
SCRATCH = "scratch/acme-review-test/investigate/return-rate-doubled"


def q(name: str) -> str:
    return (QUERIES / f"{name}.py").read_text(encoding="utf-8")


def figure(label, value, unit, period, name, rows_in, rows_out, join="none", **extra):
    fig = {"label": label, "value": value, "unit": unit, "period": period,
           "query": f"{SCRATCH}/{name}.py", "query_text": q(name),
           "rows_in": rows_in, "rows_out": rows_out, "join": join}
    fig.update(extra)
    return fig


Q3 = "Q3 FY24 (Jul-Sep 2024, inclusive)"
Q2 = "Q2 FY26 (Apr-Jun 2026, inclusive)"

record = {
    "client": "acme-review-test",
    "scope_question": "Which customer, product or channel segments no longer cover their own variable cost, and which of them should Acme stop serving or serve differently?",
    "baseline": "19.7% contribution margin, Q1 FY26 (Jan-Mar 2026, inclusive)",
    "investigations": {
        "return-rate-doubled": {
            "finding": "return-rate-doubled",
            "title": "Return rate doubled: 10.44% of lines in Q3 FY24 to 17.43% in Q2 FY26, driven by Apparel",
            "investigated_on": "2026-08-26",
            "reverified": [
                figure("all-lines return rate Q2 FY26", 17.43, "%", Q2, "q03_decompose_category", 5475, 608,
                       recorded=17.43, rederived=17.43, match=True),
                figure("apparel return rate Q2 FY26", 26.60, "%", Q2, "r01_apparel_return_rate", 5475, 312,
                       recorded=26.60, rederived=26.60, match=True),
            ],
            "claim": "Supplier B's product quality drove the apparel return rise: apparel returns went from 11.85% to 26.60% of lines (+14.75 pts) between Q3 FY24 and Q2 FY26 while Supplier B's own return rate went from 11.4% to 59.0%, so replacing Supplier B recovers the 14.75 pts.",
            "claim_strength": "established",
            "mechanism": "Supplier B's apparel is returned for sizing: 38 of its 46 Q2 FY26 returns cite sizing, against all 5 of its Q3 FY24 returns when its rate was 11.4%. The head of ops reports Supplier B changed its size block during 2025. Each returned line costs the pickup fee plus the write-down on unit cost that the P&L's return_handling line reconciles to, 431.88 rupees on average across Q2 FY26 apparel returns; at the Q2 FY26 run rate the rise of 14.75 pts is 46.0 excess returned lines a quarter, 19,880.79 rupees, or 2.94 pts of net revenue. Supplier B's share of apparel lines grew from 20.9% to 25.0% over the window, so its weight in the category is rising as well.",
            "preregistered_in": f"{SCRATCH}/hypotheses.json",
            "decompositions": [
                {
                    "metric": "return rate, all product lines", "components_by": "category",
                    "from": Q3, "to": Q2, "start": 10.44, "end": 17.43, "total_change": 7.00,
                    "terms": [
                        {"component": "Accessories", "kind": "rate", "share_start": 18.7, "share_end": 18.9, "rate_start": 6.5, "rate_end": 1.7, "points": -0.89},
                        {"component": "Apparel", "kind": "rate", "share_start": 58.5, "share_end": 58.4, "rate_start": 12.0, "rate_end": 23.7, "points": 6.80},
                        {"component": "Footwear", "kind": "rate", "share_start": 22.8, "share_end": 22.7, "rate_start": 9.6, "rate_end": 14.5, "points": 1.12},
                        {"component": "all", "kind": "mix", "points": -0.01},
                        {"component": "all", "kind": "interaction", "points": -0.03},
                    ],
                    "sum_of_terms": 6.99, "reconciles": True,
                    "query": f"{SCRATCH}/q03_decompose_category.py", "query_text": q("q03_decompose_category"),
                    "rows_in": 5475, "rows_out": 1020,
                }
            ],
            "counter_hypotheses": [],
            "allocation_dependence": "none — returned flag, line_value and sku are per line in orders/orders_export.csv; unit cost per sku in financials/cogs_by_sku.csv; net revenue per month in financials/pnl_monthly.csv. No shared cost is spread over lines.",
            "allocation_pairs": [],
            "evidence": [
                figure("apparel return rate Q3 FY24", 11.85, "%", Q3, "r01_apparel_return_rate", 5475, 211),
                figure("apparel return rate Q2 FY26", 26.60, "%", Q2, "r01_apparel_return_rate", 5475, 312),
                figure("Supplier B return rate Q3 FY24", 11.4, "%", Q3, "q01_supplier_b", 5475, 44),
                figure("Supplier B return rate Q2 FY26", 59.0, "%", Q2, "q01_supplier_b", 5475, 78),
                figure("Supplier B share of apparel lines Q3 FY24", 20.9, "%", Q3, "q01_supplier_b", 5475, 211),
                figure("Supplier B share of apparel lines Q2 FY26", 25.0, "%", Q2, "q01_supplier_b", 5475, 312),
                figure("apparel return-rate rise Q3 FY24 to Q2 FY26", 14.75, "pts", f"{Q3} to {Q2}", "q02_saving", 5475, 312),
                figure("excess returned apparel lines at the old rate, Q2 FY26", 46.0, "lines per quarter", Q2, "q02_saving", 5475, 312),
                figure("average cost per returned apparel line Q2 FY26", 431.88, "rupees", Q2, "q02_saving", 5475, 83, join="sku -> cogs_by_sku.csv (5475 in, 5475 matched)"),
                figure("cost of the rise at Q2 FY26 run rate", 19880.79, "rupees per quarter", Q2, "q02_saving", 5475, 83, join="sku -> cogs_by_sku.csv (5475 in, 5475 matched)"),
                figure("cost of the rise as a share of Q2 FY26 net revenue", 2.94, "pts of net revenue", Q2, "q02_saving", 5475, 83, join="sku -> cogs_by_sku.csv (5475 in, 5475 matched)"),
            ],
            "recoverable_at_most": figure("cost of the rise at Q2 FY26 run rate", 19880.79, "rupees per quarter", Q2, "q02_saving", 5475, 83,
                                          join="sku -> cogs_by_sku.csv (5475 in, 5475 matched)"),
            # True as arithmetic, wrong as attribution: the whole rise reversed, both terms
            # moving. The investigation claims Supplier B alone would deliver it.
            "baseline_movement_at_most": {
                "numerator_from": 137032.35, "numerator_to": 156913.14, "numerator_delta": 19880.79,
                "denominator_from": 675972.70, "denominator_to": 741498.79, "denominator_delta": 65526.09,
                "from": 20.27, "to": 21.16, "delta": 0.89, "unit": "pts of contribution margin", "period": Q2,
                "query": f"{SCRATCH}/q02_saving.py", "query_text": q("q02_saving"),
                "query_output": (
                    "rows raw 5476 -> deduplicated 5475\n"
                    "cost sheet rows 18; join orders->cost on sku: 5475 lines in, 5475 matched\n"
                    "apparel return rate 11.85% -> 26.60%, rise 14.75 pts\n"
                    "Q2 FY26 apparel lines 312; excess returned lines at the old rate: 46.0\n"
                    "average cost per returned apparel line Q2 FY26: 431.88 rupees\n"
                    "cost of the rise at Q2 FY26 run rate: 19,880.79 rupees per quarter\n"
                    "Q2 FY26 net revenue 675,972.70; the rise costs 2.94 pts of net revenue\n"
                    "margin with the fix: contribution 137,032.35 -> 156,913.14 (+19,880.79); "
                    "net revenue 675,972.70 -> 741,498.79 (+65,526.09); 20.27% -> 21.16% (+0.89 pts)\n"
                ),
                "rows_in": 5475, "rows_out": 83,
            },
            "open_questions": ["When exactly did Supplier B change its size block, and were size charts on the store updated with it?"],
            "status": "investigated",
        }
    },
}

out = HERE / "investigation.json"
out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {out.relative_to(HERE.parent.parent)} ({out.stat().st_size} bytes)")
