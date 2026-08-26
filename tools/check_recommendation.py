#!/usr/bin/env python3
"""Every figure in a recommendation traces to the investigation, the baseline, or shown
arithmetic over those.

    python tools/check_recommendation.py engagements/<client>/recommendation.md \
        engagements/<client>/investigation.json engagements/<client>/scope.md

/synthesize runs no queries. Its numbers can therefore come from exactly three places:
a figure recorded in investigation.json (a claim's decomposition term, an evidence
value, a hypothesis size, an allocation half, recoverable_at_most), the baseline line
in scope.md, or arithmetic over those, written out in the document's `## Arithmetic`
section as `<result> = <term> <op> <term> ...` with every term itself traceable.

A number written like a figure - a decimal point, a %, pts, points, or a currency
mark - that matches none of those is reported. Years, quarter labels and bare
integers are left alone: the rule is aimed at "4.1 pts" arriving from nowhere, not
at "Q3 FY24" or "3 options".

Exit 0 when clean, 1 with a list otherwise. Stdlib only.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_findings import _numbers_in, _recorded_values, _matches_recorded  # noqa: E402

ARITHMETIC_HEADING = re.compile(r"^##\s+Arithmetic\s*$", re.M)
ARITHMETIC_LINE = re.compile(r"^\s*(?:[-*]\s*)?(?:`)?(.+?)\s*=\s*(.+?)(?:`)?\s*$")
NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def recorded_from(investigation: dict, scope_text: str) -> list[float]:
    values: list[float] = []
    for inv in investigation.get("investigations", {}).values():
        values += _recorded_values(inv)
    baseline = next((l for l in scope_text.splitlines() if l.startswith("baseline:")), "")
    for tok in NUMBER.findall(baseline):
        try:
            values.append(float(tok.replace(",", "")))
        except ValueError:
            pass
    return values


def arithmetic_results(text: str, recorded: list[float]) -> tuple[list[float], list[str]]:
    """Results of the Arithmetic section whose every term is recorded; plus errors."""
    results, errors = [], []
    m = ARITHMETIC_HEADING.search(text)
    if not m:
        return results, errors
    section = text[m.end():]
    nxt = re.search(r"^##\s+", section, re.M)
    if nxt:
        section = section[: nxt.start()]
    for line in section.splitlines():
        lm = ARITHMETIC_LINE.match(line)
        if not lm or not NUMBER.search(lm.group(1)):
            continue
        result_tokens = NUMBER.findall(lm.group(1))
        term_tokens = NUMBER.findall(lm.group(2))
        bad = [t for t in term_tokens if not _matches_recorded(t.replace(",", ""), recorded + results)]
        if bad:
            errors.append(f"arithmetic line {line.strip()!r}: term(s) {bad} are not recorded figures")
            continue
        for t in result_tokens:
            try:
                results.append(float(t.replace(",", "")))
            except ValueError:
                pass
    return results, errors


def check(text: str, investigation: dict, scope_text: str) -> list[str]:
    recorded = recorded_from(investigation, scope_text)
    results, errors = arithmetic_results(text, recorded)
    allowed = recorded + results
    body = text
    m = ARITHMETIC_HEADING.search(text)
    if m:  # the arithmetic section is checked line by line above
        nxt = re.search(r"^##\s+", text[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(text)
        body = text[: m.start()] + text[end:]
    seen = set()
    for tok in _numbers_in(body):
        if tok in seen:
            continue
        seen.add(tok)
        if not _matches_recorded(tok, allowed):
            errors.append(f"{tok!r} matches no figure in investigation.json, the baseline, or the Arithmetic section")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: check_recommendation.py <recommendation.md> <investigation.json> <scope.md>")
        return 2
    rec, inv, scope = (Path(a) for a in argv[1:])
    try:
        text = rec.read_text(encoding="utf-8")
        investigation = json.loads(inv.read_text(encoding="utf-8"))
        scope_text = scope.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"check_recommendation: unreadable input: {exc}")
        return 1
    errors = check(text, investigation, scope_text)
    if errors:
        print(f"check_recommendation: {len(errors)} figure(s) from nowhere in {rec}")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"check_recommendation: OK - every figure in {rec.name} traces to the investigation, the baseline, or shown arithmetic")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
