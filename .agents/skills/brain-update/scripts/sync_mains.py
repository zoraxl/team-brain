#!/usr/bin/env python3
"""Discover sibling repos from repos.yaml and sync local main from origin.

Usage (from the brain repo):

    python3 .agents/skills/brain-update/scripts/sync_mains.py \\
      --workspace /path/to/workspace-root
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

NAME_LINE_RE = re.compile(r"^  - name:\s*(\S+)\s*$")
FIELD_RE = re.compile(r"^    (github|local_path):\s*(\S+)\s*$")
PLACEHOLDER_ORG_RE = re.compile(r"^<[^>]+>$")


@dataclass
class CatalogRepo:
    name: str
    github: str = ""
    local_path: str = ""


@dataclass
class RepoResult:
    name: str
    path: str | None
    source: str
    found: bool
    branch: str = ""
    default_branch: str = "main"
    dirty: bool = False
    on_default: bool = False
    main_status: str = "not-run"
    behind_main: int | None = None
    ahead_main: int = 0
    rebase_candidate: bool = False
    looked_in: list[str] = field(default_factory=list)
    error: str = ""


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def git_out(repo: Path, *args: str) -> str:
    proc = run_git(repo, *args)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def worktree_root(path: Path) -> Path | None:
    if not path.exists():
        return None
    proc = run_git(path, "rev-parse", "--show-toplevel")
    if proc.returncode != 0:
        return None
    return Path(proc.stdout.strip()).resolve()


def find_brain_root(explicit: Path | None) -> Path:
    if explicit is not None:
        root = explicit.resolve()
        if (root / "repos.yaml").is_file():
            return root
        raise SystemExit(f"repos.yaml not found under --brain-root {root}")

    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "repos.yaml").is_file() and (candidate / ".git").exists():
            return candidate

    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "repos.yaml").is_file() and (candidate / ".git").exists():
            return candidate

    raise SystemExit("Could not locate the brain repo (repos.yaml). Pass --brain-root.")


def parse_repos_yaml(brain_root: Path) -> list[CatalogRepo]:
    text = (brain_root / "repos.yaml").read_text()
    repos: list[CatalogRepo] = []
    current: CatalogRepo | None = None
    for line in text.splitlines():
        name_match = NAME_LINE_RE.match(line)
        if name_match:
            if current is not None:
                repos.append(current)
            current = CatalogRepo(name=name_match.group(1))
            continue
        if current is None:
            continue
        field_match = FIELD_RE.match(line)
        if field_match:
            setattr(current, field_match.group(1), field_match.group(2))
    if current is not None:
        repos.append(current)
    return repos


def catalog_orgs(catalog: list[CatalogRepo]) -> set[str]:
    orgs: set[str] = set()
    for repo in catalog:
        github = repo.github.strip()
        if not github or "/" not in github:
            continue
        org = github.split("/", 1)[0].lower()
        if PLACEHOLDER_ORG_RE.match(org) or org in {"org", "<org>"}:
            continue
        orgs.add(org)
    return orgs


def origin_matches_orgs(repo: Path, orgs: set[str]) -> bool:
    if not orgs:
        return False
    proc = run_git(repo, "remote", "get-url", "origin")
    if proc.returncode != 0:
        return False
    url = proc.stdout.strip().lower()
    return any(f"{org}/" in url for org in orgs)


def default_branch(repo: Path) -> str:
    proc = run_git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if proc.returncode == 0:
        ref = proc.stdout.strip()
        return ref.rsplit("/", 1)[-1] or "main"
    for name in ("main", "master"):
        if run_git(repo, "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{name}").returncode == 0:
            return name
        if run_git(repo, "show-ref", "--verify", "--quiet", f"refs/heads/{name}").returncode == 0:
            return name
    return "main"


def count_commits(repo: Path, rev_range: str) -> int:
    proc = run_git(repo, "rev-list", "--count", rev_range)
    if proc.returncode != 0:
        return 0
    try:
        return int(proc.stdout.strip() or "0")
    except ValueError:
        return 0


def resolve_catalog_path(brain_root: Path, repo: CatalogRepo) -> Path:
    if repo.local_path in ("", "."):
        return brain_root
    return (brain_root / repo.local_path).resolve()


def sibling_candidates(brain_root: Path, name: str) -> list[Path]:
    parent = brain_root.parent
    return [
        (parent / name).resolve(),
        (Path.home() / "Documents" / "GitHub" / name).resolve(),
        (Path.home() / "src" / name).resolve(),
    ]


def discover_extra_dirs(
    brain_root: Path,
    workspace_roots: list[Path],
    catalog: list[CatalogRepo],
    orgs: set[str],
) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    catalog_names = {repo.name for repo in catalog}

    def add(path: Path, require_org: bool) -> None:
        resolved = path.resolve()
        if resolved in seen or not resolved.is_dir():
            return
        root = worktree_root(resolved)
        if root is None or root in seen:
            return
        if require_org and not origin_matches_orgs(root, orgs):
            return
        seen.add(root)
        found.append(root)

    for workspace in workspace_roots:
        add(workspace, require_org=bool(orgs))

    parent = brain_root.parent
    if parent.is_dir():
        try:
            children = list(parent.iterdir())
        except OSError:
            children = []
        for child in children:
            if child.is_dir() and child.name in catalog_names:
                add(child, require_org=False)

    return found


def unique_repos(
    catalog: list[CatalogRepo],
    brain_root: Path,
    extra_dirs: list[Path],
) -> list[tuple[str, Path | None, str, list[str]]]:
    ordered: list[tuple[str, Path | None, str, list[str]]] = []
    seen_paths: set[Path] = set()
    seen_names: set[str] = set()

    for repo in catalog:
        looked: list[str] = []
        candidates = [resolve_catalog_path(brain_root, repo), *sibling_candidates(brain_root, repo.name)]
        chosen: Path | None = None
        for candidate in candidates:
            looked.append(str(candidate))
            if not candidate.exists():
                continue
            root = worktree_root(candidate)
            if root is None:
                continue
            chosen = root
            break
        if chosen is not None:
            if chosen in seen_paths:
                continue
            seen_paths.add(chosen)
            seen_names.add(repo.name)
            ordered.append((repo.name, chosen, "repos.yaml", looked))
        else:
            seen_names.add(repo.name)
            ordered.append((repo.name, None, "repos.yaml", looked))

    catalog_names = {repo.name for repo in catalog}
    for extra in extra_dirs:
        if extra in seen_paths:
            continue
        name = extra.name
        if name in seen_names and name in catalog_names:
            continue
        seen_paths.add(extra)
        seen_names.add(name)
        ordered.append((name, extra, "filesystem", [str(extra)]))

    return ordered


def classify_extra_source(path: Path, workspace_roots: list[Path]) -> str:
    resolved = path.resolve()
    for workspace in workspace_roots:
        try:
            workspace_resolved = workspace.resolve()
            if resolved == workspace_resolved or resolved.is_relative_to(workspace_resolved):
                return "workspace"
        except (OSError, ValueError):
            continue
    return "filesystem"


def last_error_line(proc: subprocess.CompletedProcess[str], fallback: str) -> str:
    text = (proc.stderr or proc.stdout).strip()
    if not text:
        return fallback
    return text.splitlines()[-1]


def sync_repo(name: str, path: Path, source: str) -> RepoResult:
    result = RepoResult(name=name, path=str(path), source=source, found=True)
    try:
        result.branch = git_out(path, "branch", "--show-current")
        result.dirty = bool(git_out(path, "status", "--porcelain"))
        fetch = run_git(path, "fetch", "origin")
        if fetch.returncode != 0:
            result.main_status = "failed: fetch"
            result.error = last_error_line(fetch, "git fetch origin failed")
            result.default_branch = default_branch(path)
            return result

        result.default_branch = default_branch(path)
        default = result.default_branch
        result.on_default = result.branch == default

        if result.on_default:
            if result.dirty:
                result.main_status = "skipped: dirty"
            else:
                pull = run_git(path, "pull", "--rebase", "origin", default)
                if pull.returncode != 0:
                    result.main_status = "failed: pull --rebase"
                    result.error = last_error_line(pull, "git pull --rebase failed")
                else:
                    out = (pull.stdout + pull.stderr).lower()
                    if "up to date" in out or "up-to-date" in out:
                        result.main_status = "already current"
                    else:
                        result.main_status = "pulled with rebase"
        else:
            ahead_on_main = 0
            if run_git(path, "show-ref", "--verify", "--quiet", f"refs/heads/{default}").returncode == 0:
                ahead_on_main = count_commits(path, f"origin/{default}..{default}")
            if ahead_on_main > 0:
                result.main_status = "skipped: local main has unique commits"
                result.error = f"local {default} is {ahead_on_main} commit(s) ahead of origin/{default}"
            else:
                before = run_git(path, "rev-parse", "--verify", default)
                ff = run_git(path, "fetch", "origin", f"{default}:{default}")
                if ff.returncode != 0:
                    result.main_status = "failed: update local main"
                    result.error = last_error_line(ff, f"git fetch origin {default}:{default} failed")
                else:
                    after = run_git(path, "rev-parse", default)
                    remote = run_git(path, "rev-parse", f"origin/{default}")
                    if (
                        before.returncode == 0
                        and after.returncode == 0
                        and before.stdout == after.stdout
                    ):
                        result.main_status = "already current"
                    elif after.returncode == 0 and remote.returncode == 0 and after.stdout == remote.stdout:
                        result.main_status = "fast-forwarded"
                    else:
                        result.main_status = "fast-forwarded"

        if run_git(path, "show-ref", "--verify", "--quiet", f"refs/heads/{default}").returncode == 0 and result.branch:
            if result.branch != default:
                result.behind_main = count_commits(path, f"HEAD..{default}")
                result.ahead_main = count_commits(path, f"{default}..HEAD")
                synced_ok = result.main_status in {"already current", "fast-forwarded"}
                result.rebase_candidate = synced_ok and not result.dirty and (result.behind_main or 0) > 0
            else:
                result.behind_main = 0
                result.ahead_main = 0
        return result
    except Exception as exc:  # noqa: BLE001 — keep going through the remaining repos
        result.main_status = "failed"
        result.error = str(exc)
        return result


def render_report(results: list[RepoResult]) -> str:
    lines = ["## Brain Update — main sync", ""]
    found = [r for r in results if r.found]
    missing = [r for r in results if not r.found]
    lines.append("| Repo | Branch | Main sync | Behind local main | Dirty |")
    lines.append("|------|--------|-----------|-------------------|-------|")
    for row in found:
        behind = "—" if row.behind_main is None else str(row.behind_main)
        dirty = "yes" if row.dirty else "no"
        branch = row.branch or "(detached)"
        status = row.main_status
        if row.error:
            status = f"{status} ({row.error})"
        lines.append(f"| `{row.name}` | `{branch}` | {status} | {behind} | {dirty} |")
    lines.append("")
    if missing:
        lines.append("### Not found")
        for row in missing:
            looked = ", ".join(f"`{p}`" for p in row.looked_in) or "(no paths)"
            lines.append(f"- `{row.name}`: looked in {looked}")
        lines.append("")
    candidates = [r for r in found if r.branch and not r.on_default]
    lines.append("### Feature branches")
    if not candidates:
        lines.append("None. Every found repo is on its default branch.")
    else:
        for row in candidates:
            behind = row.behind_main if row.behind_main is not None else "?"
            note = []
            if row.dirty:
                note.append("dirty — cannot rebase until clean")
            elif row.rebase_candidate:
                note.append("rebase candidate")
            elif row.behind_main == 0:
                note.append("already contains local main")
            else:
                note.append(row.main_status)
            extra = f" — {'; '.join(note)}" if note else ""
            lines.append(
                f"- `{row.name}` (`{row.branch}`): {behind} behind / {row.ahead_main} ahead of local `{row.default_branch}`{extra}"
            )
        lines.append("")
        lines.append("Ask the user whether to rebase these feature branches onto the newly synced local main.")
    lines.append("")
    return "\n".join(lines)


FAIL_STATUSES = {
    "failed",
    "failed: fetch",
    "failed: pull --rebase",
    "failed: update local main",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync local main in sibling repos from origin.")
    parser.add_argument("--brain-root", type=Path, default=None)
    parser.add_argument(
        "--workspace",
        action="append",
        default=[],
        type=Path,
        help="Workspace root to include if it is a git checkout in a catalog org.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON after the markdown report.")
    parser.add_argument("--dry-run", action="store_true", help="Discover only; do not fetch or update.")
    args = parser.parse_args(argv)

    brain_root = find_brain_root(args.brain_root)
    catalog = parse_repos_yaml(brain_root)
    orgs = catalog_orgs(catalog)
    workspace_roots = [path.resolve() for path in args.workspace if path.exists()]
    extras = discover_extra_dirs(brain_root, workspace_roots, catalog, orgs)

    discovered = unique_repos(catalog, brain_root, extras)
    results: list[RepoResult] = []
    catalog_names = {repo.name for repo in catalog}

    for name, path, source, looked_in in discovered:
        if path is None:
            results.append(
                RepoResult(
                    name=name,
                    path=None,
                    source=source,
                    found=False,
                    looked_in=looked_in,
                    main_status="not found",
                )
            )
            continue
        if name not in catalog_names:
            source = classify_extra_source(path, workspace_roots)
        if args.dry_run:
            result = RepoResult(name=name, path=str(path), source=source, found=True, looked_in=looked_in)
            try:
                result.branch = git_out(path, "branch", "--show-current")
                result.dirty = bool(git_out(path, "status", "--porcelain"))
                result.default_branch = default_branch(path)
                result.on_default = result.branch == result.default_branch
                result.main_status = "dry-run"
            except Exception as exc:  # noqa: BLE001
                result.main_status = "failed"
                result.error = str(exc)
            results.append(result)
            continue
        result = sync_repo(name, path, source)
        result.looked_in = looked_in
        results.append(result)

    sys.stdout.write(render_report(results))
    if args.json:
        payload = {
            "brain_root": str(brain_root),
            "cwd": str(Path.cwd()),
            "repos": [asdict(row) for row in results],
        }
        sys.stdout.write("\n```json\n")
        sys.stdout.write(json.dumps(payload, indent=2))
        sys.stdout.write("\n```\n")

    failed = [row for row in results if row.found and row.main_status in FAIL_STATUSES]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
