#!/usr/bin/env python3
"""Fetch a file from an ADO Git repository without cloning.

Uses the ADO REST API (via az rest) to read file contents from a
repository by path. Useful for reading deployment.yaml, pipeline
configs, or any file from repos referenced in PRs.

Usage:
    python get_repo_file.py --repository my-repo --path deployment.yaml
    python get_repo_file.py --repository my-repo --path src/config.yaml --branch main
    python get_repo_file.py --repository my-repo --path deployment.yaml --workspace "my-workspace"

Philosophy:
- Standard library + azure CLI wrapper
- Uses az rest for authenticated ADO REST API access
- Self-contained and regeneratable
"""

import argparse
import json
import sys
import urllib.parse

from common import (
    AzCliWrapper,
    ExitCode,
    handle_error,
    load_config,
)


def get_repo_file(
    org: str,
    project: str,
    repository: str,
    file_path: str,
    branch: str = "main",
) -> str | None:
    """Fetch file content from an ADO Git repository.

    Uses the ADO REST API: GET {org}/{project}/_apis/git/repositories/{repo}/items

    Args:
        org: Organization URL (e.g. https://dev.azure.com/myorg)
        project: Project name
        repository: Repository name or ID
        file_path: Path to file in the repo (e.g. deployment.yaml)
        branch: Branch to read from (default: main)

    Returns:
        File content as string, or None if not found
    """
    wrapper = AzCliWrapper()

    # Build the REST API URL
    # Encode the file path for URL safety
    encoded_path = urllib.parse.quote(file_path, safe="")
    api_version = "7.1-preview.1"
    url = (
        f"{org}/{urllib.parse.quote(project, safe='')}/"
        f"_apis/git/repositories/{urllib.parse.quote(repository, safe='')}/"
        f"items?path={encoded_path}"
        f"&versionDescriptor.version={urllib.parse.quote(branch, safe='')}"
        f"&versionDescriptor.versionType=branch"
        f"&includeContent=true"
        f"&api-version={api_version}"
    )

    result = wrapper.run(
        ["az", "rest", "--method", "get", "--url", url, "--output", "json"],
        timeout=30,
    )

    if not result.success:
        if "404" in result.stderr or "does not exist" in result.stderr.lower():
            return None
        print(
            f"Warning: Failed to fetch {file_path} from {repository}: {result.stderr}",
            file=sys.stderr,
        )
        return None

    try:
        data = json.loads(result.stdout)
        return data.get("content", "")
    except json.JSONDecodeError:
        # az rest with --output json may return raw content for text files
        return result.stdout if result.stdout else None


def get_repo_files_bulk(
    org: str,
    project: str,
    repos_and_paths: list[dict[str, str]],
    branch: str = "main",
) -> dict[str, str | None]:
    """Fetch files from multiple repos.

    Args:
        org: Organization URL
        project: Project name
        repos_and_paths: List of {"repository": name, "path": file_path}
        branch: Branch to read from

    Returns:
        Dict mapping "repo:path" to file content (None if not found)
    """
    results = {}
    for item in repos_and_paths:
        repo = item["repository"]
        path = item["path"]
        key = f"{repo}:{path}"
        print(f"Fetching {path} from {repo}...", file=sys.stderr)
        content = get_repo_file(org, project, repo, path, branch)
        results[key] = content
        if content is None:
            print(f"  Not found: {path} in {repo}", file=sys.stderr)
        else:
            print(f"  Found: {path} ({len(content)} chars)", file=sys.stderr)
    return results


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch a file from an ADO Git repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Read deployment.yaml from a repo
  %(prog)s --repository my-repo --path deployment.yaml

  # Read from a specific branch
  %(prog)s --repository my-repo --path deployment.yaml --branch develop

  # Read deployment.yaml from multiple repos (comma-separated)
  %(prog)s --repository repo-a,repo-b,repo-c --path deployment.yaml
""",
    )

    parser.add_argument(
        "--repository", "-r",
        required=True,
        help="Repository name(s), comma-separated for multiple",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="File path within the repository",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch to read from (default: main)",
    )
    parser.add_argument("--workspace", help="Named workspace alias")
    parser.add_argument("--org", help="Azure DevOps organization URL")
    parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    config = load_config(workspace=args.workspace)
    org = args.org or config.get("org")
    project = args.project or config.get("project")

    if not org or not project:
        handle_error(
            "Organization and project must be configured",
            exit_code=ExitCode.CONFIG_ERROR,
            details="Use --workspace, --org/--project, or set AZURE_DEVOPS_ORG_URL and AZURE_DEVOPS_PROJECT",
        )

    repos = [r.strip() for r in args.repository.split(",") if r.strip()]

    try:
        # Always output an array for consistent downstream parsing
        items = [{"repository": r, "path": args.path} for r in repos]
        results = get_repo_files_bulk(org, project, items, args.branch)
        output = []
        for key, content in results.items():
            repo, path = key.split(":", 1)
            output.append({
                "repository": repo,
                "path": path,
                "found": content is not None,
                "content": content,
            })
        print(json.dumps(output, indent=2))

        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        handle_error(f"Unexpected error: {e}", ExitCode.COMMAND_ERROR)


if __name__ == "__main__":
    main()


__all__ = ["get_repo_file", "get_repo_files_bulk", "main"]
