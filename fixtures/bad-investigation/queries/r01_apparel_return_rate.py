"""Apparel return rate (excluding BND-001), Q3 FY24 and Q2 FY26, de-duplicated lines."""
import csv
from pathlib import Path

ORDERS = Path("engagements/acme-review-test/corpus/orders/orders_export.csv")
Q3_FY24 = {"2024-07", "2024-08", "2024-09"}  # Jul-Sep 2024, inclusive
Q2_FY26 = {"2026-04", "2026-05", "2026-06"}  # Apr-Jun 2026, inclusive


def month_of(d):
    if "/" in d:  # March 2025 rows are DD/MM/YYYY
        dd, mm, yy = d.split("/")
        return f"{yy}-{mm}"
    return d[:7]


with ORDERS.open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
seen, lines = set(), []
for r in rows:
    k = (r["order_id"], r["line_no"])
    if k not in seen:
        seen.add(k)
        lines.append(r)
print(f"rows raw {len(rows)} -> deduplicated {len(lines)}")
apparel = [r for r in lines if r["category"] == "Apparel" and r["sku"] != "BND-001"]
for label, q in (("Q3 FY24", Q3_FY24), ("Q2 FY26", Q2_FY26)):
    sel = [r for r in apparel if month_of(r["order_date"]) in q]
    ret = sum(r["returned"] == "Y" for r in sel)
    print(f"{label}: apparel lines {len(sel)}, returned {ret}, rate {100*ret/len(sel):.2f}%")
