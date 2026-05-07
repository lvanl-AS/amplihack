#!/usr/bin/env python3
"""
Tool: get_revisions.py

Purpose: Get revision history of an Azure DevOps work item

Usage:
    python get_revisions.py --id <work_item_id> [options]

Examples:
    python get_revisions.py --id 12345
    python get_revisions.py --id 12345 --format json
    python get_revisions.py --id 12345 --workspace mobile

Philosophy:
- Standard library + azure CLI wrapper
- Clear error messages with actionable guidance
- Fail-fast validation
- Self-contained and regeneratable
"""

import argparse
import json
from typing import Any

from common import (
    AzCliWrapper,
    ExitCode,
    handle_error,
    load_config,
    validate_work_item_id,
)


def get_revisions(
    wrapper: AzCliWrapper,
    work_item_id: int,
) -> list[dict[str, Any]]:
    """Get revision history for a work item via ADO REST API.

    Args:
        wrapper: AzCliWrapper instance (must have org and project set)
        work_item_id: Work item ID

    Returns:
        List of revision objects

    Raises:
        SystemExit: If operation fails
    """
    if not wrapper.org or not wrapper.project:
        handle_error(
            "Organization and project must be configured",
            exit_code=ExitCode.CONFIG_ERROR,
        )

    url = (
        f"{wrapper.org.rstrip('/')}/{wrapper.project}"
        f"/_apis/wit/workItems/{work_item_id}/revisions?api-version=7.1"
    )

    result = wrapper.run(
        ["az", "rest", "--method", "get", "--url", url],
        timeout=30,
    )

    if not result.success:
        handle_error(
            f"Failed to get revisions for work item {work_item_id}",
            exit_code=ExitCode.COMMAND_ERROR,
            details=result.stderr,
        )

    try:
        data = json.loads(result.stdout)
        return data.get("value", [])
    except (json.JSONDecodeError, KeyError) as e:
        handle_error(
            "Failed to parse revisions response",
            exit_code=ExitCode.COMMAND_ERROR,
            details=str(e),
        )
        return []  # Never reached


def format_summary(revisions: list[dict[str, Any]]) -> str:
    """Format revisions as human-readable summary."""
    if not revisions:
        return "No revisions."

    lines = [f"Revisions ({len(revisions)}):", "=" * 60]
    for rev in revisions:
        rev_num = rev.get("rev", "?")
        fields = rev.get("fields", {})
        changed_by = fields.get("System.ChangedBy", {})
        if isinstance(changed_by, dict):
            changed_by = changed_by.get("displayName", "Unknown")
        changed_date = fields.get("System.ChangedDate", "Unknown")
        state = fields.get("System.State", "")
        title = fields.get("System.Title", "")

        lines.append(f"\nRev {rev_num} — {changed_by} — {changed_date}")
        if title:
            lines.append(f"  Title: {title}")
        if state:
            lines.append(f"  State: {state}")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Get Azure DevOps work item revision history",
    )

    parser.add_argument("--id", required=True, help="Work item ID")
    parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="Output format (default: summary)",
    )

    # Config options
    parser.add_argument("--org", help="Azure DevOps organization URL")
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--workspace", help="Named workspace alias from ~/.azure-devops-tools.json")

    args = parser.parse_args()

    # Validate work item ID
    try:
        work_item_id = validate_work_item_id(args.id)
    except ValueError as e:
        handle_error(str(e), exit_code=ExitCode.VALIDATION_ERROR)
        return

    # Load configuration
    config = load_config(workspace=args.workspace)
    org = args.org or config.get("org")
    project = args.project or config.get("project")

    if not org or not project:
        handle_error(
            "Organization and project must be configured",
            exit_code=ExitCode.CONFIG_ERROR,
            details="Use --org/--project, environment variables, or az devops configure",
        )

    wrapper = AzCliWrapper(org=org, project=project)

    try:
        revisions = get_revisions(wrapper, work_item_id)

        if args.format == "json":
            print(json.dumps(revisions, indent=2))
        else:
            print(format_summary(revisions))

    except Exception as e:
        handle_error(
            f"Unexpected error: {e}",
            exit_code=ExitCode.COMMAND_ERROR,
        )


if __name__ == "__main__":
    main()
