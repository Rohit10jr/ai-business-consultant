#!/usr/bin/env python3
"""Validate a findings.json against the grounding contract, structurally.

    python tools/validate_findings.py engagements/<client>/findings.json

This cannot tell whether a figure is *right*. It can tell whether the record
carries what BUILD_PLAN.md section 3 says every figure must carry - the query
that produced it, row counts, the checks - so that a human can go and see. A
findings.json that fails here was written by a /discover that skipped a step,
whatever the prose of its report says.

Checks:
- top-level keys present; every CSV in `preflight` has raw and de-duplicated
  row counts, with de-duplicated <= raw
- every finding has every required key; `checks` are all true (or, for the
  string-valued ones, non-empty and not a hedge)
- every figure has a non-empty `query_text`, integer `rows_in`/`rows_out`, and
  a `query` path under scratch/
- `derivation_kind: stated` findings say so in their title and have a
  second derivation of "not possible"
- `second_derivation` uses the allowed vocabulary, and a "partial" names which
  part agrees and what the rest depends on - a bare "partial" is the same
  escape hatch "not possible" would be without its files named
- every finding carries `magnitude.baseline_metric`: its size in the baseline's
  own unit, or "not derivable" with a reason. `/rank` scores impact from this,
  and a finding that omits it silently ranks as if it were small
- no rank_* keys unless `status` is `ranked` or `vetoed` (i.e. /rank wrote them)
- a vetoed finding names a recognised veto slug *and* a human-readable reason,
  and carries no score - the slug is for filtering, the sentence is for the
  person reading the file without the rulebook to hand

Exit 0 when clean, 1 with a list otherwise. Stdlib only.
"""

import json
import re
import sys
from pathlib import Path

REQUIRED_TOP = {"client", "discovered_on", "scope_question", "baseline", "out_of_scope",
                "preflight", "issue_tree", "findings", "not_recorded", "corpus_notes"}
REQUIRED_FINDING = {"title", "branch", "magnitude", "figures", "sources", "derivation_kind",
                    "known_to_client", "checks", "mix_at_boundaries", "first_seen", "status"}
REQUIRED_FIGURE = {"label", "value", "unit", "period", "query", "query_text", "rows_in",
                   "rows_out", "join"}
BOOL_CHECKS = ("sourced", "deduplicated", "dates_normalised", "joins_counted")
TEXT_CHECKS = ("reconciles", "second_derivation", "zero_price_lines_explained")
# Words that mean a check was talked around rather than passed.
HEDGES = ("roughly", "approximately", "about ", "probably", "assumed", "estimated", "tbd")

# The only three answers to "did you derive it a second way?". Anything else is a
# sentence that reads like a check and is not one.
SECOND_DERIVATION_START = ("agrees", "partial", "not possible")

# /rank Step 1. The slug is filterable; the sentence beside it is what a human reads.
VETO_SLUGS = ("out-of-scope", "ungrounded", "restates-the-baseline")


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_TOP - set(data)
    if missing:
        errors.append(f"top level: missing keys {sorted(missing)}")
        return errors

    for path, pre in data["preflight"].items():
        raw, dedup = pre.get("rows_raw"), pre.get("rows_deduplicated")
        if not isinstance(raw, int) or not isinstance(dedup, int):
            errors.append(f"preflight {path}: rows_raw and rows_deduplicated must be integers")
        elif dedup > raw:
            errors.append(f"preflight {path}: rows_deduplicated {dedup} > rows_raw {raw}")

    for slug, f in data["findings"].items():
        where = f"finding {slug}"
        miss = REQUIRED_FINDING - set(f)
        if miss:
            errors.append(f"{where}: missing keys {sorted(miss)}")
            continue
        if not f["figures"]:
            errors.append(f"{where}: no figures - a finding without a figure is a remark")
        for i, fig in enumerate(f["figures"]):
            fw = f"{where} figure[{i}]"
            miss = REQUIRED_FIGURE - set(fig)
            if miss:
                errors.append(f"{fw}: missing keys {sorted(miss)}")
                continue
            if not str(fig["query_text"]).strip():
                errors.append(f"{fw}: empty query_text - the figure has no shown query")
            if not str(fig["query"]).replace("\\", "/").startswith("scratch/"):
                errors.append(f"{fw}: query path must be under scratch/, got {fig['query']!r}")
            for k in ("rows_in", "rows_out"):
                if not isinstance(fig[k], int):
                    errors.append(f"{fw}: {k} must be an integer, got {fig[k]!r}")
        checks = f["checks"]
        for k in BOOL_CHECKS:
            if checks.get(k) is not True:
                errors.append(f"{where}: checks.{k} is not true - the finding should not have been recorded")
        for k in TEXT_CHECKS:
            v = str(checks.get(k, "")).strip()
            if not v:
                errors.append(f"{where}: checks.{k} is empty")
            elif any(h in v.lower() for h in HEDGES):
                errors.append(f"{where}: checks.{k} hedges ({v!r}) - a check passes or the finding is removed")
        second = str(checks.get("second_derivation", "")).strip()
        if second and not second.lower().startswith(SECOND_DERIVATION_START):
            errors.append(
                f"{where}: checks.second_derivation must begin with "
                f"{' / '.join(SECOND_DERIVATION_START)} - got {second!r}"
            )
        if second.lower().startswith("partial") and ";" not in second:
            errors.append(
                f"{where}: checks.second_derivation is 'partial' without a ';' - name which part "
                "agrees and what the rest depends on. A bare 'partial' is the same escape hatch "
                "'not possible' would be without its files named"
            )
        magnitude = f.get("magnitude")
        if isinstance(magnitude, dict):
            baseline = str(magnitude.get("baseline_metric", "")).strip()
            if not baseline:
                errors.append(
                    f"{where}: magnitude.baseline_metric missing - give the size in the baseline's "
                    "own unit with the query that produced it, or 'not derivable - <why>'. Without "
                    "it /rank parks the finding as unquantified and it sinks whatever it is worth"
                )
            elif baseline.lower().startswith("not derivable") and not baseline[13:].strip(" -\u2014:"):
                errors.append(
                    f"{where}: magnitude.baseline_metric says 'not derivable' with no reason - say "
                    "why, and what file would be needed"
                )
        if f["derivation_kind"] not in ("joined", "single-file", "stated"):
            errors.append(f"{where}: derivation_kind {f['derivation_kind']!r} not recognised")
        if f["derivation_kind"] == "stated":
            if "stated" not in f["title"].lower():
                errors.append(f"{where}: stated-only finding must say so in its title")
            if "not possible" not in str(checks.get("second_derivation", "")):
                errors.append(f"{where}: stated-only finding cannot claim a second derivation")
        if f["status"] == "vetoed":
            slug = str(f.get("rank_veto", "")).strip()
            if slug not in VETO_SLUGS:
                errors.append(
                    f"{where}: rank_veto {slug!r} is not one of {', '.join(VETO_SLUGS)}"
                )
            reason = str(f.get("rank_veto_reason", "")).strip()
            if not reason:
                errors.append(
                    f"{where}: vetoed with no rank_veto_reason - the slug says which rule "
                    "fired, not why this finding tripped it. Name the specific thing"
                )
            elif reason.strip(" .").lower().replace(" ", "-") in VETO_SLUGS:
                errors.append(
                    f"{where}: rank_veto_reason {reason!r} restates the rule instead of "
                    "giving the reason. Name what this finding actually did"
                )
            if f.get("rank_score") is not None:
                errors.append(f"{where}: vetoed findings are not scored, but rank_score is set")
        ranked = any(k.startswith("rank_") for k in f)
        if ranked and f["status"] not in ("ranked", "vetoed"):
            errors.append(f"{where}: has rank_* keys but status is {f['status']!r}")
        if not ranked and f["status"] in ("ranked", "vetoed"):
            errors.append(f"{where}: status {f['status']!r} but no rank_* keys")
    return errors


# --- investigation.json ----------------------------------------------------
# /investigate's output succeeds findings.json and is held to the same contract
# plus the counter-hypothesis rule. Same file, same CLI: the two records are
# told apart by their top-level key.

REQUIRED_INVESTIGATION = {"finding", "title", "investigated_on", "reverified", "claim",
                          "claim_strength", "mechanism", "preregistered_in", "decompositions",
                          "counter_hypotheses", "allocation_dependence", "allocation_pairs",
                          "evidence", "recoverable_at_most", "baseline_movement_at_most",
                          "open_questions", "status"}
# recoverable_at_most is rupees (or another currency) and nothing else. Points of the
# baseline live only in baseline_movement_at_most, whose query shows both terms move.
CURRENCY_MARKS = ("₹", "rs", "rupee", "inr", "$", "usd", "€", "eur", "£", "gbp")
POINTS_MARKS = ("pt", "point", "%", "margin", "percent")
MOVEMENT_KEYS = {"numerator_from", "numerator_to", "numerator_delta", "denominator_from",
                 "denominator_to", "denominator_delta", "from", "to", "delta", "unit", "period",
                 "query_output"}
MOVEMENT_NUMERIC_KEYS = MOVEMENT_KEYS - {"unit", "period", "query_output"}
RATIO_TOLERANCE = 0.011  # two-decimal points of the baseline
# A unit that claims points of the baseline metric. Allowed only on
# baseline_movement_at_most; on any other figure it is the frozen-denominator bug
# wearing a label. "pts of return rate" (a decomposition term) is not this.
BASELINE_POINTS_UNIT = re.compile(
    r"(pt|point)s?\s+of\s+(the\s+baseline|contribution\s+margin|margin|the\s+baseline\s+metric)|"
    r"%\s+of\s+(the\s+baseline|contribution\s+margin)", re.I)


def _printed(value: float, output: str) -> bool:
    """Does the query's printed output carry this number, with or without thousands
    separators, at two decimals or as written?"""
    candidates = {f"{value:,.2f}", f"{value:.2f}", f"{value:,.1f}", f"{value:.1f}", f"{value:g}", str(value)}
    return any(c in output for c in candidates)


def _pairs_covered(overlaps: list, slugs: list[str]) -> list[str]:
    seen = {frozenset((o.get("a"), o.get("b"))) for o in overlaps if isinstance(o, dict)}
    missing = []
    for i, a in enumerate(slugs):
        for b in slugs[i + 1:]:
            if frozenset((a, b)) not in seen:
                missing.append(f"{a} / {b}")
    return missing
CLAIM_STRENGTHS = ("established", "partial", "unsupported")
# Every investigation must have looked at these three shapes of alternative, plus
# the cause it is arguing for. Only `mix` may be absent, and only for a finding
# that is not a rate - a common cause and a recording change can affect anything.
REQUIRED_CLASSES = ("mix", "common-cause", "measurement", "named")
MAY_BE_NOT_APPLICABLE = ("mix",)
FIELD_CLASSES = ("mix", "common-cause")  # these name the field Step 3 decomposes by
HYPOTHESIS_STATUSES = ("ruled_out", "supported", "not_ruled_out", "not_applicable")
# Words that mean a kill query was not run.
SOFT_STATUS_WORDS = ("unlikely", "probably", "considered", "seems")
DECOMPOSITION_TOLERANCE = 0.011  # two-decimal rounding on each term
FIGURE_KEYS = {"query", "query_text", "rows_in", "rows_out"}

# A number in the claim or mechanism counts as a figure - and must be recorded -
# when it is written like one: a decimal point, a percent, points, or a currency
# mark. Years, quarter labels and round thresholds quoted from the corpus are
# left alone; the rule is aimed at the "4.1 pts" that arrived from nowhere.
_CLAIM_NUMBER = re.compile(
    r"(?<![\w.])(?:₹|Rs\.?\s?)?(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+\.\d+|-?\d+)(?=\s?(?:%|pts?\b|points?\b|rupees\b|₹))"
    r"|(?<![\w.])(?:₹|Rs\.?\s?)(-?\d[\d,]*(?:\.\d+)?)"
    r"|(?<![\w.])(-?\d+\.\d+)(?![\w.])"
)


def _figure_errors(fw: str, fig: dict) -> list[str]:
    errors = []
    if not isinstance(fig, dict):
        return [f"{fw}: must be an object with a query, query_text and row counts"]
    miss = FIGURE_KEYS - set(fig)
    if miss:
        return [f"{fw}: missing keys {sorted(miss)}"]
    if not str(fig["query_text"]).strip():
        errors.append(f"{fw}: empty query_text - the figure has no shown query")
    if not str(fig["query"]).replace("\\", "/").startswith("scratch/"):
        errors.append(f"{fw}: query path must be under scratch/, got {fig['query']!r}")
    for k in ("rows_in", "rows_out"):
        if not isinstance(fig[k], int):
            errors.append(f"{fw}: {k} must be an integer, got {fig[k]!r}")
    return errors


def _numbers_in(text: str) -> list[str]:
    found = []
    for m in _CLAIM_NUMBER.finditer(str(text)):
        token = next(g for g in m.groups() if g is not None)
        found.append(token.replace(",", ""))
    return found


def _recorded_values(inv: dict) -> list[float]:
    values: list[float] = []

    def add(v):
        if isinstance(v, bool):
            return
        if isinstance(v, (int, float)):
            values.append(float(v))
        elif isinstance(v, str):
            for tok in re.findall(r"-?\d[\d,]*(?:\.\d+)?", v):
                try:
                    values.append(float(tok.replace(",", "")))
                except ValueError:
                    pass

    for r in inv.get("reverified", []):
        add(r.get("recorded")); add(r.get("rederived"))
    decs = inv.get("decompositions")
    if isinstance(decs, list):
        for d in decs:
            for k in ("start", "end", "total_change", "sum_of_terms"):
                add(d.get(k))
            for t in d.get("terms", []):
                for k in ("points", "share_start", "share_end", "rate_start", "rate_end"):
                    add(t.get(k))
    for h in inv.get("counter_hypotheses", []):
        add(h.get("result")); add(h.get("size"))
    for p in inv.get("allocation_pairs", []):
        for half in ("allocation_free", "allocated"):
            add((p.get(half) or {}).get("value"))
    for e in inv.get("evidence", []):
        add(e.get("value"))
    rec = inv.get("recoverable_at_most")
    if isinstance(rec, dict):
        add(rec.get("value"))
    mov = inv.get("baseline_movement_at_most")
    if isinstance(mov, dict):
        for k in MOVEMENT_NUMERIC_KEYS:
            add(mov.get(k))
    return values


def _matches_recorded(token: str, recorded: list[float]) -> bool:
    try:
        n = float(token)
    except ValueError:
        return True
    decimals = len(token.split(".")[1]) if "." in token else 0
    tol = 0.5 * 10 ** (-decimals) + 1e-9
    return any(abs(round(v, decimals) - n) <= tol for v in recorded)


def validate_investigation(data: dict) -> list[str]:
    errors: list[str] = []
    missing = {"client", "scope_question", "baseline", "investigations"} - set(data)
    if missing:
        return [f"top level: missing keys {sorted(missing)}"]

    for slug, inv in data["investigations"].items():
        where = f"investigation {slug}"
        miss = REQUIRED_INVESTIGATION - set(inv)
        if miss:
            errors.append(f"{where}: missing keys {sorted(miss)}")
            continue

        # Re-derived figures are source-checked whatever the status: a blocked entry
        # exists precisely because a rerun produced a different number, so the rerun
        # must be there to see.
        for i, r in enumerate(inv["reverified"]):
            rw = f"{where} reverified[{i}]"
            errors += _figure_errors(rw, r)
            for k in ("recorded", "rederived"):
                if not isinstance(r.get(k), (int, float)):
                    errors.append(f"{rw}: {k} must be a number")
        if inv["status"] == "blocked":
            if not any(r.get("match") is False for r in inv["reverified"]):
                errors.append(f"{where}: blocked, but no re-derived figure is marked match: false - blocked on what?")
            continue
        if inv["status"] != "investigated":
            errors.append(f"{where}: status must be investigated or blocked, got {inv['status']!r}")
        for i, r in enumerate(inv["reverified"]):
            if r.get("match") is not True:
                errors.append(f"{where} reverified[{i}]: figure did not reproduce; an investigation cannot build on it")

        if inv["claim_strength"] not in CLAIM_STRENGTHS:
            errors.append(f"{where}: claim_strength must be one of {CLAIM_STRENGTHS}, got {inv['claim_strength']!r}")
        if not str(inv["preregistered_in"]).replace("\\", "/").startswith("scratch/"):
            errors.append(f"{where}: preregistered_in must point at the hypotheses file under scratch/")

        # --- counter-hypotheses
        hyps = inv["counter_hypotheses"]
        if not hyps:
            errors.append(f"{where}: counter_hypotheses is empty - an investigation with no alternatives is not one")
        decs = inv["decompositions"]
        is_rate = isinstance(decs, list)
        classes_seen = set()
        fields_named = set()
        open_alternative = False
        for i, h in enumerate(hyps):
            hw = f"{where} counter_hypotheses[{i}]"
            cls, status = h.get("class"), h.get("status")
            classes_seen.add(cls)
            if status not in HYPOTHESIS_STATUSES:
                errors.append(f"{hw}: status must be one of {HYPOTHESIS_STATUSES}, got {status!r}")
                continue
            if status == "not_applicable":
                if cls not in MAY_BE_NOT_APPLICABLE:
                    errors.append(f"{hw}: class {cls!r} is never not_applicable - a common cause or a recording change can affect anything; run the query")
                elif is_rate:
                    errors.append(f"{hw}: mix is not_applicable only when the finding is not a rate, and this one has a decomposition")
                if not str(h.get("needs", "")).strip():
                    errors.append(f"{hw}: not_applicable must say why (needs)")
                continue
            for k in ("would_be_true_if", "killed_if"):
                if not str(h.get(k, "")).strip():
                    errors.append(f"{hw}: {k} is empty - the kill criterion is stated before the query is run")
            if not re.search(r"\d", str(h.get("killed_if", ""))):
                errors.append(f"{hw}: killed_if has no figure in it - a threshold without a number is room to decide later")
            if cls in FIELD_CLASSES:
                field = str(h.get("field", "")).strip()
                if not field:
                    errors.append(f"{hw}: a {cls} candidate must name the field it lives on")
                else:
                    fields_named.add(field.lower())
            if status in ("ruled_out", "supported"):
                errors += _figure_errors(hw, h)
                if not str(h.get("result", "")).strip():
                    errors.append(f"{hw}: {status} with no result recorded")
            if status == "supported" and not str(h.get("size", "")).strip():
                errors.append(f"{hw}: supported alternative has no size - it must be nameable in the claim")
            if status == "not_ruled_out":
                open_alternative = True
                if not str(h.get("needs", "")).strip():
                    errors.append(f"{hw}: not_ruled_out must say what would decide it (needs)")
            note = " ".join(str(h.get(k, "")) for k in ("result", "needs", "hypothesis")).lower()
            if status == "ruled_out" and any(w in note for w in SOFT_STATUS_WORDS):
                errors.append(f"{hw}: ruled_out with a soft word ({SOFT_STATUS_WORDS}) - ruled out by a number, or not ruled out")
        for cls in REQUIRED_CLASSES:
            if cls not in classes_seen:
                errors.append(f"{where}: no counter-hypothesis of class {cls!r}")
        if inv["claim_strength"] == "established" and open_alternative:
            errors.append(f"{where}: claim_strength is established but an alternative is not_ruled_out")

        # --- decompositions: one per field any candidate lives on
        if isinstance(decs, str):
            if not decs.lower().startswith("n/a"):
                errors.append(f"{where}: decompositions must be a list or 'n/a - <why>', got {decs!r}")
        elif isinstance(decs, list):
            if not decs:
                errors.append(f"{where}: decompositions is an empty list - a rate finding needs at least one table")
            fields_done = set()
            for j, dec in enumerate(decs):
                dw = f"{where} decompositions[{j}]"
                if not isinstance(dec, dict):
                    errors.append(f"{dw}: must be an object")
                    continue
                miss = {"metric", "components_by", "total_change", "terms", "sum_of_terms", "reconciles"} - set(dec)
                if miss:
                    errors.append(f"{dw}: missing keys {sorted(miss)}")
                    continue
                fields_done.add(str(dec["components_by"]).strip().lower())
                errors += _figure_errors(dw, dec)
                kinds = [t.get("kind") for t in dec["terms"]]
                if kinds.count("rate") < 2:
                    errors.append(f"{dw}: needs a rate term for every component (at least two); got {kinds.count('rate')}")
                for k in ("mix", "interaction"):
                    if k not in kinds:
                        errors.append(f"{dw}: has no {k} term")
                for i, t in enumerate(dec["terms"]):
                    if not isinstance(t.get("points"), (int, float)):
                        errors.append(f"{dw} terms[{i}]: points must be a number")
                try:
                    total = float(dec["total_change"])
                    summed = sum(float(t["points"]) for t in dec["terms"])
                    if abs(summed - total) > DECOMPOSITION_TOLERANCE or abs(float(dec["sum_of_terms"]) - summed) > DECOMPOSITION_TOLERANCE:
                        errors.append(f"{dw}: terms sum to {summed:.4f}, total_change is {total:.4f} - the components are not the whole denominator")
                except (TypeError, ValueError, KeyError):
                    errors.append(f"{dw}: totals are not numbers")
                if dec["reconciles"] is not True:
                    errors.append(f"{dw}: reconciles is not true - not reported until it is")
            for field in sorted(fields_named - fields_done):
                errors.append(f"{where}: a candidate lives on field {field!r} but there is no decomposition by it - the alternatives choose their lens, not the story")
        else:
            errors.append(f"{where}: decompositions must be a list or a string")

        # --- allocation: an explicit statement, consistent with the pairs
        dep = str(inv["allocation_dependence"]).strip()
        pairs = inv["allocation_pairs"]
        if dep.lower().startswith("none"):
            if not dep[4:].strip(" -—:"):
                errors.append(f"{where}: allocation_dependence says 'none' with no evidence - name every cost used and where it is recorded at that grain")
            if pairs:
                errors.append(f"{where}: allocation_dependence says none but allocation_pairs is not empty")
        elif dep.lower().startswith("see allocation_pairs"):
            if not pairs:
                errors.append(f"{where}: allocation_dependence points at allocation_pairs, which is empty")
        else:
            errors.append(f"{where}: allocation_dependence must be 'see allocation_pairs' or 'none - <where each cost is recorded>', got {dep!r}")
        for i, p in enumerate(pairs):
            pw = f"{where} allocation_pairs[{i}]"
            for half in ("allocation_free", "allocated"):
                side = p.get(half)
                if not isinstance(side, dict) or not isinstance(side.get("value"), (int, float)):
                    errors.append(f"{pw}: {half} needs a numeric value")
                    continue
                errors += _figure_errors(f"{pw} {half}", side)
            if not str((p.get("allocated") or {}).get("rule", "")).strip():
                errors.append(f"{pw}: allocated figure has no rule - say how the shared cost was spread")
            if p.get("conclusion_changes") is True and inv["claim_strength"] == "established":
                errors.append(f"{where}: claim is established but an allocation pair changes the conclusion")

        # --- evidence and the ceiling
        if not inv["evidence"]:
            errors.append(f"{where}: no evidence figures")
        for i, fig in enumerate(inv["evidence"]):
            errors += _figure_errors(f"{where} evidence[{i}]", fig)
            if not isinstance(fig.get("value"), (int, float)):
                errors.append(f"{where} evidence[{i}]: value must be a number")
        # Points of the baseline belong to baseline_movement_at_most alone. Any other
        # figure carrying that unit is rupees over a frozen denominator with a label.
        labelled = ([(f"evidence[{i}]", f) for i, f in enumerate(inv["evidence"])]
                    + [(f"reverified[{i}]", f) for i, f in enumerate(inv["reverified"])]
                    + [(f"allocation_pairs[{i}].{half}", (p.get(half) or {}))
                       for i, p in enumerate(inv["allocation_pairs"]) for half in ("allocation_free", "allocated")])
        for label, fig in labelled:
            if isinstance(fig, dict) and BASELINE_POINTS_UNIT.search(str(fig.get("unit", ""))):
                errors.append(f"{where} {label}: unit {fig.get('unit')!r} claims points of the baseline - only "
                              "baseline_movement_at_most may; a rupee delta over the old denominator is not a movement")
        rec = inv["recoverable_at_most"]
        if isinstance(rec, str):
            if not rec.lower().startswith("not derivable"):
                errors.append(f"{where}: recoverable_at_most must be a figure object or 'not derivable - <why>', got {rec!r}")
            elif not rec[13:].strip(" -—:"):
                errors.append(f"{where}: recoverable_at_most says 'not derivable' with no reason")
        elif isinstance(rec, dict):
            errors += _figure_errors(f"{where} recoverable_at_most", rec)
            if not isinstance(rec.get("value"), (int, float)):
                errors.append(f"{where}: recoverable_at_most.value must be a number")
            unit = str(rec.get("unit", "")).lower()
            if any(m in unit for m in POINTS_MARKS) or not any(m in unit for m in CURRENCY_MARKS):
                errors.append(f"{where}: recoverable_at_most.unit must be a currency, got {rec.get('unit')!r} - "
                              "points of the baseline live only in baseline_movement_at_most")
        else:
            errors.append(f"{where}: recoverable_at_most must be a figure object or a string")

        # --- the movement of the baseline: both terms, before and after
        mov = inv["baseline_movement_at_most"]
        mw = f"{where} baseline_movement_at_most"
        if isinstance(mov, str):
            if not mov.lower().startswith("not derivable"):
                errors.append(f"{mw}: must be a movement object or 'not derivable - <why>', got {mov!r}")
            elif not mov[13:].strip(" -—:"):
                errors.append(f"{mw}: says 'not derivable' with no reason")
        elif isinstance(mov, dict):
            errors += _figure_errors(mw, mov)
            miss = MOVEMENT_KEYS - set(mov)
            if miss:
                errors.append(f"{mw}: missing keys {sorted(miss)} - the query must show numerator and denominator before and after")
            else:
                nums = {k: mov[k] for k in MOVEMENT_NUMERIC_KEYS}
                if not all(isinstance(v, (int, float)) for v in nums.values()):
                    errors.append(f"{mw}: every term must be a number")
                else:
                    n0, n1, d0, d1 = nums["numerator_from"], nums["numerator_to"], nums["denominator_from"], nums["denominator_to"]
                    if abs((n1 - n0) - nums["numerator_delta"]) > 0.011 or abs((d1 - d0) - nums["denominator_delta"]) > 0.011:
                        errors.append(f"{mw}: numerator_delta or denominator_delta is not to - from")
                    if d0 == 0 or d1 == 0:
                        errors.append(f"{mw}: a denominator is zero")
                    else:
                        if abs(100 * n0 / d0 - nums["from"]) > RATIO_TOLERANCE or abs(100 * n1 / d1 - nums["to"]) > RATIO_TOLERANCE:
                            errors.append(f"{mw}: from/to are not numerator ÷ denominator × 100 - the ratio was not recomputed")
                        if abs((nums["to"] - nums["from"]) - nums["delta"]) > RATIO_TOLERANCE:
                            errors.append(f"{mw}: delta is not to - from")
                    if d1 == d0 and not str(mov.get("denominator_unchanged_because", "")).strip():
                        errors.append(f"{mw}: the denominator did not move and no denominator_unchanged_because is given - "
                                      "a fix that restores revenue moves it; say why this one does not")
                    # The query's printed output is the evidence that both terms were
                    # computed, not typed: all four must appear in it.
                    output = str(mov.get("query_output", ""))
                    if not output.strip():
                        errors.append(f"{mw}: query_output is empty - paste the query's printed output; it must show both terms before and after")
                    else:
                        for label, val in (("numerator_from", n0), ("numerator_to", n1), ("denominator_from", d0), ("denominator_to", d1)):
                            if not _printed(float(val), output):
                                errors.append(f"{mw}: {label} = {val} does not appear in query_output - the term was typed, not computed")
                unit = str(mov.get("unit", "")).lower()
                if not any(m in unit for m in ("pt", "point")):
                    errors.append(f"{mw}: unit must be points of the baseline, got {mov.get('unit')!r}")
        else:
            errors.append(f"{mw}: must be a movement object or a string")

        # --- numbers in the claim and mechanism come from the record
        recorded = _recorded_values(inv)
        for label in ("claim", "mechanism"):
            for tok in _numbers_in(inv[label]):
                if not _matches_recorded(tok, recorded):
                    errors.append(f"{where}: {label} contains {tok!r}, which matches no recorded figure in this entry - a number from nowhere")

    # --- overlap between causes: /synthesize may combine two causes only if the rows
    # each fix touches are recorded as disjoint, by a query. With two or more entries
    # every pair must be covered.
    slugs = [s for s, i in data["investigations"].items() if i.get("status") == "investigated"]
    overlaps = data.get("overlaps", [])
    if len(slugs) >= 2:
        if not isinstance(overlaps, list):
            errors.append("top level: overlaps must be a list of {a, b, shared_rows, query, query_text, rows_in, rows_out}")
        else:
            for i, o in enumerate(overlaps):
                ow = f"overlaps[{i}]"
                if not isinstance(o, dict):
                    errors.append(f"{ow}: must be an object")
                    continue
                if not isinstance(o.get("shared_rows"), int):
                    errors.append(f"{ow}: shared_rows must be an integer row count")
                errors += _figure_errors(ow, o)
            for pair in _pairs_covered(overlaps, slugs):
                errors.append(f"overlaps: no entry for {pair} - the rows the two fixes touch must be compared by a query "
                              "before /synthesize may combine them")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_findings.py <findings.json | investigation.json>")
        return 2
    path = Path(argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{path}: unreadable or invalid JSON: {exc}")
        return 1
    if isinstance(data, dict) and "investigations" in data:
        errors = validate_investigation(data)
        label, n, what = "investigation", len(data["investigations"]), "every alternative carries its query and the decomposition reconciles"
    else:
        errors = validate(data)
        label, n, what = "findings", len(data.get("findings", {})), "every figure carries its query and row counts"
    if errors:
        print(f"validate_findings: {len(errors)} problem(s) in {path}")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"validate_findings: OK - {n} {label}(s), {what}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
