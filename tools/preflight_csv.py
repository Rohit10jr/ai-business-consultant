#!/usr/bin/env python3
"""Preflight a CSV before any figure is derived from it.

    python tools/preflight_csv.py <file.csv> [<file.csv> ...]
    python tools/preflight_csv.py --key order_id,line_no orders_export.csv

For each file, reports the things a query silently gets wrong if nobody
looked first:

- rows raw, rows after exact-duplicate removal, and the duplicates themselves
- if --key is given, rows whose key repeats (a duplicate order line with a
  different timestamp is not an exact duplicate, but it still double-counts)
- blank cells per column
- for every column that looks like a date, how many values are in each
  format - ISO `2025-03-04`, day-first `04/03/2025`, month `2025-03`, other

`/discover` runs this on every CSV it reads and records the before/after row
counts in findings.json. A figure computed from a file that was not
preflighted has no de-duplication count to show, and BUILD_PLAN.md section 3
does not allow it.

The tool reports; it does not rewrite anything. The de-duplicated view is
something each query builds for itself, and says so.

Stdlib only.
"""

import argparse
import csv
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

DATE_CLASSES = OrderedDict([
    ("iso YYYY-MM-DD", re.compile(r"^\d{4}-\d{2}-\d{2}$")),
    ("day-first DD/MM/YYYY", re.compile(r"^\d{2}/\d{2}/\d{4}$")),
    ("month YYYY-MM", re.compile(r"^\d{4}-\d{2}$")),
])
# A column is "date-like" when at least this share of its non-blank values
# match some date class. Below that it is reported as an ordinary column.
DATE_COLUMN_THRESHOLD = 0.5


def classify_date(value: str) -> str:
    for name, pattern in DATE_CLASSES.items():
        if pattern.match(value):
            return name
    return "other"


def preflight(path: Path, key: list[str] | None = None) -> dict:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [tuple(r) for r in reader]

    seen, duplicates, deduped = set(), [], []
    for i, row in enumerate(rows, start=2):  # line numbers as an editor shows them
        if row in seen:
            duplicates.append((i, row))
        else:
            seen.add(row)
            deduped.append(row)

    blanks = Counter()
    for row in deduped:
        for col, value in zip(header, row):
            if value == "":
                blanks[col] += 1

    date_columns = {}
    for idx, col in enumerate(header):
        values = [row[idx] for row in deduped if idx < len(row) and row[idx] != ""]
        if not values:
            continue
        counts = Counter(classify_date(v) for v in values)
        matched = sum(n for name, n in counts.items() if name != "other")
        if matched / len(values) >= DATE_COLUMN_THRESHOLD:
            date_columns[col] = dict(counts)

    # One --key serves several files on the command line; a file without those
    # columns simply gets no key check, and the report says so.
    key_applies = bool(key) and all(k in header for k in key)
    key_repeats = []
    if key_applies:
        idxs = [header.index(k) for k in key]
        counts = Counter(tuple(row[i] for i in idxs) for row in deduped)
        key_repeats = [(k, n) for k, n in counts.items() if n > 1]

    return {
        "file": str(path),
        "columns": header,
        "rows_raw": len(rows),
        "rows_deduplicated": len(deduped),
        "duplicate_rows": duplicates,
        "key": key if key_applies else [],
        "key_skipped": key if (key and not key_applies) else [],
        "key_repeats": key_repeats,
        "blank_cells": dict(blanks),
        "date_columns": date_columns,
    }


def render(report: dict) -> str:
    lines = [
        f"== {report['file']}",
        f"columns: {', '.join(report['columns'])}",
        f"rows raw: {report['rows_raw']}   rows after exact-duplicate removal: "
        f"{report['rows_deduplicated']}   duplicates: {len(report['duplicate_rows'])}",
    ]
    for line_no, row in report["duplicate_rows"][:10]:
        lines.append(f"  duplicate at line {line_no}: {','.join(row)[:120]}")
    if report["key"]:
        lines.append(f"key {'+'.join(report['key'])} repeats: {len(report['key_repeats'])}")
        for k, n in report["key_repeats"][:10]:
            lines.append(f"  {'+'.join(k)} x{n}")
    elif report["key_skipped"]:
        lines.append(f"key {'+'.join(report['key_skipped'])}: not in this file, key check skipped")
    if report["blank_cells"]:
        blanks = ", ".join(f"{c}={n}" for c, n in sorted(report["blank_cells"].items()))
        lines.append(f"blank cells: {blanks}")
    else:
        lines.append("blank cells: none")
    for col, counts in report["date_columns"].items():
        formats = ", ".join(f"{name}={n}" for name, n in counts.items())
        mixed = " MIXED FORMATS - normalise before grouping by date" if len(counts) > 1 else ""
        lines.append(f"date column {col}: {formats}{mixed}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--key", help="comma-separated columns that should be unique per row")
    args = parser.parse_args(argv[1:])
    key = args.key.split(",") if args.key else None
    for path in args.files:
        try:
            print(render(preflight(path, key)))
        except (OSError, ValueError, StopIteration) as exc:
            print(f"== {path}\nunreadable: {exc}")
            return 1
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
