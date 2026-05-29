#!/usr/bin/env python3
"""Extract unique repository names from multiple PR data sources.

Reads PR data JSON from stdin with sources separated by ===SOURCE===
markers. Each source should be JSON output from get_linked_prs.py or
fetch_prs_by_ids.py (containing an "all_prs" array), or an empty string.

Usage:
    python extract_repo_names.py <<'EOF'
    {"all_prs": [{"repository": "repo-a"}, {"repository": "repo-b"}]}
    ===SOURCE===
    {"all_prs": [{"repository": "repo-b"}, {"repository": "repo-c"}]}
    ===SOURCE===

    EOF

    # Output: repo-a,repo-b,repo-c

Philosophy:
- Standard library only
- Reads from stdin to avoid shell quoting issues with large JSON
- Handles empty/missing sources gracefully
- Self-contained and regeneratable
"""

import json
import sys


def extract_repos_from_pr_data(json_text: str) -> set[str]:
    """Extract repository names from a single PR data JSON string.

    Args:
        json_text: JSON string with "all_prs" array

    Returns:
        Set of repository name strings
    """
    text = json_text.strip()
    if not text:
        return set()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return set()

    repos = set()
    prs = data.get("all_prs", [])
    if isinstance(prs, list):
        for pr in prs:
            repo = pr.get("repository", "")
            if repo:
                repos.add(repo)
    return repos


def main() -> None:
    """Main entry point."""
    text = sys.stdin.read()
    sources = text.split("===SOURCE===")

    all_repos: set[str] = set()
    for source in sources:
        repos = extract_repos_from_pr_data(source)
        all_repos.update(repos)

    print(",".join(sorted(all_repos)))


if __name__ == "__main__":
    main()


__all__ = ["extract_repos_from_pr_data", "main"]
