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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_findings.py <findings.json>")
        return 2
    path = Path(argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{path}: unreadable or invalid JSON: {exc}")
        return 1
    errors = validate(data)
    if errors:
        print(f"validate_findings: {len(errors)} problem(s) in {path}")
        for e in errors:
            print(f"  - {e}")
        return 1
    n = len(data["findings"])
    print(f"validate_findings: OK - {n} finding(s), every figure carries its query and row counts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
