#!/usr/bin/env python3
"""Fetch details for multiple work items by ID.

Given a comma-separated list of work item IDs, fetches each with relations
and outputs JSON array to stdout. Skips items that fail to fetch with a
warning to stderr.

Usage:
    python fetch_child_stories.py --ids 12345,12346,12347 --workspace "my-workspace"

Philosophy:
- Standard library + azure CLI wrapper
- Replaces fragile inline Python in recipe YAML
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
    validate_work_item_id,
)
from get_work_item import get_work_item_details


def fetch_work_items(
    work_item_ids: list[int],
    org: str,
    project: str,
) -> list[dict]:
    """Fetch multiple work items with relations.

    Args:
        work_item_ids: List of work item IDs
        org: Organization URL
        project: Project name

    Returns:
        List of work item data dicts
    """
    wrapper = AzCliWrapper(org=org, project=project)
    stories = []

    for wi_id in work_item_ids:
        try:
            story = get_work_item_details(
                wrapper, wi_id, include_relations=True
            )
            stories.append(story)
            print(f"Fetched work item #{wi_id}", file=sys.stderr)
        except SystemExit:
            print(
                f"Warning: Could not fetch #{wi_id}, skipping",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"Warning: Could not fetch #{wi_id}: {e}",
                file=sys.stderr,
            )

    return stories


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch details for multiple work items",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch stories by ID
  %(prog)s --ids 12345,12346,12347

  # With workspace
  %(prog)s --ids 12345,12346 --workspace "my-board"
""",
    )

    parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated work item IDs",
    )
    parser.add_argument("--workspace", help="Named workspace alias")
    parser.add_argument("--org", help="Azure DevOps organization URL")
    parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    # Parse and validate IDs
    try:
        work_item_ids = [
            validate_work_item_id(id_str.strip())
            for id_str in args.ids.split(",")
            if id_str.strip()
        ]
    except ValueError as e:
        handle_error(str(e), exit_code=ExitCode.VALIDATION_ERROR)
        return

    if not work_item_ids:
        print("[]")
        sys.exit(ExitCode.SUCCESS)

    config = load_config(workspace=args.workspace)
    org = args.org or config.get("org")
    project = args.project or config.get("project")

    if not org or not project:
        handle_error(
            "Organization and project must be configured",
            exit_code=ExitCode.CONFIG_ERROR,
            details="Use --workspace, --org/--project, or set AZURE_DEVOPS_ORG_URL and AZURE_DEVOPS_PROJECT",
        )

    try:
        stories = fetch_work_items(work_item_ids, org, project)
        print(json.dumps(stories, indent=2))
        print(
            f"Fetched {len(stories)} of {len(work_item_ids)} work items",
            file=sys.stderr,
        )
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        handle_error(f"Unexpected error: {e}", ExitCode.COMMAND_ERROR)


if __name__ == "__main__":
    main()


__all__ = ["fetch_work_items", "main"]
