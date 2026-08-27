"""Rupee cost of the apparel return-rate rise at the Q2 FY26 run rate, and its size in
points of net revenue: excess returned lines x cost per returned line.

Cost per returned line follows the P&L definition: 150 pickup per returned order plus 40%
of unit cost written down (return_handling reconciles to pnl_monthly.csv on that rule).
Unit cost is the 2023 cost sheet; the P&L applies a small drift, so this is a floor.
"""
import csv
from pathlib import Path

CORPUS = Path("engagements/acme-review-test/corpus")
Q3_FY24 = {"2024-07", "2024-08", "2024-09"}
Q2_FY26 = {"2026-04", "2026-05", "2026-06"}


def month_of(d):
    if "/" in d:
        dd, mm, yy = d.split("/")
        return f"{yy}-{mm}"
    return d[:7]


with (CORPUS / "orders" / "orders_export.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
seen, lines = set(), []
for r in rows:
    k = (r["order_id"], r["line_no"])
    if k not in seen:
        seen.add(k)
        lines.append(r)
print(f"rows raw {len(rows)} -> deduplicated {len(lines)}")
with (CORPUS / "financials" / "cogs_by_sku.csv").open(encoding="utf-8", newline="") as f:
    cost = {r["sku"]: float(r["unit_cost_2023"]) for r in csv.DictReader(f)}
print(f"cost sheet rows {len(cost)}; join orders->cost on sku: {len(lines)} lines in, "
      f"{sum(r['sku'] in cost for r in lines)} matched")

apparel = [r for r in lines if r["category"] == "Apparel" and r["sku"] != "BND-001"]
q3 = [r for r in apparel if month_of(r["order_date"]) in Q3_FY24]
q2 = [r for r in apparel if month_of(r["order_date"]) in Q2_FY26]
rate0 = sum(r["returned"] == "Y" for r in q3) / len(q3)
rate1 = sum(r["returned"] == "Y" for r in q2) / len(q2)
rise = rate1 - rate0
excess = rise * len(q2)
returned_q2 = [r for r in q2 if r["returned"] == "Y"]
avg_cost = sum(150 + 0.4 * cost[r["sku"]] * int(r["qty"]) for r in returned_q2) / len(returned_q2)
saving = excess * avg_cost
print(f"apparel return rate {100*rate0:.2f}% -> {100*rate1:.2f}%, rise {100*rise:.2f} pts")
print(f"Q2 FY26 apparel lines {len(q2)}; excess returned lines at the old rate: {excess:.1f}")
print(f"average cost per returned apparel line Q2 FY26: {avg_cost:.2f} rupees")
print(f"cost of the rise at Q2 FY26 run rate: {saving:,.2f} rupees per quarter")

with (CORPUS / "financials" / "pnl_monthly.csv").open(encoding="utf-8", newline="") as f:
    pnl = {r["month"]: r for r in csv.DictReader(f)}
net_q2 = sum(float(pnl[m]["net_revenue"]) for m in sorted(Q2_FY26))
print(f"Q2 FY26 net revenue {net_q2:,.2f}; the rise costs {100*saving/net_q2:.2f} pts of net revenue")
