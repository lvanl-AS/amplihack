#!/usr/bin/env python3
"""Interactive Azure DevOps board selector.

Presents known boards with arrow navigation. Supports fuzzy search via
Levenshtein distance for discovering new boards. Saves new boards to
~/.azure-devops-tools.json. Prints the selected workspace alias to stdout.

Usage (from a skill/shell, capturing output):
    WORKSPACE=$(python select_board.py)
    amplihack recipe run ... -c selected_workspace="$WORKSPACE"

Options:
    --non-interactive    Print known boards as JSON and exit (for testing)
"""

import argparse
import json
import sys
from pathlib import Path

# Try questionary for arrow navigation; fall back to plain numbered input
try:
    import questionary
    from questionary import Style
    HAS_QUESTIONARY = True
except ImportError:
    HAS_QUESTIONARY = False

CONFIG_PATH = Path.home() / ".azure-devops-tools.json"

_STYLE = None
if HAS_QUESTIONARY:
    _STYLE = Style([
        ("separator", "fg:#444444"),
        ("selected", "fg:#00aa44 bold"),
        ("pointer", "fg:#00aa44 bold"),
        ("highlighted", "fg:#ffffff bold"),
        ("answer", "fg:#00aa44"),
    ])


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"workspaces": {}}
    try:
        raw = json.loads(CONFIG_PATH.read_text())
        if "workspaces" not in raw:
            raw["workspaces"] = {}
        return raw
    except Exception:
        return {"workspaces": {}}


def save_config(config: dict) -> None:
    try:
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
    except OSError as e:
        print(f"Warning: could not save config: {e}", file=sys.stderr)


def known_boards(config: dict) -> list[dict]:
    """Return list of saved boards from workspaces."""
    result = []
    for alias, ws in config.get("workspaces", {}).items():
        result.append({
            "alias": alias,
            "org": ws.get("org", ""),
            "project": ws.get("project", ""),
            "team": ws.get("team", ""),
        })
    return result


def save_board(config: dict, board: dict) -> str:
    """Save a new board to config. Returns the alias used."""
    alias = board.get("alias") or f"{board['project']}/{board['team']}"
    # Deduplicate alias if needed
    existing = config.get("workspaces", {})
    base, n = alias, 2
    while alias in existing:
        alias = f"{base}_{n}"
        n += 1
    config.setdefault("workspaces", {})[alias] = {
        "org": board["org"],
        "project": board["project"],
        "team": board.get("team", ""),
    }
    save_config(config)
    return alias


# ---------------------------------------------------------------------------
# Levenshtein search
# ---------------------------------------------------------------------------

def _levenshtein(s1: str, s2: str) -> int:
    s1, s2 = s1.lower(), s2.lower()
    m, n = len(s1), len(s2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            prev, dp[j] = dp[j], prev if s1[i-1] == s2[j-1] else 1 + min(prev, dp[j], dp[j-1])
    return dp[n]


def _score(query: str, board: dict) -> float:
    q = query.lower()
    project = board["project"].lower()
    team = board["team"].lower()
    # Substring match always wins
    if q in project or q in team:
        return 0.0
    return min(
        _levenshtein(q, project) / max(len(q), len(project)),
        _levenshtein(q, team) / max(len(q), len(team)),
    )


def fuzzy_search(query: str, boards: list[dict], exclude_aliases: set[str]) -> list[dict]:
    """Return top 5 boards matching query, excluding already-known ones."""
    candidates = [b for b in boards if b.get("alias") not in exclude_aliases]
    scored = sorted(candidates, key=lambda b: _score(query, b))
    return [b for b in scored if _score(query, b) < 0.65][:5]


# ---------------------------------------------------------------------------
# Board discovery (lazy import to keep startup fast)
# ---------------------------------------------------------------------------

def _get_all_boards(refresh: bool = False) -> list[dict]:
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from discover_boards import get_boards
    return get_boards(refresh=refresh, verbose=True)


# ---------------------------------------------------------------------------
# Interactive UI — questionary path
# ---------------------------------------------------------------------------

def _run_questionary(config: dict) -> str:
    boards = known_boards(config)
    known_aliases = {b["alias"] for b in boards}

    SEPARATOR = "─" * 40
    DIFFERENT = "Different board..."

    choices = []
    for b in boards:
        label = f"{b['project']} / {b['team']}" if b["team"] else b["project"]
        choices.append(questionary.Choice(title=label, value=b["alias"]))

    choices.append(questionary.Separator(SEPARATOR))
    choices.append(questionary.Choice(title=DIFFERENT, value="__different__"))

    answer = questionary.select(
        "Which Azure DevOps board?",
        choices=choices,
        style=_STYLE,
    ).ask()

    if answer is None:
        sys.exit(1)

    if answer != "__different__":
        return answer

    # --- Different board: fuzzy search ---
    return _search_flow_questionary(config, known_aliases)


def _search_flow_questionary(config: dict, known_aliases: set[str]) -> str:
    """Search for a new board using cached discovery data."""
    all_boards = _get_all_boards(refresh=False)

    while True:
        query = questionary.text(
            "Search boards (partial name, typos ok):",
            style=_STYLE,
        ).ask()

        if query is None:
            sys.exit(1)

        query = query.strip()
        if not query:
            continue

        results = fuzzy_search(query, all_boards, known_aliases)

        REPULL = "I don't see my board — refresh from ADO"
        BACK = "← Back"

        if not results:
            choices = [
                questionary.Choice(title=REPULL, value="__repull__"),
                questionary.Choice(title=BACK, value="__back__"),
            ]
        else:
            choices = [
                questionary.Choice(
                    title=f"{b['project']} / {b['team']}",
                    value=b,
                )
                for b in results
            ]
            choices += [
                questionary.Separator("─" * 40),
                questionary.Choice(title=REPULL, value="__repull__"),
                questionary.Choice(title=BACK, value="__back__"),
            ]

        pick = questionary.select(
            f"Results for '{query}':",
            choices=choices,
            style=_STYLE,
        ).ask()

        if pick is None or pick == "__back__":
            return _run_questionary(config)

        if pick == "__repull__":
            print("Re-fetching all boards from ADO...", file=sys.stderr)
            all_boards = _get_all_boards(refresh=True)
            continue

        # User selected a board — save and return alias
        alias = save_board(config, pick)
        return alias


# ---------------------------------------------------------------------------
# Fallback UI — plain numbered input
# ---------------------------------------------------------------------------

def _run_plain(config: dict) -> str:
    boards = known_boards(config)
    known_aliases = {b["alias"] for b in boards}

    while True:
        print("\nWhich Azure DevOps board?", file=sys.stderr)
        for i, b in enumerate(boards, 1):
            label = f"{b['project']} / {b['team']}" if b["team"] else b["project"]
            print(f"  {i}. {label}", file=sys.stderr)
        print(f"  {len(boards)+1}. Different board...", file=sys.stderr)

        try:
            raw = input("\nSelect (number): ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(1)

        try:
            n = int(raw)
        except ValueError:
            continue

        if 1 <= n <= len(boards):
            return boards[n - 1]["alias"]

        if n == len(boards) + 1:
            return _search_flow_plain(config, known_aliases)


def _search_flow_plain(config: dict, known_aliases: set[str]) -> str:
    all_boards = _get_all_boards(refresh=False)

    while True:
        try:
            query = input("\nSearch boards (partial name): ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(1)

        if not query:
            continue

        results = fuzzy_search(query, all_boards, known_aliases)

        if not results:
            print("No matches found.", file=sys.stderr)
            print("  1. Try a different search", file=sys.stderr)
            print("  2. Refresh boards from ADO (~14s)", file=sys.stderr)
            try:
                choice = input("Select: ").strip()
            except (EOFError, KeyboardInterrupt):
                sys.exit(1)
            if choice == "2":
                print("Re-fetching...", file=sys.stderr)
                all_boards = _get_all_boards(refresh=True)
            continue

        print(f"\nResults for '{query}':", file=sys.stderr)
        for i, b in enumerate(results, 1):
            print(f"  {i}. {b['project']} / {b['team']}", file=sys.stderr)
        print(f"  {len(results)+1}. Refresh boards from ADO (~14s)", file=sys.stderr)
        print(f"  {len(results)+2}. Search again", file=sys.stderr)

        try:
            raw = input("Select: ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(1)

        try:
            n = int(raw)
        except ValueError:
            continue

        if 1 <= n <= len(results):
            alias = save_board(config, results[n - 1])
            return alias
        if n == len(results) + 1:
            print("Re-fetching...", file=sys.stderr)
            all_boards = _get_all_boards(refresh=True)
        # else: search again


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Select an Azure DevOps board")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Print known boards as JSON and exit",
    )
    args = parser.parse_args()

    config = load_config()

    if args.non_interactive:
        print(json.dumps(known_boards(config), indent=2))
        return

    if HAS_QUESTIONARY:
        alias = _run_questionary(config)
    else:
        alias = _run_plain(config)

    # Print alias to stdout so the caller can capture it
    print(alias)


if __name__ == "__main__":
    main()


__all__ = ["known_boards", "fuzzy_search", "save_board", "load_config"]
