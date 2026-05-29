#!/usr/bin/env python3
"""Fetch pipeline definitions and recent runs for ADO repositories.

Given repository names, finds associated pipelines and their recent run
history (status, duration, result). Used by the rollback drafter to
ground time estimates and deployment status in real data.

Pipeline discovery uses a cascade strategy (A→B→D):
  A. List all ADO pipelines, fuzzy-match names against target repos
  B. Confirm matches by fetching full pipeline definition (checks repo binding)
  C. Fall back to GitHub Actions workflows for any unmatched repos

This approach is thorough rather than fast — it prefers finding all pipelines
over quick partial results.

Usage:
    python get_pipeline_runs.py --repositories my-repo
    python get_pipeline_runs.py --repositories repo-a,repo-b --top 5
    python get_pipeline_runs.py --repositories my-repo --workspace "my-workspace"

Philosophy:
- Standard library + azure CLI wrapper
- Grounded data for release documentation — no guessing
- Thoroughness over speed — find everything
- Self-contained and regeneratable
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from typing import Any

from common import (
    AzCliWrapper,
    ExitCode,
    handle_error,
    load_config,
)


# ---------------------------------------------------------------------------
# Step A: List all pipelines, fuzzy-match against repo names
# ---------------------------------------------------------------------------

def _normalize(name: str) -> str:
    """Normalize a name for fuzzy comparison."""
    return name.lower().strip().replace("-", "").replace("_", "").replace(" ", "")


def _fuzzy_match(pipeline_name: str, repo_name: str) -> bool:
    """Check if a pipeline name is a plausible match for a repo name.

    Matches if either name contains the other as a substring after
    normalization (case-insensitive, ignoring hyphens/underscores).
    """
    pn = _normalize(pipeline_name)
    rn = _normalize(repo_name)
    return rn in pn or pn in rn


def _list_all_pipelines(wrapper: AzCliWrapper) -> list[dict[str, Any]]:
    """Fetch the full list of pipeline definitions in the project.

    Returns:
        List of raw pipeline dicts from az pipelines list
    """
    cmd = ["az", "pipelines", "list", "--output", "json"]

    if wrapper.org:
        cmd.extend(["--org", wrapper.org])
    if wrapper.project:
        cmd.extend(["--project", wrapper.project])

    result = wrapper.run(cmd, timeout=60)
    if not result.success:
        print(
            f"Warning: Could not list pipelines: {result.stderr}",
            file=sys.stderr,
        )
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def _find_candidates(
    all_pipelines: list[dict[str, Any]],
    repo_name: str,
) -> list[dict[str, Any]]:
    """Filter pipeline list to candidates that fuzzy-match a repo name.

    Args:
        all_pipelines: Full list of pipeline dicts
        repo_name: Target repository name

    Returns:
        List of candidate pipeline dicts
    """
    candidates = []
    for p in all_pipelines:
        pname = p.get("name", "")
        if _fuzzy_match(pname, repo_name):
            candidates.append(p)
    return candidates


# ---------------------------------------------------------------------------
# Step B: Confirm match by inspecting full pipeline definition
# ---------------------------------------------------------------------------

def _get_pipeline_definition(
    wrapper: AzCliWrapper,
    pipeline_id: int,
) -> dict[str, Any] | None:
    """Fetch full pipeline definition to inspect the repo binding.

    Args:
        wrapper: AzCliWrapper instance
        pipeline_id: Pipeline definition ID

    Returns:
        Full pipeline definition dict, or None on failure
    """
    cmd = ["az", "pipelines", "show",
           "--id", str(pipeline_id),
           "--output", "json"]

    if wrapper.org:
        cmd.extend(["--org", wrapper.org])
    if wrapper.project:
        cmd.extend(["--project", wrapper.project])

    result = wrapper.run(cmd, timeout=30)
    if not result.success:
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def _confirm_repo_match(
    definition: dict[str, Any],
    repo_name: str,
) -> bool:
    """Check if a pipeline definition is bound to the target repo.

    Inspects the repository field in the definition for name matches
    across Azure Repos, GitHub, and other source providers.

    Args:
        definition: Full pipeline definition
        repo_name: Target repository name (short name, e.g., "my-repo")

    Returns:
        True if the pipeline is bound to a repo matching repo_name
    """
    repo = definition.get("repository", {})
    repo_def_name = repo.get("name", "")

    # Direct match on repo name (Azure Repos or GitHub short name)
    if _normalize(repo_def_name) == _normalize(repo_name):
        return True

    # GitHub repos may appear as "org/repo" — match the repo part
    if "/" in repo_def_name:
        _, _, short = repo_def_name.rpartition("/")
        if _normalize(short) == _normalize(repo_name):
            return True

    # Also check the pipeline name itself as a last resort
    pipeline_name = definition.get("name", "")
    if _normalize(pipeline_name) == _normalize(repo_name):
        return True

    return False


# ---------------------------------------------------------------------------
# Step D: Fall back to GitHub Actions
# ---------------------------------------------------------------------------

def _check_github_actions(
    repo_full_name: str,
) -> list[dict[str, Any]]:
    """Check if a GitHub repo has GitHub Actions workflows.

    Args:
        repo_full_name: Full GitHub repo name (e.g., "org/repo")

    Returns:
        List of workflow dicts with name and path, empty if none or gh unavailable
    """
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repo_full_name}/actions/workflows",
             "--jq", ".workflows[] | {name: .name, path: .path, state: .state}"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []

        workflows = []
        for line in result.stdout.strip().splitlines():
            try:
                workflows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return workflows
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


# ---------------------------------------------------------------------------
# Cascade: A → B → D
# ---------------------------------------------------------------------------

def get_pipelines_for_repo(
    wrapper: AzCliWrapper,
    repository: str,
    all_pipelines: list[dict[str, Any]] | None = None,
    github_full_name: str | None = None,
) -> list[dict[str, Any]]:
    """Find pipelines associated with a repository using cascade discovery.

    Strategy:
      A. Fuzzy-match pipeline names against the repo name
      B. Confirm each candidate by fetching full definition and checking repo binding
      D. If no ADO pipelines found and github_full_name provided, check GitHub Actions

    Args:
        wrapper: AzCliWrapper instance
        repository: Repository short name (e.g., "my-repo")
        all_pipelines: Pre-fetched list of all pipelines (avoids repeated listing)
        github_full_name: Full GitHub repo name for fallback (e.g., "org/repo")

    Returns:
        List of pipeline dicts with id, name, folder, source
    """
    confirmed = []

    # --- Step A: Fuzzy match against all pipelines ---
    if all_pipelines is not None:
        candidates = _find_candidates(all_pipelines, repository)
        print(
            f"  Step A: {len(candidates)} candidate(s) from fuzzy match",
            file=sys.stderr,
        )

        # --- Step B: Confirm each candidate ---
        for candidate in candidates:
            pid = candidate.get("id")
            pname = candidate.get("name", "")
            print(
                f"  Step B: Checking pipeline '{pname}' (ID: {pid})...",
                file=sys.stderr,
            )
            definition = _get_pipeline_definition(wrapper, pid)
            if definition and _confirm_repo_match(definition, repository):
                repo_info = definition.get("repository", {})
                confirmed.append({
                    "id": pid,
                    "name": pname,
                    "folder": candidate.get("folder", ""),
                    "repository": repository,
                    "source": "ado",
                    "repo_type": repo_info.get("type", "unknown"),
                    "repo_name_in_definition": repo_info.get("name", ""),
                })
                print(
                    f"    Confirmed: '{pname}' → {repo_info.get('name', '?')} "
                    f"(type: {repo_info.get('type', '?')})",
                    file=sys.stderr,
                )
            else:
                print(f"    No match for '{pname}'", file=sys.stderr)

    # --- Legacy: also try the direct --repository flag for Azure Repos ---
    if not confirmed:
        for repo_type in ["tfsgit", "github"]:
            cmd = ["az", "pipelines", "list",
                   "--repository", repository,
                   "--repository-type", repo_type,
                   "--output", "json"]
            if wrapper.org:
                cmd.extend(["--org", wrapper.org])
            if wrapper.project:
                cmd.extend(["--project", wrapper.project])

            result = wrapper.run(cmd, timeout=30)
            if result.success:
                try:
                    pipelines = json.loads(result.stdout)
                    for p in pipelines:
                        # Avoid duplicates
                        if not any(c["id"] == p.get("id") for c in confirmed):
                            confirmed.append({
                                "id": p.get("id"),
                                "name": p.get("name", ""),
                                "folder": p.get("folder", ""),
                                "repository": repository,
                                "source": "ado",
                                "repo_type": repo_type,
                            })
                except json.JSONDecodeError:
                    pass

        if confirmed:
            print(
                f"  Found {len(confirmed)} via direct --repository lookup",
                file=sys.stderr,
            )

    # --- Step D: Fall back to GitHub Actions ---
    if not confirmed and github_full_name:
        print(
            f"  Step D: Checking GitHub Actions for {github_full_name}...",
            file=sys.stderr,
        )
        workflows = _check_github_actions(github_full_name)
        if workflows:
            for wf in workflows:
                confirmed.append({
                    "id": None,
                    "name": wf.get("name", ""),
                    "folder": wf.get("path", ""),
                    "repository": repository,
                    "source": "github_actions",
                    "state": wf.get("state", ""),
                })
            print(
                f"    Found {len(workflows)} GitHub Actions workflow(s)",
                file=sys.stderr,
            )
        else:
            print(f"    No GitHub Actions workflows found", file=sys.stderr)

    return confirmed


def get_recent_runs(
    wrapper: AzCliWrapper,
    pipeline_id: int,
    top: int = 5,
) -> list[dict[str, Any]]:
    """Fetch recent runs for a pipeline.

    Args:
        wrapper: AzCliWrapper instance
        pipeline_id: Pipeline definition ID
        top: Number of runs to fetch

    Returns:
        List of run summary dicts
    """
    cmd = ["az", "pipelines", "runs", "list",
           "--pipeline-ids", str(pipeline_id),
           "--top", str(top),
           "--query-order", "FinishTimeDesc",
           "--output", "json"]

    if wrapper.org:
        cmd.extend(["--org", wrapper.org])
    if wrapper.project:
        cmd.extend(["--project", wrapper.project])

    result = wrapper.run(cmd, timeout=30)
    if not result.success:
        print(
            f"Warning: Could not fetch runs for pipeline {pipeline_id}: {result.stderr}",
            file=sys.stderr,
        )
        return []

    try:
        runs = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    summaries = []
    for run in runs:
        start = run.get("startTime", "")
        finish = run.get("finishTime", "")
        duration_minutes = None

        if start and finish:
            try:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                finish_dt = datetime.fromisoformat(finish.replace("Z", "+00:00"))
                duration_minutes = round(
                    (finish_dt - start_dt).total_seconds() / 60, 1
                )
            except (ValueError, TypeError):
                pass

        summaries.append({
            "run_id": run.get("id"),
            "build_number": run.get("buildNumber", ""),
            "status": run.get("status", ""),
            "result": run.get("result", ""),
            "start_time": start,
            "finish_time": finish,
            "duration_minutes": duration_minutes,
            "source_branch": run.get("sourceBranch", "").replace("refs/heads/", ""),
            "reason": run.get("reason", ""),
            "requested_by": run.get("requestedBy", {}).get("displayName", ""),
        })

    return summaries


def compute_stats(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute summary statistics from run history.

    Args:
        runs: List of run summary dicts

    Returns:
        Stats dict with averages and success rate
    """
    if not runs:
        return {"total_runs": 0}

    durations = [
        r["duration_minutes"] for r in runs
        if r["duration_minutes"] is not None
    ]
    succeeded = sum(1 for r in runs if r.get("result") == "succeeded")

    stats = {
        "total_runs": len(runs),
        "succeeded": succeeded,
        "failed": sum(1 for r in runs if r.get("result") == "failed"),
        "success_rate": round(succeeded / len(runs) * 100, 1) if runs else 0,
    }

    if durations:
        stats["avg_duration_minutes"] = round(sum(durations) / len(durations), 1)
        stats["min_duration_minutes"] = min(durations)
        stats["max_duration_minutes"] = max(durations)

    last_successful = next(
        (r for r in runs if r.get("result") == "succeeded"), None
    )
    if last_successful:
        stats["last_successful_run"] = {
            "run_id": last_successful["run_id"],
            "build_number": last_successful["build_number"],
            "finish_time": last_successful["finish_time"],
            "duration_minutes": last_successful["duration_minutes"],
        }

    return stats


def get_pipeline_data_for_repos(
    repositories: list[str],
    org: str,
    project: str,
    top: int = 5,
    github_org: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch pipeline definitions and run history for multiple repos.

    Uses the A→B→D cascade for pipeline discovery:
      A. One-time fetch of all ADO pipelines, fuzzy-match per repo
      B. Confirm candidates via full definition inspection
      D. Fall back to GitHub Actions for unmatched repos

    Args:
        repositories: List of repository short names
        org: Organization URL
        project: Project name
        top: Number of recent runs per pipeline
        github_org: GitHub organization for fallback (e.g., "Alaska-ECommerce")

    Returns:
        List of pipeline data dicts with definitions, runs, and stats
    """
    wrapper = AzCliWrapper(org=org, project=project)

    # Step A (one-time): fetch all pipelines in the project
    print(
        f"Fetching all pipelines in {project}...",
        file=sys.stderr,
    )
    all_pipelines = _list_all_pipelines(wrapper)
    print(
        f"Found {len(all_pipelines)} total pipeline(s) in project",
        file=sys.stderr,
    )

    results = []

    for repo in repositories:
        print(f"\nFinding pipelines for {repo}...", file=sys.stderr)
        github_full_name = f"{github_org}/{repo}" if github_org else None

        pipelines = get_pipelines_for_repo(
            wrapper, repo,
            all_pipelines=all_pipelines,
            github_full_name=github_full_name,
        )

        if not pipelines:
            print(f"  No pipelines found for {repo}", file=sys.stderr)
            results.append({
                "repository": repo,
                "pipelines": [],
                "has_pipelines": False,
            })
            continue

        repo_pipelines = []
        for pipeline in pipelines:
            source = pipeline.get("source", "ado")

            if source == "github_actions":
                # GitHub Actions — no run history via az CLI
                repo_pipelines.append({
                    "pipeline_id": None,
                    "pipeline_name": pipeline["name"],
                    "folder": pipeline["folder"],
                    "source": "github_actions",
                    "state": pipeline.get("state", ""),
                    "recent_runs": [],
                    "stats": {"total_runs": 0, "note": "GitHub Actions — use gh CLI for run history"},
                })
                continue

            # ADO pipeline — fetch runs
            print(
                f"  Fetching runs for pipeline '{pipeline['name']}' "
                f"(ID: {pipeline['id']})...",
                file=sys.stderr,
            )
            runs = get_recent_runs(wrapper, pipeline["id"], top=top)
            stats = compute_stats(runs)

            repo_pipelines.append({
                "pipeline_id": pipeline["id"],
                "pipeline_name": pipeline["name"],
                "folder": pipeline["folder"],
                "source": "ado",
                "repo_type": pipeline.get("repo_type", ""),
                "recent_runs": runs,
                "stats": stats,
            })

        results.append({
            "repository": repo,
            "pipelines": repo_pipelines,
            "has_pipelines": True,
        })
        print(
            f"  Found {len(pipelines)} pipeline(s) for {repo}",
            file=sys.stderr,
        )

    return results


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch pipeline definitions and recent runs for ADO repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get pipelines and runs for a single repo
  %(prog)s --repositories my-repo

  # Multiple repos
  %(prog)s --repositories repo-a,repo-b,repo-c

  # Fetch more run history
  %(prog)s --repositories my-repo --top 10

  # With GitHub Actions fallback
  %(prog)s --repositories my-repo --github-org Alaska-ECommerce
""",
    )

    parser.add_argument(
        "--repositories",
        required=True,
        help="Comma-separated repository names",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of recent runs to fetch per pipeline (default: 5)",
    )
    parser.add_argument(
        "--github-org",
        help="GitHub organization for fallback discovery (e.g., Alaska-ECommerce)",
    )
    parser.add_argument("--workspace", help="Named workspace alias")
    parser.add_argument("--org", help="Azure DevOps organization URL")
    parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    repos = [r.strip() for r in args.repositories.split(",") if r.strip()]
    if not repos:
        handle_error("No repositories specified", ExitCode.VALIDATION_ERROR)

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
        results = get_pipeline_data_for_repos(
            repos, org, project, args.top,
            github_org=args.github_org,
        )
        print(json.dumps(results, indent=2))
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        handle_error(f"Unexpected error: {e}", ExitCode.COMMAND_ERROR)


if __name__ == "__main__":
    main()


__all__ = ["get_pipeline_data_for_repos", "get_pipelines_for_repo", "get_recent_runs", "main"]
