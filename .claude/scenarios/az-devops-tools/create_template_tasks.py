#!/usr/bin/env python3
"""Create mandatory template tasks on a parent story.

Fetches Task-type templates from ADO for the team, then creates each one
as a child task on the specified parent story. Tasks inherit the parent's
iteration path and area path.

Usage:
    python create_template_tasks.py --parent-id 12345 --workspace "my-workspace"
    python create_template_tasks.py --parent-id 12345 --workspace "my-workspace" --dry-run

Philosophy:
- Single responsibility: fetch templates + create tasks in one step
- Inherits parent fields automatically (iteration, area)
- Fails fast with clear errors
- Composable with other tools
"""

import argparse
import json
import sys

from common import AzCliWrapper, ExitCode, handle_error, load_config
from create_work_item import create_work_item
from get_templates import find_templates
from get_work_item import get_work_item_details


def create_template_tasks(
    parent_id: int,
    org: str,
    project: str,
    dry_run: bool = False,
) -> list[dict]:
    """Create all template tasks for a parent story.

    Args:
        parent_id: Parent work item ID (must be a User Story)
        org: Organization URL
        project: Project name
        dry_run: If True, list what would be created without creating

    Returns:
        List of created task dicts with id, title, url
    """
    # Fetch parent story (get_work_item_details exits on failure)
    wrapper = AzCliWrapper(org=org, project=project)
    parent = get_work_item_details(wrapper, parent_id, include_relations=True)

    fields = parent.get("fields", {})
    parent_type = fields.get("System.WorkItemType", "")
    if parent_type != "User Story":
        raise ValueError(
            f"Work item {parent_id} is a {parent_type}, not a User Story. "
            "Tasks always live under a User Story."
        )

    # Extract fields to inherit
    iteration = fields.get("System.IterationPath", "")
    area = fields.get("System.AreaPath", "")

    # Check for existing child tasks to avoid duplicates on re-run
    existing_titles = set()
    for rel in parent.get("relations") or []:
        if rel.get("rel") == "System.LinkTypes.Hierarchy-Forward":
            child_url = rel.get("url", "")
            if child_url:
                try:
                    child_id = int(child_url.rstrip("/").split("/")[-1])
                    child = get_work_item_details(wrapper, child_id)
                    child_fields = child.get("fields", {})
                    child_type = child_fields.get("System.WorkItemType", "")
                    if child_type == "Task":
                        existing_titles.add(child_fields.get("System.Title", ""))
                except Exception:
                    pass

    # Find Task templates
    templates = find_templates(org, project, "Task")
    if not templates:
        print("No Task templates found for this project.", file=sys.stderr)
        return []

    print(f"Found {len(templates)} Task template(s):", file=sys.stderr)
    for t in templates:
        print(f"  - {t['name']} ({t['_team_name']})", file=sys.stderr)

    if dry_run:
        print("\nDry run — would create:", file=sys.stderr)
        for t in templates:
            print(f"  Task: {t['name']} (parent: {parent_id})", file=sys.stderr)
            if iteration:
                print(f"    Iteration: {iteration}", file=sys.stderr)
            if area:
                print(f"    Area: {area}", file=sys.stderr)
        return []

    # Create each template task (skip if already exists)
    created = []
    skipped = []
    for t in templates:
        if t["name"] in existing_titles:
            skipped.append(t["name"])
            print(f"  Skipped (already exists): {t['name']}", file=sys.stderr)
            continue
        try:
            work_item = create_work_item(
                title=t["name"],
                work_item_type="Task",
                org=org,
                project=project,
                iteration=iteration or None,
                area=area or None,
                parent_id=parent_id,
            )
            task_info = {
                "id": work_item["id"],
                "title": t["name"],
                "url": work_item.get("url", ""),
            }
            created.append(task_info)
            print(f"  Created: {t['name']} (ID: {work_item['id']})", file=sys.stderr)
        except Exception as e:
            print(f"  WARNING: Failed to create '{t['name']}': {e}", file=sys.stderr)

    if skipped:
        print(f"  Skipped {len(skipped)} existing template task(s)", file=sys.stderr)

    return created


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create mandatory template tasks on a parent story",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create template tasks on story #12345
  %(prog)s --parent-id 12345 --workspace "my-board"

  # Dry run — show what would be created
  %(prog)s --parent-id 12345 --workspace "my-board" --dry-run
""",
    )
    parser.add_argument(
        "--parent-id",
        type=int,
        required=True,
        help="Parent work item ID (must be a User Story)",
    )
    parser.add_argument("--workspace", help="Named workspace alias")
    parser.add_argument("--org", help="Azure DevOps organization URL")
    parser.add_argument("--project", help="Project name")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating",
    )

    args = parser.parse_args()

    # Resolve config
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
        created = create_template_tasks(
            parent_id=args.parent_id,
            org=org,
            project=project,
            dry_run=args.dry_run,
        )

        # Output JSON summary to stdout
        print(json.dumps(created, indent=2))

        if created:
            print(
                f"\nCreated {len(created)} template task(s) under story #{args.parent_id}",
                file=sys.stderr,
            )
        sys.exit(ExitCode.SUCCESS)

    except ValueError as e:
        handle_error(str(e), ExitCode.VALIDATION_ERROR)
    except RuntimeError as e:
        handle_error(str(e), ExitCode.COMMAND_ERROR)
    except Exception as e:
        handle_error(f"Unexpected error: {e}", ExitCode.COMMAND_ERROR)


if __name__ == "__main__":
    main()


__all__ = ["create_template_tasks", "main"]
