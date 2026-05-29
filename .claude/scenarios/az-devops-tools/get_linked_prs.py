#!/usr/bin/env python3
"""Fetch pull requests linked to ADO work items.

Given one or more work item IDs, fetches each item's relations, extracts
PR links (both Azure Repos and GitHub), and retrieves PR details (title,
repo, branches, status, diff stats). Returns structured JSON to stdout.

Supports two PR link types:
- Azure Repos PRs (vstfs:///Git/PullRequestId/...) — fetched via az CLI
- GitHub PRs (vstfs:///GitHub/PullRequest/...) — fetched via gh CLI

Usage:
    python get_linked_prs.py --ids 12345
    python get_linked_prs.py --ids 12345,12346,12347
    python get_linked_prs.py --ids 12345 --workspace "my-workspace"
    python get_linked_prs.py --ids 12345 --detail

Philosophy:
- Standard library + azure CLI wrapper + gh CLI for GitHub PRs
- Reusable across CR, CRAM, and Proof of Testing workflows
- Fail-fast validation, clear errors
- Self-contained and regeneratable
"""

import argparse
import json
import re
import subprocess
import sys
from typing import Any

from common import (
    AzCliWrapper,
    ExitCode,
    handle_error,
    load_config,
    validate_work_item_id,
)
from get_work_item import get_work_item_details


# URL pattern for extracting PR ID and repo from vstfs artifact links
# Format: vstfs:///Git/PullRequestId/<project-id>/<repo-id>/<pr-id>
VSTFS_PR_PATTERN = re.compile(
    r"vstfs:///Git/PullRequestId/[^/]+/([^/]+)/(\d+)"
)

# GitHub PR artifact link pattern (linked via ADO GitHub integration)
# Format: vstfs:///GitHub/PullRequest/<repo-connection-id>%2f<pr-number>
GITHUB_PR_PATTERN = re.compile(
    r"vstfs:///GitHub/PullRequest/([a-f0-9-]+)%2[fF](\d+)"
)

# REST API URL pattern for PR links
# Format: https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullRequests/{id}
REST_PR_PATTERN = re.compile(
    r"_apis/git/repositories/([^/]+)/pullRequests/(\d+)"
)


def extract_pr_refs_from_relations(relations: list[dict]) -> list[dict[str, str]]:
    """Extract PR references from work item relations.

    Args:
        relations: List of relation dicts from work item

    Returns:
        List of dicts with repo_id and pr_id keys
    """
    pr_refs = []
    seen = set()

    for rel in relations:
        rel_type = rel.get("rel", "")
        url = rel.get("url", "")
        name = rel.get("attributes", {}).get("name", "")

        # Check ADO Git artifact links (PRs in Azure Repos)
        if rel_type == "ArtifactLink" and "PullRequestId" in url:
            match = VSTFS_PR_PATTERN.search(url)
            if match:
                repo_id, pr_id = match.group(1), match.group(2)
                key = f"{repo_id}/{pr_id}"
                if key not in seen:
                    seen.add(key)
                    pr_refs.append({"repo_id": repo_id, "pr_id": pr_id})
            continue

        # Check GitHub PR artifact links (PRs linked via ADO-GitHub integration)
        if rel_type == "ArtifactLink" and "GitHub/PullRequest" in url:
            match = GITHUB_PR_PATTERN.search(url)
            if match:
                connection_id, pr_number = match.group(1), match.group(2)
                key = f"github/{connection_id}/{pr_number}"
                if key not in seen:
                    seen.add(key)
                    pr_refs.append({
                        "repo_id": connection_id,
                        "pr_id": pr_number,
                        "source": "github",
                    })
            continue

        # Check REST API style links
        if "pullRequests" in url:
            match = REST_PR_PATTERN.search(url)
            if match:
                repo_id, pr_id = match.group(1), match.group(2)
                key = f"{repo_id}/{pr_id}"
                if key not in seen:
                    seen.add(key)
                    pr_refs.append({"repo_id": repo_id, "pr_id": pr_id})
            continue

        # Check by relation name
        if "pull request" in name.lower():
            # Try to extract from URL
            match = REST_PR_PATTERN.search(url)
            if match:
                repo_id, pr_id = match.group(1), match.group(2)
                key = f"{repo_id}/{pr_id}"
                if key not in seen:
                    seen.add(key)
                    pr_refs.append({"repo_id": repo_id, "pr_id": pr_id})

    return pr_refs


def get_pr_details(
    wrapper: AzCliWrapper,
    pr_id: str,
    repo_id: str | None = None,
) -> dict[str, Any] | None:
    """Fetch PR details from ADO.

    Args:
        wrapper: AzCliWrapper instance
        pr_id: Pull request ID
        repo_id: Repository ID or name (optional)

    Returns:
        PR data dict or None on failure
    """
    cmd = ["repos", "pr", "show", "--id", pr_id, "--output", "json"]
    if repo_id:
        cmd.extend(["--repository", repo_id])

    result = wrapper.devops_command(cmd, timeout=30)
    if not result.success:
        print(
            f"  Warning: Could not fetch PR #{pr_id}: {result.stderr}",
            file=sys.stderr,
        )
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def format_pr_summary(pr_data: dict[str, Any]) -> dict[str, Any]:
    """Format raw PR data into a clean summary.

    Args:
        pr_data: Raw PR data from az repos pr show

    Returns:
        Clean summary dict
    """
    repo = pr_data.get("repository", {})
    created_by = pr_data.get("createdBy", {})

    # Truncate long descriptions to keep context manageable
    description = pr_data.get("description", "") or ""
    if len(description) > 2000:
        description = description[:2000] + "... (truncated)"

    return {
        "pr_id": pr_data.get("pullRequestId"),
        "title": pr_data.get("title", ""),
        "description": description,
        "status": pr_data.get("status", ""),
        "source_branch": pr_data.get("sourceRefName", "").replace("refs/heads/", ""),
        "target_branch": pr_data.get("targetRefName", "").replace("refs/heads/", ""),
        "repository": repo.get("name", ""),
        "repository_id": repo.get("id", ""),
        "created_by": created_by.get("displayName", ""),
        "creation_date": pr_data.get("creationDate", ""),
        "merge_status": pr_data.get("mergeStatus", ""),
        "is_draft": pr_data.get("isDraft", False),
        "url": pr_data.get("url", ""),
    }


def resolve_github_repo(
    pr_number: str,
    work_item_id: int | None = None,
) -> str | None:
    """Resolve the GitHub org/repo for a PR using gh search.

    Searches for PRs with the AB#<work_item_id> convention in the title,
    then matches by PR number.

    Args:
        pr_number: PR number to find
        work_item_id: ADO work item ID (for title search)

    Returns:
        Full repo name (e.g., "Alaska-ECommerce/PlatformFrontDoor") or None
    """
    if not work_item_id:
        return None

    try:
        result = subprocess.run(
            [
                "gh", "search", "prs",
                f"AB#{work_item_id}",
                "--json", "number,repository",
                "--limit", "20",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None

        prs = json.loads(result.stdout)
        for pr in prs:
            if pr.get("number") == int(pr_number):
                repo = pr.get("repository", {})
                return repo.get("nameWithOwner") or repo.get("name")

    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass

    return None


def get_github_pr_details(
    pr_number: str,
    repo_full_name: str,
    include_files: bool = False,
) -> dict[str, Any] | None:
    """Fetch PR details from GitHub via gh CLI.

    Args:
        pr_number: PR number
        repo_full_name: Full repo name (e.g., "Alaska-ECommerce/PlatformFrontDoor")
        include_files: If True, include file change details

    Returns:
        PR data dict matching the same shape as format_pr_summary output, or None
    """
    fields = (
        "number,title,state,headRefName,baseRefName,"
        "changedFiles,additions,deletions,author,createdAt,"
        "mergedAt,isDraft,url,body"
    )
    if include_files:
        fields += ",files"

    try:
        result = subprocess.run(
            [
                "gh", "pr", "view", pr_number,
                "--repo", repo_full_name,
                "--json", fields,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(
                f"  Warning: Could not fetch GitHub PR #{pr_number} "
                f"from {repo_full_name}: {result.stderr.strip()}",
                file=sys.stderr,
            )
            return None

        return json.loads(result.stdout)

    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(
            f"  Warning: Error fetching GitHub PR #{pr_number}: {e}",
            file=sys.stderr,
        )
        return None


def format_github_pr_summary(
    pr_data: dict[str, Any],
    repo_full_name: str,
) -> dict[str, Any]:
    """Format GitHub PR data into the same shape as ADO PR summaries.

    Args:
        pr_data: Raw PR data from gh pr view
        repo_full_name: Full repo name (org/repo)

    Returns:
        Clean summary dict matching format_pr_summary output shape
    """
    # Map GitHub state names to ADO-style status
    state = pr_data.get("state", "")
    status_map = {"MERGED": "completed", "CLOSED": "abandoned", "OPEN": "active"}
    status = status_map.get(state, state.lower())

    # Truncate long descriptions
    description = pr_data.get("body", "") or ""
    if len(description) > 2000:
        description = description[:2000] + "... (truncated)"

    repo_name = repo_full_name.split("/")[-1] if "/" in repo_full_name else repo_full_name

    summary = {
        "pr_id": pr_data.get("number"),
        "title": pr_data.get("title", ""),
        "description": description,
        "status": status,
        "source_branch": pr_data.get("headRefName", ""),
        "target_branch": pr_data.get("baseRefName", ""),
        "repository": repo_name,
        "repository_id": repo_full_name,
        "created_by": pr_data.get("author", {}).get("login", ""),
        "creation_date": pr_data.get("createdAt", ""),
        "merge_status": "succeeded" if state == "MERGED" else "",
        "is_draft": pr_data.get("isDraft", False),
        "url": pr_data.get("url", ""),
        "source": "github",
        "additions": pr_data.get("additions", 0),
        "deletions": pr_data.get("deletions", 0),
    }

    # Include file changes if present
    files = pr_data.get("files")
    if files is not None:
        summary["file_changes"] = [
            {
                "path": f.get("path", ""),
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
            }
            for f in files
        ]
        summary["files_changed_count"] = len(files)

    return summary


def get_pr_file_changes(
    wrapper: AzCliWrapper,
    pr_id: str,
    repository_id: str,
    org: str,
    project: str,
) -> list[dict[str, str]] | None:
    """Fetch the list of files changed in a PR via ADO REST API.

    Args:
        wrapper: AzCliWrapper instance
        pr_id: Pull request ID
        repository_id: Repository ID (GUID)
        org: Organization URL
        project: Project name

    Returns:
        List of file change dicts, or None on failure
    """
    import urllib.parse

    api_version = "7.1-preview.1"
    url = (
        f"{org}/{urllib.parse.quote(project, safe='')}/"
        f"_apis/git/repositories/{repository_id}/"
        f"pullRequests/{pr_id}/iterations?api-version={api_version}"
    )

    result = wrapper.run(
        ["az", "rest", "--method", "get", "--url", url, "--output", "json"],
        timeout=30,
    )

    if not result.success:
        print(
            f"  Warning: Could not fetch iterations for PR #{pr_id}: {result.stderr}",
            file=sys.stderr,
        )
        return None

    try:
        iterations = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    # Get the latest iteration's changes
    iteration_list = iterations.get("value", [])
    if not iteration_list:
        return []

    latest_iteration = iteration_list[-1]["id"]

    # Fetch changes for the latest iteration
    changes_url = (
        f"{org}/{urllib.parse.quote(project, safe='')}/"
        f"_apis/git/repositories/{repository_id}/"
        f"pullRequests/{pr_id}/iterations/{latest_iteration}/"
        f"changes?api-version={api_version}"
    )

    changes_result = wrapper.run(
        ["az", "rest", "--method", "get", "--url", changes_url, "--output", "json"],
        timeout=30,
    )

    if not changes_result.success:
        print(
            f"  Warning: Could not fetch file changes for PR #{pr_id}: {changes_result.stderr}",
            file=sys.stderr,
        )
        return None

    try:
        changes_data = json.loads(changes_result.stdout)
    except json.JSONDecodeError:
        return None

    file_changes = []
    for change in changes_data.get("changeEntries", []):
        item = change.get("item", {})
        file_changes.append({
            "path": item.get("path", ""),
            "change_type": change.get("changeType", ""),
            "type": "folder" if item.get("isFolder") else "file",
        })

    return [fc for fc in file_changes if fc["type"] == "file"]


def get_linked_prs(
    work_item_ids: list[int],
    org: str,
    project: str,
    detail: bool = False,
) -> dict[str, Any]:
    """Fetch all PRs linked to a set of work items.

    Args:
        work_item_ids: List of work item IDs to check
        org: Organization URL
        project: Project name
        detail: If True, also fetch file changes per PR

    Returns:
        Dict with work_items (mapping of ID to PR list) and all_prs (deduplicated list)
    """
    wrapper = AzCliWrapper(org=org, project=project)
    work_item_prs: dict[int, list[dict]] = {}
    all_prs: dict[str, dict] = {}  # keyed by dedup key (source/repo/pr_id)

    for wi_id in work_item_ids:
        print(f"Fetching relations for work item #{wi_id}...", file=sys.stderr)
        try:
            work_item = get_work_item_details(
                wrapper, wi_id, include_relations=True
            )
        except SystemExit:
            print(
                f"  Warning: Could not fetch work item #{wi_id}, skipping",
                file=sys.stderr,
            )
            work_item_prs[wi_id] = []
            continue

        relations = work_item.get("relations") or []
        pr_refs = extract_pr_refs_from_relations(relations)

        wi_pr_list = []
        for ref in pr_refs:
            is_github = ref.get("source") == "github"
            # Dedup key includes source + repo/connection_id + PR number
            # (GitHub PR numbers are per-repo, so can't dedup on number alone)
            dedup_key = f"{'github' if is_github else 'ado'}/{ref['repo_id']}/{ref['pr_id']}"

            if dedup_key in all_prs:
                wi_pr_list.append(all_prs[dedup_key])
                continue

            if is_github:
                # GitHub PR — resolve repo via gh search, then fetch details
                print(
                    f"  Resolving GitHub PR #{ref['pr_id']} (connection {ref['repo_id'][:8]}...)...",
                    file=sys.stderr,
                )
                repo_full_name = resolve_github_repo(ref["pr_id"], wi_id)
                if not repo_full_name:
                    print(
                        f"  Warning: Could not resolve GitHub repo for PR #{ref['pr_id']}",
                        file=sys.stderr,
                    )
                    continue

                print(
                    f"  Fetching GitHub PR #{ref['pr_id']} from {repo_full_name}...",
                    file=sys.stderr,
                )
                pr_data = get_github_pr_details(
                    ref["pr_id"], repo_full_name, include_files=detail
                )
                if pr_data:
                    summary = format_github_pr_summary(pr_data, repo_full_name)
                    all_prs[dedup_key] = summary
                    wi_pr_list.append(summary)
            else:
                # Azure Repos PR — existing flow
                print(f"  Fetching PR #{ref['pr_id']}...", file=sys.stderr)
                pr_data = get_pr_details(wrapper, ref["pr_id"], ref.get("repo_id"))
                if pr_data:
                    summary = format_pr_summary(pr_data)

                    if detail:
                        repo_id = summary.get("repository_id", "")
                        if repo_id:
                            print(
                                f"    Fetching file changes for PR #{ref['pr_id']}...",
                                file=sys.stderr,
                            )
                            file_changes = get_pr_file_changes(
                                wrapper, ref["pr_id"], repo_id, org, project
                            )
                            if file_changes is not None:
                                summary["file_changes"] = file_changes
                                summary["files_changed_count"] = len(file_changes)
                            else:
                                summary["file_changes"] = []
                                summary["files_changed_count"] = 0

                    all_prs[dedup_key] = summary
                    wi_pr_list.append(summary)

        work_item_prs[wi_id] = wi_pr_list
        print(
            f"  Found {len(wi_pr_list)} PR(s) for #{wi_id}",
            file=sys.stderr,
        )

    return {
        "work_items": {str(k): v for k, v in work_item_prs.items()},
        "all_prs": list(all_prs.values()),
        "total_prs": len(all_prs),
        "total_work_items": len(work_item_ids),
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch pull requests linked to ADO work items",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get PRs for a single work item
  %(prog)s --ids 12345

  # Get PRs for multiple work items (e.g., all stories under a feature)
  %(prog)s --ids 12345,12346,12347

  # With workspace
  %(prog)s --ids 12345 --workspace "my-board"

  # Include file changes and full descriptions
  %(prog)s --ids 12345 --detail
""",
    )

    parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated work item IDs",
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

    # Parse and validate IDs
    try:
        work_item_ids = [
            validate_work_item_id(id_str.strip())
            for id_str in args.ids.split(",")
        ]
    except ValueError as e:
        handle_error(str(e), exit_code=ExitCode.VALIDATION_ERROR)
        return

    # Load config
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
        result = get_linked_prs(work_item_ids, org, project, detail=args.detail)
        print(json.dumps(result, indent=2))
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        handle_error(f"Unexpected error: {e}", ExitCode.COMMAND_ERROR)


if __name__ == "__main__":
    main()


__all__ = ["get_linked_prs", "extract_pr_refs_from_relations", "main"]
