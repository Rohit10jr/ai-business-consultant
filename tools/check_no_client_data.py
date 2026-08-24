#!/usr/bin/env python3
"""Client-data guard: fail if anything that looks like client data is in git.

Run from anywhere:  python tools/check_no_client_data.py [repo_root]

Client data entering git history is the one unrecoverable failure in this
repo (CLAUDE.md rule 1). This guard makes it loud. It looks at the union of
what is *staged* (about to be committed, the local pre-commit case) and what
is *tracked* (already committed on this branch, the CI case), and fails if:

1. any path has a component named `engagements` - that directory is the
   client corpus and is gitignored entirely;
2. any corpus-shaped file (.xlsx .xls .csv .pdf .pptx .docx) sits outside
   `fixtures/` - the only place synthetic data is allowed;
3. `.gitignore` has lost one of the client-data rules, or has grown a
   negation (`!pattern`) that is not on the reviewed allowlist. A negation
   re-includes what an earlier rule excluded, so a rule can be present and
   yet no longer take effect. Modelled on the reference repo's guard.

Honest limit: a client P&L pasted into `notes.txt` outside `engagements/`
passes. The guard catches the shapes client data actually arrives in, not a
determined author. Review of diffs is the real backstop.

Stdlib only. Exit 0 on success, 1 with a list of failures.
"""

import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

# Any path with this directory component is client data, whatever the depth.
CLIENT_DIR = "engagements"

# File types a client corpus arrives in. Allowed only under FIXTURE_ROOT.
CORPUS_SUFFIXES = {".xlsx", ".xls", ".csv", ".pdf", ".pptx", ".docx"}
FIXTURE_ROOT = "fixtures"

# .gitignore rules that must never disappear. Exact-line match.
REQUIRED_IGNORE_RULES = [
    "engagements/",
    "**/engagements/",
    "practice/tracker.csv",
    "**/practice/tracker.csv",
    "scratch/",
    "*.xlsx",
    "*.xls",
    "*.csv",
    "*.pdf",
    "*.pptx",
    "*.docx",
]

# The only negation the repo ships: synthetic fixtures stay tracked. Any other
# `!pattern` must be added here in the same diff, so widening is reviewable.
ALLOWED_IGNORE_NEGATIONS = {"!fixtures/**"}


def _components(path: str) -> list[str]:
    # Git always reports forward slashes; lower-case so a Windows checkout
    # cannot smuggle `Engagements/` past a case-sensitive comparison.
    return [part.lower() for part in path.split("/") if part]


def find_violations(paths: list[str]) -> list[str]:
    """Return one message per offending path. Pure - no git, no filesystem."""
    violations: list[str] = []
    for path in sorted(set(paths)):
        parts = _components(path)
        if not parts:
            continue
        if CLIENT_DIR in parts:
            violations.append(
                f"{path}: under `{CLIENT_DIR}/` - client data never enters git. "
                "Unstage it (`git restore --staged <path>`) and keep it on disk only."
            )
            continue
        suffix = Path(parts[-1]).suffix
        if suffix in CORPUS_SUFFIXES and parts[0] != FIXTURE_ROOT:
            violations.append(
                f"{path}: `{suffix}` outside `{FIXTURE_ROOT}/` - corpus-shaped files are "
                "client data unless they are synthetic fixtures. Move it under "
                f"`{FIXTURE_ROOT}/` only if it is fictional; otherwise unstage it."
            )
    return violations


def check_gitignore(root: Path) -> list[str]:
    path = root / ".gitignore"
    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    except OSError as exc:
        return [f".gitignore: unreadable: {exc}"]
    errors: list[str] = []
    present = set(lines)
    for rule in REQUIRED_IGNORE_RULES:
        if rule not in present:
            errors.append(
                f".gitignore: required client-data rule missing: {rule!r}. If it moved "
                "intentionally, update REQUIRED_IGNORE_RULES in tools/check_no_client_data.py "
                "in the same commit."
            )
    for line in lines:
        if line.startswith("!") and line not in ALLOWED_IGNORE_NEGATIONS:
            errors.append(
                f".gitignore: negation not on the reviewed allowlist: {line!r}. A negation "
                "re-includes what an earlier rule excluded. If it is intentional, add it to "
                "ALLOWED_IGNORE_NEGATIONS in tools/check_no_client_data.py in the same commit."
            )
    return errors


def _git_paths(root: Path, *args: str) -> list[str]:
    out = subprocess.run(
        ["git", *args, "-z"], cwd=root, capture_output=True, check=True
    ).stdout
    return [p.decode("utf-8") for p in out.split(b"\0") if p]


def git_paths_to_check(root: Path) -> list[str]:
    # Staged covers "about to be committed"; tracked covers "already committed
    # on this branch". CI has nothing staged, a pre-commit run has the
    # offending file staged and not yet tracked - the union serves both.
    staged = _git_paths(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    tracked = _git_paths(root, "ls-files")
    return staged + tracked


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_ROOT
    try:
        paths = git_paths_to_check(root)
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"check_no_client_data: cannot list git paths in {root}: {exc}")
        return 1
    errors = find_violations(paths) + check_gitignore(root)
    if errors:
        print(f"check_no_client_data: {len(errors)} failure(s) - client data must not enter git")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"check_no_client_data: OK ({len(paths)} staged+tracked paths, .gitignore rules intact)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
