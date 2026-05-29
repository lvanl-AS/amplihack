#!/usr/bin/env python3
"""Extract child work item IDs from a parent's relations.

Given a parent work item ID, fetches its relations and returns a
comma-separated list of child IDs (Hierarchy-Forward links).

Usage:
    python extract_child_ids.py --parent-id 12345 --workspace "my-workspace"

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


def extract_child_ids(
    parent_id: int,
    org: str,
    project: str,
) -> list[int]:
    """Extract child work item IDs from parent relations.

    Args:
        parent_id: Parent work item ID
        org: Organization URL
        project: Project name

    Returns:
        List of child work item IDs
    """
    wrapper = AzCliWrapper(org=org, project=project)
    parent = get_work_item_details(wrapper, parent_id, include_relations=True)

    child_ids = []
    for rel in parent.get("relations") or []:
        if rel.get("rel") == "System.LinkTypes.Hierarchy-Forward":
            url = rel.get("url", "")
            if url:
                try:
                    child_id = int(url.rstrip("/").split("/")[-1])
                    child_ids.append(child_id)
                except ValueError:
                    pass

    return child_ids


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract child work item IDs from a parent's relations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get child IDs for feature #12345
  %(prog)s --parent-id 12345

  # With workspace
  %(prog)s --parent-id 12345 --workspace "my-board"
""",
    )

    parser.add_argument(
        "--parent-id",
        required=True,
        help="Parent work item ID",
    )
    parser.add_argument("--workspace", help="Named workspace alias")
    parser.add_argument("--org", help="Azure DevOps organization URL")
    parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    try:
        parent_id = validate_work_item_id(args.parent_id)
    except ValueError as e:
        handle_error(str(e), exit_code=ExitCode.VALIDATION_ERROR)
        return

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
        child_ids = extract_child_ids(parent_id, org, project)
        # Output comma-separated IDs (empty string if none)
        print(",".join(str(cid) for cid in child_ids))
        print(
            f"Found {len(child_ids)} child work item(s) under #{parent_id}",
            file=sys.stderr,
        )
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        handle_error(f"Unexpected error: {e}", ExitCode.COMMAND_ERROR)


if __name__ == "__main__":
    main()


__all__ = ["extract_child_ids", "main"]
