#!/usr/bin/env python3
"""
Tool: get_templates.py

Purpose: Fetch work item templates from Azure DevOps, filtered by type.
         If multiple templates match, present an interactive selector.

Usage:
    python get_templates.py --type Feature --workspace "my-workspace"
    python get_templates.py --type "User Story" --workspace "my-workspace"
    python get_templates.py --type Feature --workspace "my-workspace" --list

Examples:
    # Get Feature template (auto-selects if only one)
    TEMPLATE=$(python get_templates.py --type Feature --workspace "my-board")

    # List available templates without selecting
    python get_templates.py --type Feature --workspace "my-board" --list

Philosophy:
- Standard library + az CLI wrapper
- Searches all teams in the project for templates
- Interactive selector when multiple matches
- Outputs template fields as JSON to stdout
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from common import AzCliWrapper, ExitCode, handle_error, load_config

# Try questionary for arrow navigation; fall back to plain numbered input
try:
    import questionary
    from questionary import Style

    HAS_QUESTIONARY = True
except ImportError:
    HAS_QUESTIONARY = False

_STYLE = None
if HAS_QUESTIONARY:
    _STYLE = Style(
        [
            ("selected", "fg:#00aa44 bold"),
            ("pointer", "fg:#00aa44 bold"),
            ("highlighted", "fg:#ffffff bold"),
            ("answer", "fg:#00aa44"),
        ]
    )


def _list_teams(wrapper: AzCliWrapper, org: str, project: str) -> list[dict]:
    """List all teams in a project."""
    result = wrapper.run(
        ["az", "devops", "team", "list", "--org", org, "--project", project, "--output", "json"],
        timeout=20,
    )
    if not result.success:
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def _fetch_templates_for_team(
    org: str, project: str, team_id: str, team_name: str
) -> list[dict]:
    """Fetch all templates for a specific team."""
    wrapper = AzCliWrapper()
    result = wrapper.run(
        [
            "az",
            "devops",
            "invoke",
            "--area",
            "wit",
            "--resource",
            "templates",
            "--route-parameters",
            f"project={project}",
            f"team={team_id}",
            "--api-version",
            "7.1",
            "--org",
            org,
            "--output",
            "json",
        ],
        timeout=20,
    )
    if not result.success:
        return []
    try:
        data = json.loads(result.stdout)
        templates = data.get("value", [])
        # Tag each template with its source team
        for t in templates:
            t["_team_id"] = team_id
            t["_team_name"] = team_name
        return templates
    except json.JSONDecodeError:
        return []


def _fetch_template_detail(
    org: str, project: str, team_id: str, template_id: str
) -> dict | None:
    """Fetch full template content including field values."""
    wrapper = AzCliWrapper()
    result = wrapper.run(
        [
            "az",
            "devops",
            "invoke",
            "--area",
            "wit",
            "--resource",
            "templates",
            "--route-parameters",
            f"project={project}",
            f"team={team_id}",
            f"templateId={template_id}",
            "--api-version",
            "7.1",
            "--org",
            org,
            "--output",
            "json",
        ],
        timeout=20,
    )
    if not result.success:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def find_templates(
    org: str, project: str, work_item_type: str
) -> list[dict]:
    """Find all templates matching a work item type across all project teams."""
    wrapper = AzCliWrapper()
    teams = _list_teams(wrapper, org, project)
    if not teams:
        return []

    # Fetch templates from all teams in parallel
    all_templates = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {
            pool.submit(
                _fetch_templates_for_team, org, project, t["id"], t["name"]
            ): t
            for t in teams
        }
        for future in as_completed(futures):
            all_templates.extend(future.result())

    # Filter by type
    matched = [t for t in all_templates if t.get("workItemTypeName") == work_item_type]

    # Deduplicate by template ID (same template may appear via nested teams)
    seen = set()
    unique = []
    for t in matched:
        if t["id"] not in seen:
            seen.add(t["id"])
            unique.append(t)

    return unique


def select_template_interactive(templates: list[dict]) -> dict:
    """Present an interactive selector for multiple templates."""
    if HAS_QUESTIONARY:
        choices = [
            questionary.Choice(
                title=f"{t['name']}  ({t['_team_name']})",
                value=t,
            )
            for t in templates
        ]
        answer = questionary.select(
            "Multiple templates found. Which one?",
            choices=choices,
            style=_STYLE,
        ).ask()
        if answer is None:
            sys.exit(1)
        return answer
    else:
        print("\nMultiple templates found:", file=sys.stderr)
        for i, t in enumerate(templates, 1):
            print(f"  {i}. {t['name']}  ({t['_team_name']})", file=sys.stderr)
        while True:
            try:
                raw = input("\nSelect (number): ").strip()
            except (EOFError, KeyboardInterrupt):
                sys.exit(1)
            try:
                n = int(raw)
                if 1 <= n <= len(templates):
                    return templates[n - 1]
            except ValueError:
                pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch work item templates from Azure DevOps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get Feature template
  %(prog)s --type Feature --workspace "my-board"

  # Get Story template
  %(prog)s --type "User Story" --workspace "my-board"

  # List matching templates without selecting
  %(prog)s --type Feature --workspace "my-board" --list
""",
    )
    parser.add_argument(
        "--type",
        required=True,
        help='Work item type to filter templates (e.g., "Feature", "User Story", "Task")',
    )
    parser.add_argument("--workspace", help="Named workspace alias")
    parser.add_argument("--org", help="Azure DevOps organization URL")
    parser.add_argument("--project", help="Project name")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List matching templates and exit (no selection)",
    )
    parser.add_argument(
        "--fields-only",
        action="store_true",
        help="Output only the fields dict (default: full template JSON)",
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

    # Find templates
    print(f"Searching for {args.type} templates in {project}...", file=sys.stderr)
    templates = find_templates(org, project, args.type)

    if not templates:
        handle_error(
            f"No {args.type} templates found in project {project}",
            exit_code=ExitCode.VALIDATION_ERROR,
            details="Templates are team-scoped in ADO. Check that your team has templates defined.",
        )
        return

    # List mode
    if args.list:
        for t in templates:
            print(f"  {t['name']}  (team: {t['_team_name']}, id: {t['id']})", file=sys.stderr)
        print(json.dumps([{"name": t["name"], "id": t["id"], "team": t["_team_name"]} for t in templates]))
        return

    # Select
    if len(templates) == 1:
        selected = templates[0]
        print(f"Using template: {selected['name']}  ({selected['_team_name']})", file=sys.stderr)
    else:
        selected = select_template_interactive(templates)

    # Fetch full template content
    print(f"Fetching template content...", file=sys.stderr)
    detail = _fetch_template_detail(org, project, selected["_team_id"], selected["id"])

    if not detail:
        handle_error(
            f"Failed to fetch template content for '{selected['name']}'",
            exit_code=ExitCode.COMMAND_ERROR,
        )
        return

    # Output
    if args.fields_only:
        print(json.dumps(detail.get("fields", {}), indent=2))
    else:
        print(json.dumps(detail, indent=2))


if __name__ == "__main__":
    main()
