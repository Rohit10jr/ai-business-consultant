#!/usr/bin/env python3
"""Every figure in a recommendation traces to the investigation, the baseline, or shown
arithmetic over those; every ceiling is rupees from recoverable_at_most; every movement
of the baseline is a recomputed ratio, never a sum of movements.

    python tools/check_recommendation.py engagements/<client>/recommendation.md \
        engagements/<client>/investigation.json engagements/<client>/scope.md

/synthesize runs no queries. Its numbers can therefore come from exactly three places:
a figure recorded in investigation.json, a figure in the baseline line of scope.md, or
arithmetic over those written out in the document's `## Arithmetic` section as
`<result> = <expression>` - and the expression is evaluated, so the result has to be
what the terms make it.

Two lines in each option are held to narrower rules:

- `- Ceiling:` is rupees. Its first figure must be a recoverable_at_most value or an
  Arithmetic result whose every term is one, and the line may not carry a points or
  percent unit at all. A rupee delta over a frozen denominator is not a movement of the
  baseline, and a finding's magnitude - recorded too - is not a ceiling.
- `- Movement:` is points of the baseline, recomputed. Its figures must be a
  baseline_movement_at_most term (from, to, delta) or an Arithmetic result whose
  expression contains a division - a ratio rebuilt from numerator and denominator terms.
  A figure equal to the sum of two or more causes' movement deltas is rejected even if an
  Arithmetic line produced it: movements are ratios against a denominator each fix also
  moves, and they do not add.

Numbers written like figures - a decimal point, a %, pts, points, or a currency mark -
are checked. Years, quarter labels and bare integers are left alone.

Exit 0 when clean, 1 with a list otherwise. Stdlib only.
"""

import ast
import itertools
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_findings import _numbers_in, _recorded_values, _matches_recorded  # noqa: E402

ARITHMETIC_HEADING = re.compile(r"^##\s+Arithmetic\s*$", re.M)
ARITHMETIC_LINE = re.compile(r"^\s*(?:[-*]\s*)?`?(.+?)\s*=\s*(.+?)`?\s*$")
CEILING_LINE = re.compile(r"^\s*[-*]\s*Ceiling:\s*(.+)$", re.M)
MOVEMENT_LINE = re.compile(r"^\s*[-*]\s*Movement:\s*(.+)$", re.M)
POINTS_UNIT = re.compile(r"\bpts?\b|\bpoints?\b|%", re.I)
# Figures written as points of the baseline, wherever they appear in the prose. Two
# grades: a figure that names the baseline ("of net revenue", "of the baseline", "of
# contribution margin") must be a movement figure or a rebuilt ratio; a bare "pts" or
# "points" may also be any recorded figure - a decomposition term is points of a rate,
# and the claim sentence quotes it verbatim - but never a figure that exists only
# through the Arithmetic section.
BASELINE_POINTS = re.compile(
    r"(?<![\w.])([+−-]?\d[\d,]*(?:\.\d+)?)\s*(?:pts?|points?)\s+of\s+(?:the\s+baseline|net\s+revenue|revenue|"
    r"contribution\s+margin|margin|the\s+baseline\s+metric)\b"
    r"|(?<![\w.])([+−-]?\d[\d,]*(?:\.\d+)?)\s*%\s+of\s+(?:net\s+)?(?:revenue|the\s+baseline|contribution\s+margin)\b", re.I)
BARE_POINTS = re.compile(r"(?<![\w.])([+−-]?\d[\d,]*(?:\.\d+)?)\s*(?:pts?|points?)\b", re.I)
NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub,
                 ast.Mult, ast.Div, ast.USub)


def _evaluate(expression: str):
    """Value of a plain arithmetic expression over numbers, or None if it is not one."""
    text = (expression.replace("×", "*").replace("÷", "/").replace("−", "-")
            .replace(",", "").replace("₹", "").replace("Rs", ""))
    text = re.sub(r"[A-Za-z%_]+", " ", text)  # unit words
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


class Recorded:
    """What the investigation and the baseline line let a recommendation say."""

    def __init__(self):
        self.values: list[float] = []      # every recorded figure
        self.ceilings: list[float] = []    # recoverable_at_most, rupees
        self.movements: list[float] = []   # from / to / delta of each movement
        self.deltas: list[float] = []      # movement deltas only
        self.num_from: list[float] = []    # movement numerator_from
        self.num_delta: list[float] = []   # movement numerator_delta
        self.den_from: list[float] = []    # movement denominator_from
        self.den_delta: list[float] = []   # movement denominator_delta


def recorded_from(investigation: dict, scope_text: str) -> Recorded:
    r = Recorded()
    for inv in investigation.get("investigations", {}).values():
        r.values += _recorded_values(inv)
        rec = inv.get("recoverable_at_most")
        if isinstance(rec, dict) and isinstance(rec.get("value"), (int, float)):
            r.ceilings.append(float(rec["value"]))
        mov = inv.get("baseline_movement_at_most")
        if isinstance(mov, dict):
            for k in ("from", "to", "delta"):
                if isinstance(mov.get(k), (int, float)):
                    r.movements.append(float(mov[k]))
            if isinstance(mov.get("delta"), (int, float)):
                r.deltas.append(float(mov["delta"]))
            for key, bucket in (("numerator_from", r.num_from), ("numerator_delta", r.num_delta),
                                ("denominator_from", r.den_from), ("denominator_delta", r.den_delta)):
                if isinstance(mov.get(key), (int, float)):
                    bucket.append(float(mov[key]))
    baseline = next((l for l in scope_text.splitlines() if l.startswith("baseline:")), "")
    for tok in _numbers_in(baseline):  # "19.7%" yes, the 26 in "FY26" no
        try:
            r.values.append(float(tok))
        except ValueError:
            pass
    return r


def _is_recomputed_ratio(expression: str, r: Recorded) -> bool:
    """A movement-grade ratio is rebuilt from the baseline's own terms: a numerator that
    starts from a recorded numerator_from plus at least one numerator_delta, over a
    denominator that starts from a recorded denominator_from plus at least one
    denominator_delta. `100 × 46,121.67 / 631,425.85` - a delta over the frozen
    denominator - has no numerator_from and no denominator_delta, and is refused."""
    text = expression.replace("÷", "/")
    depth, split = 0, -1
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "/" and depth == 0:
            split = i
            break
    if split < 0:
        return False
    left = [t.replace(",", "") for t in NUMBER.findall(text[:split])]
    right = [t.replace(",", "") for t in NUMBER.findall(text[split + 1:])]
    has = lambda toks, bucket: any(_matches_recorded(t, bucket) for t in toks)  # noqa: E731
    return (has(left, r.num_from) and has(left, r.num_delta)
            and has(right, r.den_from) and has(right, r.den_delta))


def _sums_of_deltas(deltas: list[float]) -> list[float]:
    sums = []
    for r in range(2, len(deltas) + 1):
        for combo in itertools.combinations(deltas, r):
            sums.append(sum(combo))
    return sums


def arithmetic_results(text: str, r: Recorded):
    """Evaluate the Arithmetic section.

    Returns (results, ceiling_results, ratio_results, errors): results whose every term is
    recorded and whose value is what the expression makes it; the subset whose every term
    is a recoverable_at_most value; the subset that is movement-grade - a ratio rebuilt
    from the baseline's own terms, or arithmetic whose every term is already a movement
    figure; and the errors found.
    """
    recorded, ceilings, movements = r.values, r.ceilings, r.movements
    results, ceiling_results, ratio_results, errors = [], [], [], []
    m = ARITHMETIC_HEADING.search(text)
    if not m:
        return results, ceiling_results, ratio_results, errors
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
        is_ratio = "/" in lm.group(2) or "÷" in lm.group(2)
        # The one constant a recomputed ratio needs: the percent scaler. Nothing else
        # unrecorded may appear as a term - a bare multiplier would launder a figure.
        bad = [t for t in term_tokens
               if not (is_ratio and t == "100") and not _matches_recorded(t, recorded + results)]
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
        # Movement-grade: a ratio rebuilt from the baseline's own terms, or arithmetic whose
        # every term is already a movement figure (a delta as `to − from`). A sum of deltas
        # also lands here and is caught by the delta-sum rule in check(). A division that
        # is not rebuilt from both terms - the frozen-denominator bug - is plain arithmetic:
        # its result may appear as a figure, never as a movement.
        if (is_ratio and _is_recomputed_ratio(lm.group(2), r)) or \
                (not is_ratio and all(_matches_recorded(t, movements + ratio_results) for t in term_tokens)):
            ratio_results.append(lhs)
    return results, ceiling_results, ratio_results, errors


def check(text: str, investigation: dict, scope_text: str) -> list[str]:
    r = recorded_from(investigation, scope_text)
    recorded, ceilings, movements, deltas = r.values, r.ceilings, r.movements, r.deltas
    results, ceiling_results, ratio_results, errors = arithmetic_results(text, r)
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
        line = cm.group(0).strip()
        toks = [t.replace(",", "") for t in NUMBER.findall(cm.group(1))]
        if not toks:
            errors.append(f"ceiling line {line!r} carries no figure")
            continue
        if POINTS_UNIT.search(cm.group(1)):
            errors.append(f"ceiling line {line!r} is stated in points or percent - a ceiling is rupees; "
                          "the baseline's movement goes on the Movement line, from baseline_movement_at_most")
        if not _matches_recorded(toks[0], ceilings + ceiling_results):
            errors.append(f"ceiling {toks[0]!r} is not a recoverable_at_most value or arithmetic over them only - "
                          "a finding's magnitude is recorded, but it is not a ceiling")

    # Points of the baseline anywhere in the prose - not only on Ceiling and Movement
    # lines - must be a movement figure or a rebuilt ratio. A rate in % (a return rate,
    # a share) is ordinary evidence; "pts", "points", and "% of revenue / of the
    # baseline / of contribution margin" are claims about the baseline.
    movement_grade = movements + ratio_results
    for pm in BASELINE_POINTS.finditer(body):
        tok = (pm.group(1) or pm.group(2)).replace(",", "").lstrip("+−-")
        if not _matches_recorded(tok, movement_grade):
            errors.append(f"{tok!r} is stated as points of the baseline ({pm.group(0).strip()!r}) but is not a "
                          "baseline_movement_at_most figure or a ratio rebuilt from both terms")
    for pm in BARE_POINTS.finditer(body):
        tok = pm.group(1).replace(",", "").lstrip("+−-")
        if not _matches_recorded(tok, recorded + movement_grade):
            errors.append(f"{tok!r} pts ({pm.group(0).strip()!r}) is neither a recorded figure nor a movement - "
                          "a points figure that exists only through the Arithmetic section")

    delta_sums = _sums_of_deltas(deltas)
    for mm in MOVEMENT_LINE.finditer(body):
        line = mm.group(0).strip()
        toks = [t.replace(",", "") for t in NUMBER.findall(mm.group(1))]
        figures = [t for t in toks if "." in t or POINTS_UNIT.search(mm.group(1))]
        if not figures:
            errors.append(f"movement line {line!r} carries no figure")
            continue
        for t in figures:
            if _matches_recorded(t, delta_sums):
                errors.append(f"movement {t!r} in {line!r} equals the sum of two or more causes' movement deltas - "
                              "movements are ratios and do not add; recompute the option jointly from numerator and denominator")
            elif not _matches_recorded(t, movements + ratio_results):
                errors.append(f"movement {t!r} in {line!r} is not a baseline_movement_at_most figure or a ratio "
                              "recomputed in the Arithmetic section")
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
    print(f"check_recommendation: OK - every figure in {rec.name} traces to the investigation, the baseline, or shown arithmetic; "
          "every ceiling is rupees from recoverable_at_most; every movement is a recomputed ratio")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
