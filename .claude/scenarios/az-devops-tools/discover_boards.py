#!/usr/bin/env python3
"""Discover all Azure DevOps boards (project + team combinations) for the itsals org.

Fetches all projects then all teams in parallel, caches results to
~/.azure-devops-tools-cache.json. Subsequent runs are instant.

Usage:
    python discover_boards.py              # use cache if available
    python discover_boards.py --refresh    # force re-fetch from ADO
    python discover_boards.py --bootstrap  # populate cache, print summary, exit
"""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

ORG = "https://dev.azure.com/itsals"
CACHE_PATH = Path.home() / ".azure-devops-tools-cache.json"
CACHE_TTL_DAYS = 7
MAX_WORKERS = 20


def _run(cmd: list[str]) -> dict | list | None:
    """Run an az CLI command and return parsed JSON output."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return None


def _fetch_teams_for_project(project_name: str) -> list[dict]:
    data = _run([
        "az", "devops", "team", "list",
        "--org", ORG,
        "--project", project_name,
        "--output", "json",
    ])
    if not data:
        return []
    return [
        {
            "org": ORG,
            "project": project_name,
            "team": t["name"],
            "alias": f"{project_name}/{t['name']}",
        }
        for t in data
    ]


def fetch_all_boards(verbose: bool = False) -> list[dict]:
    """Fetch every project+team combination from ADO. Takes ~14s."""
    if verbose:
        print("Fetching projects...", file=sys.stderr)

    data = _run([
        "az", "devops", "project", "list",
        "--org", ORG,
        "--output", "json",
    ])
    if not data:
        print("Error: could not fetch projects. Check az login and org access.", file=sys.stderr)
        sys.exit(1)

    projects = data.get("value", [])
    if verbose:
        print(f"Found {len(projects)} projects. Fetching teams in parallel...", file=sys.stderr)

    boards = []
    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_fetch_teams_for_project, p["name"]): p for p in projects}
        for future in as_completed(futures):
            boards.extend(future.result())
            completed += 1
            if verbose and completed % 20 == 0:
                print(f"  {completed}/{len(projects)} projects fetched...", file=sys.stderr)

    if verbose:
        print(f"Done. Found {len(boards)} boards.", file=sys.stderr)

    return boards


def load_cache() -> list[dict] | None:
    """Return cached boards if cache exists and is fresh. None otherwise."""
    if not CACHE_PATH.exists():
        return None
    try:
        raw = json.loads(CACHE_PATH.read_text())
        cached_at = datetime.fromisoformat(raw.get("cached_at", "2000-01-01"))
        if datetime.now() - cached_at > timedelta(days=CACHE_TTL_DAYS):
            return None
        return raw.get("boards", [])
    except Exception:
        return None


def save_cache(boards: list[dict]) -> None:
    """Write boards to the cache file."""
    try:
        CACHE_PATH.write_text(json.dumps({
            "cached_at": datetime.now().isoformat(),
            "org": ORG,
            "boards": boards,
        }, indent=2))
    except OSError as e:
        print(f"Warning: could not write cache: {e}", file=sys.stderr)


def get_boards(refresh: bool = False, verbose: bool = False) -> list[dict]:
    """Return boards from cache, fetching from ADO if needed."""
    if not refresh:
        cached = load_cache()
        if cached is not None:
            return cached

    boards = fetch_all_boards(verbose=verbose)
    save_cache(boards)
    return boards


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover Azure DevOps boards for itsals")
    parser.add_argument("--refresh", action="store_true", help="Force re-fetch even if cache is fresh")
    parser.add_argument("--bootstrap", action="store_true", help="Populate cache and print summary")
    parser.add_argument("--json", action="store_true", help="Output boards as JSON")
    args = parser.parse_args()

    boards = get_boards(refresh=args.refresh, verbose=True)

    if args.json:
        print(json.dumps(boards, indent=2))
    elif args.bootstrap:
        print(f"Cached {len(boards)} boards from {len({b['project'] for b in boards})} projects.")
        print(f"Cache written to: {CACHE_PATH}")
    else:
        for b in boards:
            print(f"{b['project']} / {b['team']}")


if __name__ == "__main__":
    main()


__all__ = ["get_boards", "fetch_all_boards", "load_cache", "save_cache"]
