#!/usr/bin/env python3
"""Client-data guard: fail if anything that looks like client data is in git.

Run from anywhere:  python tools/check_no_client_data.py [repo_root]

Client data entering git history is the one unrecoverable failure in this
repo (CLAUDE.md rule 1). This guard makes it loud. It looks at the union of
what is *staged* (about to be committed, the local pre-commit case) and what
is *tracked* (already committed on this branch, the CI case), and fails if:

1. any path has a component named `engagements` - that directory is the
   client corpus and is gitignored entirely;
2. any corpus-shaped file (.xlsx .xls .csv .pdf .pptx .docx) sits outside a
   known synthetic corpus (FIXTURE_CORPORA below);
3. `.gitignore` has lost one of the client-data rules, or has grown a
   negation (`!pattern`) that is not on the reviewed allowlist. A negation
   re-includes what an earlier rule excluded, so a rule can be present and
   yet no longer take effect. Modelled on the reference repo's guard.
4. any path *ever added* on any ref matches (1) or (2) - checks 1 and 2 see
   only the files that exist now, and `git rm` removes a file from the tree
   but never from history. A client P&L committed on Monday and deleted on
   Tuesday stays readable in the repo forever, which is the single failure
   this project calls unrecoverable.

Check 4 needs full history. A shallow clone - `actions/checkout` defaults to
`fetch-depth: 1` - would find nothing and pass without checking anything, so
a shallow repository is a hard failure rather than a warning.

Honest limits: a client P&L pasted into `notes.txt` outside `engagements/`
passes. Merge commits are not diffed, so content introduced only by an evil
merge is missed. The guard catches the shapes client data actually arrives
in, not a determined author. Review of diffs is the real backstop.

Stdlib only. Exit 0 on success, 1 with a list of failures.
"""

import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

# Any path with this directory component is client data, whatever the depth.
CLIENT_DIR = "engagements"

# File types a client corpus arrives in. Allowed only under a known synthetic
# corpus. Adding a corpus means adding it here in the same diff - a real export
# dropped at fixtures/ root must fail, not pass by virtue of the directory name.
CORPUS_SUFFIXES = {".xlsx", ".xls", ".csv", ".pdf", ".pptx", ".docx"}
FIXTURE_CORPORA = {"fixtures/acme-d2c"}

# What to tell the author. The staged case is recoverable with one command; the
# history case is not, and saying so is the point - a "just delete it" reflex is
# exactly what leaves the blob reachable.
STAGED_REMEDY = "Unstage it (`git restore --staged <path>`) and keep it on disk only."

HISTORY_REMEDY = (
    "It is in git history. Deleting the file does not remove it - the blob stays "
    "reachable through the commit that added it. Removing it means rewriting history "
    "(`git filter-repo`) and force-pushing every branch. Do it before the repo is "
    "shared any further, and treat the data as disclosed if it was ever pushed."
)

SHALLOW_ERROR = (
    "history: this is a shallow clone, so the history scan can see nothing and would "
    "pass without checking anything. A gate that passes vacuously is worse than no "
    "gate. Set `fetch-depth: 0` on the checkout step in .github/workflows/ci.yml, or "
    "run `git fetch --unshallow` locally."
)

# .gitignore rules that must never disappear. Exact-line match.
REQUIRED_IGNORE_RULES = [
    "engagements/",
    "**/engagements/",
    "practice/tracker.csv",
    "**/practice/tracker.csv",
    "scratch/",
    "documents/",
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


def find_violations(paths: list[str], remedy: str = STAGED_REMEDY) -> list[str]:
    """Return one message per offending path. Pure - no git, no filesystem.

    `remedy` is the closing sentence of each message. It differs between the
    staged case and the history case because the fix differs.
    """
    violations: list[str] = []
    for path in sorted(set(paths)):
        parts = _components(path)
        if not parts:
            continue
        if CLIENT_DIR in parts:
            violations.append(
                f"{path}: under `{CLIENT_DIR}/` - client data never enters git. {remedy}"
            )
            continue
        suffix = Path(parts[-1]).suffix
        in_corpus = any("/".join(parts).startswith(c + "/") for c in FIXTURE_CORPORA)
        if suffix in CORPUS_SUFFIXES and not in_corpus:
            violations.append(
                f"{path}: `{suffix}` outside a known synthetic corpus "
                f"({', '.join(sorted(FIXTURE_CORPORA))}) - corpus-shaped files are client "
                "data unless they are fixtures. If it is fictional, add its corpus root to "
                f"FIXTURE_CORPORA in tools/check_no_client_data.py; otherwise: {remedy}"
            )
    return violations


def _gitignore_text(root: Path) -> str:
    # Read the *index* copy when there is one: that is what the commit will
    # contain. A weakened .gitignore staged and then restored in the working
    # tree would otherwise pass while the commit carried the weak version.
    staged = subprocess.run(
        ["git", "show", ":.gitignore"], cwd=root, capture_output=True
    )
    if staged.returncode == 0:
        return staged.stdout.decode("utf-8")
    return (root / ".gitignore").read_text(encoding="utf-8")


def check_gitignore(root: Path) -> list[str]:
    try:
        lines = [line.strip() for line in _gitignore_text(root).splitlines()]
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


def is_shallow(root: Path) -> bool:
    out = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=root, capture_output=True, check=True,
    )
    return out.stdout.decode("utf-8").strip() == "true"


def git_history_paths(root: Path) -> list[str]:
    # Every path ever added, on every ref. `--no-renames` so a file moved *into*
    # `engagements/` is reported as an add at its new path; with rename detection
    # git reports it as R and the path would slip through.
    return _git_paths(
        root, "log", "--all", "--diff-filter=A", "--no-renames",
        "--name-only", "--pretty=format:",
    )


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_ROOT
    try:
        paths = git_paths_to_check(root)
        shallow = is_shallow(root)
        history = [] if shallow else git_history_paths(root)
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"check_no_client_data: cannot list git paths in {root}: {exc}")
        return 1
    errors = find_violations(paths) + check_gitignore(root)
    if shallow:
        errors.append(SHALLOW_ERROR)
    else:
        errors += find_violations(history, HISTORY_REMEDY)
    if errors:
        print(f"check_no_client_data: {len(errors)} failure(s) - client data must not enter git")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(
        f"check_no_client_data: OK ({len(paths)} staged+tracked paths, "
        f"{len(set(history))} paths ever added across all refs, .gitignore rules intact)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
