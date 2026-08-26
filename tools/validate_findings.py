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
                          "claim_strength", "mechanism", "decomposition", "counter_hypotheses",
                          "allocation_pairs", "evidence", "recoverable_at_most",
                          "open_questions", "status"}
CLAIM_STRENGTHS = ("established", "partial", "unsupported")
# Every investigation must have looked at these three shapes of alternative, plus
# the cause it is arguing for. A class may only be absent with a stated reason.
REQUIRED_CLASSES = ("mix", "common-cause", "measurement", "named")
HYPOTHESIS_STATUSES = ("ruled_out", "supported", "not_ruled_out", "not_applicable")
# Words that mean a kill query was not run.
SOFT_STATUS_WORDS = ("unlikely", "probably", "considered", "seems")
DECOMPOSITION_TOLERANCE = 0.011  # two-decimal rounding on each term


def _figure_errors(fw: str, fig: dict) -> list[str]:
    errors = []
    miss = {"query", "query_text", "rows_in", "rows_out"} - set(fig)
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
        if inv["status"] == "blocked":
            # A blocked entry records a figure that would not reproduce; it makes
            # no claim, so the claim rules below do not apply to it.
            if all(r.get("match") is True for r in inv["reverified"]):
                errors.append(f"{where}: blocked, but every re-derived figure matched - blocked on what?")
            continue
        if inv["status"] != "investigated":
            errors.append(f"{where}: status must be investigated or blocked, got {inv['status']!r}")

        for i, r in enumerate(inv["reverified"]):
            rw = f"{where} reverified[{i}]"
            errors += _figure_errors(rw, r)
            if r.get("match") is not True:
                errors.append(f"{rw}: figure did not reproduce; an investigation cannot build on it")

        if inv["claim_strength"] not in CLAIM_STRENGTHS:
            errors.append(f"{where}: claim_strength must be one of {CLAIM_STRENGTHS}, got {inv['claim_strength']!r}")
        if any(h in str(inv["recoverable_at_most"]).lower() for h in HEDGES):
            errors.append(f"{where}: recoverable_at_most hedges - a ceiling is a figure or 'not derivable - <why>'")
        rec = str(inv["recoverable_at_most"]).strip()
        if rec.lower().startswith("not derivable") and not rec[13:].strip(" -—:"):
            errors.append(f"{where}: recoverable_at_most says 'not derivable' with no reason")

        hyps = inv["counter_hypotheses"]
        if not hyps:
            errors.append(f"{where}: counter_hypotheses is empty - an investigation with no alternatives is not one")
        classes_seen = set()
        open_alternative = False
        for i, h in enumerate(hyps):
            hw = f"{where} counter_hypotheses[{i}]"
            cls, status = h.get("class"), h.get("status")
            classes_seen.add(cls)
            if status not in HYPOTHESIS_STATUSES:
                errors.append(f"{hw}: status must be one of {HYPOTHESIS_STATUSES}, got {status!r}")
                continue
            for k in ("would_be_true_if", "killed_if"):
                if not str(h.get(k, "")).strip() and status != "not_applicable":
                    errors.append(f"{hw}: {k} is empty - the kill criterion is stated before the query is run")
            if status in ("ruled_out", "supported"):
                errors += _figure_errors(hw, h)
                if not str(h.get("result", "")).strip():
                    errors.append(f"{hw}: {status} with no result recorded")
            if status == "supported" and not str(h.get("size", "")).strip():
                errors.append(f"{hw}: supported alternative has no size - it must be nameable in the claim")
            if status in ("not_ruled_out", "not_applicable") and not str(h.get("needs", "")).strip():
                errors.append(f"{hw}: {status} must say what would decide it (needs)")
            if status == "not_ruled_out":
                open_alternative = True
            note = " ".join(str(h.get(k, "")) for k in ("result", "needs", "hypothesis")).lower()
            if status == "ruled_out" and any(w in note for w in SOFT_STATUS_WORDS):
                errors.append(f"{hw}: ruled_out with a soft word ({SOFT_STATUS_WORDS}) - ruled out by a number, or not ruled out")
        for cls in REQUIRED_CLASSES:
            if cls not in classes_seen:
                errors.append(f"{where}: no counter-hypothesis of class {cls!r} - each class needs a query or a not_applicable reason")
        if inv["claim_strength"] == "established" and open_alternative:
            errors.append(f"{where}: claim_strength is established but an alternative is not_ruled_out")

        dec = inv["decomposition"]
        if isinstance(dec, str):
            if not dec.lower().startswith("n/a"):
                errors.append(f"{where}: decomposition must be an object or 'n/a - <why>', got {dec!r}")
        elif isinstance(dec, dict):
            miss = {"metric", "components_by", "total_change", "terms", "sum_of_terms", "reconciles"} - set(dec)
            if miss:
                errors.append(f"{where}: decomposition missing keys {sorted(miss)}")
            else:
                errors += _figure_errors(f"{where} decomposition", dec)
                kinds = [t.get("kind") for t in dec["terms"]]
                if kinds.count("rate") < 2:
                    errors.append(f"{where}: decomposition needs a rate term for every component (at least two); got {kinds.count('rate')}")
                for k in ("mix", "interaction"):
                    if k not in kinds:
                        errors.append(f"{where}: decomposition has no {k} term")
                for i, t in enumerate(dec["terms"]):
                    if not isinstance(t.get("points"), (int, float)):
                        errors.append(f"{where} decomposition terms[{i}]: points must be a number")
                try:
                    total = float(dec["total_change"])
                    summed = sum(float(t["points"]) for t in dec["terms"])
                    if abs(summed - total) > DECOMPOSITION_TOLERANCE or abs(float(dec["sum_of_terms"]) - summed) > DECOMPOSITION_TOLERANCE:
                        errors.append(f"{where}: decomposition terms sum to {summed:.4f}, total_change is {total:.4f} - the components are not the whole denominator")
                except (TypeError, ValueError, KeyError):
                    errors.append(f"{where}: decomposition totals are not numbers")
                if dec["reconciles"] is not True:
                    errors.append(f"{where}: decomposition.reconciles is not true - not reported until it is")
        else:
            errors.append(f"{where}: decomposition must be an object or a string")

        for i, p in enumerate(inv["allocation_pairs"]):
            pw = f"{where} allocation_pairs[{i}]"
            for half in ("allocation_free", "allocated"):
                side = p.get(half)
                if not isinstance(side, dict) or not isinstance(side.get("value"), (int, float)) or not str(side.get("query", "")).strip():
                    errors.append(f"{pw}: {half} needs a numeric value and a query")
            if not str((p.get("allocated") or {}).get("rule", "")).strip():
                errors.append(f"{pw}: allocated figure has no rule - say how the shared cost was spread")
            if p.get("conclusion_changes") is True and inv["claim_strength"] == "established":
                errors.append(f"{where}: claim is established but an allocation pair changes the conclusion")

        if not inv["evidence"]:
            errors.append(f"{where}: no evidence figures")
        for i, fig in enumerate(inv["evidence"]):
            errors += _figure_errors(f"{where} evidence[{i}]", fig)
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
