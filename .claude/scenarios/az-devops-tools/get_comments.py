#!/usr/bin/env python3
"""
Tool: get_comments.py

Purpose: Get comments on an Azure DevOps work item

Usage:
    python get_comments.py --id <work_item_id> [options]

Examples:
    python get_comments.py --id 12345
    python get_comments.py --id 12345 --format json
    python get_comments.py --id 12345 --workspace mobile

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


def get_comments(
    wrapper: AzCliWrapper,
    work_item_id: int,
) -> list[dict[str, Any]]:
    """Get comments for a work item via ADO REST API.

    Args:
        wrapper: AzCliWrapper instance (must have org and project set)
        work_item_id: Work item ID

    Returns:
        List of comment objects

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
        f"/_apis/wit/workItems/{work_item_id}/comments?api-version=7.1-preview.4"
    )

    result = wrapper.run(
        ["az", "rest", "--method", "get", "--url", url],
        timeout=30,
    )

    if not result.success:
        handle_error(
            f"Failed to get comments for work item {work_item_id}",
            exit_code=ExitCode.COMMAND_ERROR,
            details=result.stderr,
        )

    try:
        data = json.loads(result.stdout)
        return data.get("comments", [])
    except (json.JSONDecodeError, KeyError) as e:
        handle_error(
            "Failed to parse comments response",
            exit_code=ExitCode.COMMAND_ERROR,
            details=str(e),
        )
        return []  # Never reached


def format_summary(comments: list[dict[str, Any]]) -> str:
    """Format comments as human-readable summary."""
    if not comments:
        return "No comments."

    lines = [f"Comments ({len(comments)}):", "=" * 60]
    for comment in comments:
        author = comment.get("createdBy", {}).get("displayName", "Unknown")
        date = comment.get("createdDate", "Unknown")
        text = comment.get("text", "")
        # Strip HTML tags
        import re

        clean_text = re.sub("<[^<]+?>", "", text)
        lines.append(f"\n[{author} — {date}]")
        lines.append(clean_text[:300])
        if len(text) > 300:
            lines.append("... (truncated)")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Get Azure DevOps work item comments",
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
        comments = get_comments(wrapper, work_item_id)

        if args.format == "json":
            print(json.dumps(comments, indent=2))
        else:
            print(format_summary(comments))

    except Exception as e:
        handle_error(
            f"Unexpected error: {e}",
            exit_code=ExitCode.COMMAND_ERROR,
        )


if __name__ == "__main__":
    main()
