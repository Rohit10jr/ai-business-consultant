#!/usr/bin/env python3
"""Every figure in a recommendation traces to the investigation, the baseline, or shown
arithmetic over those - and every option ceiling traces to recoverable_at_most.

    python tools/check_recommendation.py engagements/<client>/recommendation.md \
        engagements/<client>/investigation.json engagements/<client>/scope.md

/synthesize runs no queries. Its numbers can therefore come from exactly three places:
a figure recorded in investigation.json (a claim's decomposition term, an evidence
value, a hypothesis size, an allocation half, recoverable_at_most), a figure in the
baseline line of scope.md, or arithmetic over those written out in the document's
`## Arithmetic` section as `<result> = <expression>` - and the expression is evaluated,
so the result has to be what the terms make it.

Option ceilings are held to a narrower rule: a `- Ceiling:` line's figure must be a
recoverable_at_most value, or an Arithmetic result whose every term is one. A finding's
magnitude is recorded in the investigation too, but it is not a ceiling, and a number
merely *existing* somewhere in the record does not make it one.

A number written like a figure - a decimal point, a %, pts, points, or a currency
mark - that matches none of those is reported. Years, quarter labels and bare
integers are left alone: the rule is aimed at "4.1 pts" arriving from nowhere, not
at "Q3 FY24" or "3 options".

Exit 0 when clean, 1 with a list otherwise. Stdlib only.
"""

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_findings import _numbers_in, _recorded_values, _matches_recorded  # noqa: E402

ARITHMETIC_HEADING = re.compile(r"^##\s+Arithmetic\s*$", re.M)
ARITHMETIC_LINE = re.compile(r"^\s*(?:[-*]\s*)?`?(.+?)\s*=\s*(.+?)`?\s*$")
CEILING_LINE = re.compile(r"^\s*[-*]\s*Ceiling:\s*(.+)$", re.M)
NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub,
                 ast.Mult, ast.Div, ast.USub)


def _evaluate(expression: str):
    """Value of a plain arithmetic expression over numbers, or None if it is not one."""
    text = (expression.replace("×", "*").replace("÷", "/").replace("−", "-")
            .replace(",", "").replace("₹", "").replace("Rs", ""))
    # Strip unit words so "9.93 pts + 3.04 pts" still evaluates.
    text = re.sub(r"[A-Za-z%_]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text or not re.fullmatch(r"[\d.\s+\-*/()]+", text):
        return None
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError:
        return None
    if any(not isinstance(node, ALLOWED_NODES) for node in ast.walk(tree)):
        return None
    try:
        return float(eval(compile(tree, "<arithmetic>", "eval"), {"__builtins__": {}}, {}))
    except (ZeroDivisionError, ValueError, TypeError):
        return None


def _decimals(token: str) -> int:
    return len(token.split(".")[1]) if "." in token else 0


def recorded_from(investigation: dict, scope_text: str) -> tuple[list[float], list[float]]:
    """(every recorded value, the recoverable_at_most values only)."""
    values: list[float] = []
    ceilings: list[float] = []
    for inv in investigation.get("investigations", {}).values():
        values += _recorded_values(inv)
        rec = inv.get("recoverable_at_most")
        if isinstance(rec, dict) and isinstance(rec.get("value"), (int, float)):
            ceilings.append(float(rec["value"]))
    baseline = next((l for l in scope_text.splitlines() if l.startswith("baseline:")), "")
    # Only figure-shaped numbers on the baseline line: "19.7%" yes, the 26 in "FY26" no.
    for tok in _numbers_in(baseline):
        try:
            values.append(float(tok))
        except ValueError:
            pass
    return values, ceilings


def arithmetic_results(text: str, recorded: list[float], ceilings: list[float]):
    """Evaluate the Arithmetic section.

    Returns (results, ceiling_results, errors): results whose every term is recorded and
    whose value is what the expression makes it; the subset whose every term is a
    recoverable_at_most value; and the errors found.
    """
    results, ceiling_results, errors = [], [], []
    m = ARITHMETIC_HEADING.search(text)
    if not m:
        return results, ceiling_results, errors
    section = text[m.end():]
    nxt = re.search(r"^##\s+", section, re.M)
    if nxt:
        section = section[: nxt.start()]
    for line in section.splitlines():
        lm = ARITHMETIC_LINE.match(line)
        if not lm or not NUMBER.search(lm.group(1)):
            continue
        lhs_tokens = [t.replace(",", "") for t in NUMBER.findall(lm.group(1))]
        term_tokens = [t.replace(",", "") for t in NUMBER.findall(lm.group(2))]
        bad = [t for t in term_tokens if not _matches_recorded(t, recorded + results)]
        if bad:
            errors.append(f"arithmetic line {line.strip()!r}: term(s) {bad} are not recorded figures")
            continue
        value = _evaluate(lm.group(2))
        if value is None:
            errors.append(f"arithmetic line {line.strip()!r}: right-hand side is not plain arithmetic")
            continue
        if len(lhs_tokens) != 1:
            errors.append(f"arithmetic line {line.strip()!r}: left-hand side must be one figure")
            continue
        lhs = float(lhs_tokens[0])
        tol = 0.5 * 10 ** (-_decimals(lhs_tokens[0])) + 1e-9
        if abs(lhs - value) > tol:
            errors.append(f"arithmetic line {line.strip()!r}: the terms make {value:.4f}, not {lhs_tokens[0]}")
            continue
        results.append(lhs)
        if all(_matches_recorded(t, ceilings + ceiling_results) for t in term_tokens):
            ceiling_results.append(lhs)
    return results, ceiling_results, errors


def check(text: str, investigation: dict, scope_text: str) -> list[str]:
    recorded, ceilings = recorded_from(investigation, scope_text)
    results, ceiling_results, errors = arithmetic_results(text, recorded, ceilings)
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
    for cm in CEILING_LINE.finditer(body):
        toks = [t.replace(",", "") for t in NUMBER.findall(cm.group(1))]
        if not toks:
            errors.append(f"ceiling line {cm.group(0).strip()!r} carries no figure")
            continue
        first = toks[0]
        if not _matches_recorded(first, ceilings + ceiling_results):
            errors.append(f"ceiling {first!r} is not a recoverable_at_most value or arithmetic over them only - "
                          "a finding's magnitude is recorded, but it is not a ceiling")
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
    print(f"check_recommendation: OK - every figure in {rec.name} traces to the investigation, the baseline, or shown arithmetic; every ceiling to recoverable_at_most")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
