#!/usr/bin/env python3
"""Fetch PR details directly by PR ID.

Unlike get_linked_prs.py which starts from work item relations, this
script fetches PRs directly by their IDs. Used for standalone PRs that
users provide during the deployment checkpoint.

Usage:
    python fetch_prs_by_ids.py --ids 123,456
    python fetch_prs_by_ids.py --ids 123 --workspace "my-workspace"
    python fetch_prs_by_ids.py --ids 123,456 --detail

Philosophy:
- Standard library + azure CLI wrapper
- Reuses get_pr_details/format_pr_summary from get_linked_prs.py
- Self-contained and regeneratable
"""

import argparse
import json
import sys

from common import (
    AzCliWrapper,
    ExitCode,
    handle_error,
    load_config,
)
from get_linked_prs import format_pr_summary, get_pr_details, get_pr_file_changes


def fetch_prs(
    pr_ids: list[int],
    org: str,
    project: str,
    detail: bool = False,
) -> dict:
    """Fetch multiple PRs by their IDs.

    Args:
        pr_ids: List of PR IDs to fetch
        org: Organization URL
        project: Project name
        detail: If True, also fetch file changes per PR

    Returns:
        Dict with all_prs list and total_prs count
    """
    wrapper = AzCliWrapper(org=org, project=project)
    prs = []

    for pr_id in pr_ids:
        print(f"Fetching PR #{pr_id}...", file=sys.stderr)
        pr_data = get_pr_details(wrapper, str(pr_id))
        if pr_data:
            summary = format_pr_summary(pr_data)

            if detail:
                repo_id = summary.get("repository_id", "")
                if repo_id:
                    print(
                        f"  Fetching file changes for PR #{pr_id}...",
                        file=sys.stderr,
                    )
                    file_changes = get_pr_file_changes(
                        wrapper, str(pr_id), repo_id, org, project
                    )
                    if file_changes is not None:
                        summary["file_changes"] = file_changes
                        summary["files_changed_count"] = len(file_changes)
                    else:
                        summary["file_changes"] = []
                        summary["files_changed_count"] = 0

            prs.append(summary)
        else:
            print(
                f"  Warning: Could not fetch PR #{pr_id}",
                file=sys.stderr,
            )

    return {
        "all_prs": prs,
        "total_prs": len(prs),
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch PR details by ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch a single PR
  %(prog)s --ids 123

  # Fetch multiple PRs
  %(prog)s --ids 123,456,789

  # With file change details
  %(prog)s --ids 123 --detail

  # With workspace
  %(prog)s --ids 123 --workspace "my-board"
""",
    )

    parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated PR IDs",
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Include file changes per PR (additional API calls)",
    )
    parser.add_argument("--workspace", help="Named workspace alias")
    parser.add_argument("--org", help="Azure DevOps organization URL")
    parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    try:
        pr_ids = [
            int(id_str.strip())
            for id_str in args.ids.split(",")
            if id_str.strip()
        ]
    except ValueError as e:
        handle_error(f"Invalid PR ID: {e}", exit_code=ExitCode.VALIDATION_ERROR)
        return

    if not pr_ids:
        print(json.dumps({"all_prs": [], "total_prs": 0}))
        sys.exit(ExitCode.SUCCESS)

    config = load_config(workspace=args.workspace)
    org = args.org or config.get("org")
    project = args.project or config.get("project")

    if not org:
        handle_error(
            "Organization must be configured",
            exit_code=ExitCode.CONFIG_ERROR,
            details="Use --org, set AZURE_DEVOPS_ORG_URL, or run 'az devops configure'",
        )

    try:
        result = fetch_prs(pr_ids, org, project, detail=args.detail)
        print(json.dumps(result, indent=2))
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        handle_error(f"Unexpected error: {e}", ExitCode.COMMAND_ERROR)


if __name__ == "__main__":
    main()


__all__ = ["fetch_prs", "main"]
