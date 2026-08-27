"""Decompose the all-lines return-rate change Q3 FY24 -> Q2 FY26 by category:
rate effect per category at old shares, pure mix, interaction. Terms sum to the total."""
import csv
from collections import defaultdict
from pathlib import Path

ORDERS = Path("engagements/acme-review-test/corpus/orders/orders_export.csv")
Q3_FY24 = {"2024-07", "2024-08", "2024-09"}
Q2_FY26 = {"2026-04", "2026-05", "2026-06"}


def month_of(d):
    if "/" in d:
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


def stats(q):
    n, ret = defaultdict(int), defaultdict(int)
    for r in lines:
        if month_of(r["order_date"]) in q:
            n[r["category"]] += 1
            ret[r["category"]] += r["returned"] == "Y"
    total = sum(n.values())
    return {c: (n[c] / total, ret[c] / n[c]) for c in n}, sum(ret.values()) / total, total


s0, r0, n0 = stats(Q3_FY24)
s1, r1, n1 = stats(Q2_FY26)
print(f"all lines: {n0} -> {n1}; return rate {100*r0:.2f}% -> {100*r1:.2f}%, change {100*(r1-r0):+.2f} pts")
cats = sorted(set(s0) | set(s1))
total_terms = 0.0
for c in cats:
    sh0, rt0 = s0.get(c, (0, 0))
    sh1, rt1 = s1.get(c, (0, 0))
    eff = sh0 * (rt1 - rt0)
    total_terms += eff
    print(f"  rate {c:12s} share {100*sh0:5.1f}% -> {100*sh1:5.1f}%  rate {100*rt0:5.1f}% -> {100*rt1:5.1f}%  {100*eff:+.2f} pts")
mix = sum((s1.get(c, (0, 0))[0] - s0.get(c, (0, 0))[0]) * s0.get(c, (0, 0))[1] for c in cats)
inter = sum((s1.get(c, (0, 0))[0] - s0.get(c, (0, 0))[0]) * (s1.get(c, (0, 0))[1] - s0.get(c, (0, 0))[1]) for c in cats)
print(f"  mix                    {100*mix:+.2f} pts")
print(f"  interaction            {100*inter:+.2f} pts")
print(f"  sum of terms           {100*(total_terms+mix+inter):+.2f} pts")
