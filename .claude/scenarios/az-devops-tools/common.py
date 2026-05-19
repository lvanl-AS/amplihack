"""Common utilities for Azure DevOps CLI tools.

Philosophy:
- Standard library only for core utilities
- Clear error messages with actionable guidance
- No swallowed exceptions
- Reusable, composable functions

Public API:
    AzCliWrapper: Safe wrapper for az CLI commands
    load_config: Load Azure DevOps configuration
    handle_error: Standardized error handling
    ExitCode: Standard exit codes
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any


class ExitCode(IntEnum):
    """Standard exit codes for all tools."""

    SUCCESS = 0
    AUTH_ERROR = 1
    CONFIG_ERROR = 2
    COMMAND_ERROR = 3
    VALIDATION_ERROR = 4


@dataclass
class CommandResult:
    """Result from az CLI command execution."""

    returncode: int
    stdout: str
    stderr: str
    success: bool

    @property
    def json_output(self) -> dict[str, Any] | None:
        """Parse stdout as JSON if possible."""
        if not self.stdout:
            return None
        try:
            return json.loads(self.stdout)
        except json.JSONDecodeError:
            return None


class AzCliWrapper:
    """Safe wrapper for Azure DevOps CLI commands.

    Provides consistent error handling, logging, and result parsing.
    """

    def __init__(self, org: str | None = None, project: str | None = None):
        """Initialize wrapper with optional default org/project."""
        self.org = org
        self.project = project

    def run(
        self,
        command: list[str],
        timeout: int = 30,
        capture_output: bool = True,
    ) -> CommandResult:
        """Execute az CLI command with error handling.

        Args:
            command: Command and arguments (e.g., ["az", "devops", "project", "list"])
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            CommandResult with execution details

        Raises:
            FileNotFoundError: If az CLI not installed
            subprocess.TimeoutExpired: If command times out
        """
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
            )

            return CommandResult(
                returncode=result.returncode,
                stdout=result.stdout.strip() if result.stdout else "",
                stderr=result.stderr.strip() if result.stderr else "",
                success=result.returncode == 0,
            )

        except FileNotFoundError:
            raise FileNotFoundError(
                "Azure CLI (az) not found. Install from: "
                "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
            )

        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired(
                cmd=command,
                timeout=timeout,
            )

    def devops_command(
        self,
        subcommand: list[str],
        additional_args: list[str] | None = None,
        timeout: int = 30,
    ) -> CommandResult:
        """Execute az devops command with default org/project.

        Use for organization-level commands: project list, configure, wiki, etc.
        For work items and boards operations, use boards_command() instead.

        Args:
            subcommand: Devops subcommand (e.g., ["project", "list"])
            additional_args: Additional arguments
            timeout: Command timeout

        Returns:
            CommandResult with execution details
        """
        command = ["az", "devops"] + subcommand

        # Add default org/project if set
        if self.org:
            command.extend(["--org", self.org])
        if self.project:
            command.extend(["--project", self.project])

        if additional_args:
            command.extend(additional_args)

        return self.run(command, timeout=timeout)

    def boards_command(
        self,
        subcommand: list[str],
        additional_args: list[str] | None = None,
        timeout: int = 30,
    ) -> CommandResult:
        """Execute az boards command with default org/project.

        Use for work item operations: query, work-item show/create/update/delete,
        work-item relation, area, iteration.

        Args:
            subcommand: Boards subcommand (e.g., ["work-item", "show", "--id", "123"])
            additional_args: Additional arguments
            timeout: Command timeout

        Returns:
            CommandResult with execution details
        """
        command = ["az", "boards"] + subcommand

        if self.org:
            command.extend(["--org", self.org])
        if self.project:
            command.extend(["--project", self.project])

        if additional_args:
            command.extend(additional_args)

        return self.run(command, timeout=timeout)


def _load_dotenv() -> None:
    """Load .env file into os.environ without overriding existing vars.

    Searches current directory, then walks up from the script location
    (up to 5 levels) to find a .env file. Only sets variables not already
    present in the environment. Never logs or prints values.
    """
    candidates = [Path.cwd()]
    script_dir = Path(__file__).resolve().parent
    for _ in range(5):
        candidates.append(script_dir)
        script_dir = script_dir.parent

    env_path = None
    for candidate in candidates:
        p = candidate / ".env"
        if p.is_file():
            env_path = p
            break

    if not env_path:
        return

    try:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            # Never override real environment variables
            if key and key not in os.environ:
                os.environ[key] = value
    except OSError:
        pass  # Silent — env vars or config file will be tried next


def load_config(
    config_file: str | None = None,
    workspace: str | None = None,
) -> dict[str, str]:
    """Load Azure DevOps configuration.

    Loads from (in priority order):
    1. .env file (loaded into env without overriding existing vars)
    2. Named workspace in config file (~/.azure-devops-tools.json)
    3. Flat config file values
    4. Environment variables (AZURE_DEVOPS_ORG_URL or ADO_ORG, AZURE_DEVOPS_PROJECT)
    5. az devops configure --list output

    Args:
        config_file: Path to JSON config file (optional, defaults to ~/.azure-devops-tools.json)
        workspace: Named workspace alias to resolve from config file

    Returns:
        Dictionary with org, project, and optionally area_path keys
    """
    _load_dotenv()
    config = {}
    default_config_path = Path.home() / ".azure-devops-tools.json"

    # Determine config file path
    config_path = Path(config_file) if config_file else default_config_path

    # Try config file first
    if config_path.exists():
        try:
            raw = json.loads(config_path.read_text())

            # Check for workspace support
            if "workspaces" in raw:
                # Resolve workspace name: explicit arg > default > None
                ws_name = workspace or raw.get("default")
                if ws_name and ws_name in raw["workspaces"]:
                    ws = raw["workspaces"][ws_name]
                    config["org"] = ws.get("org", "")
                    config["project"] = ws.get("project", "")
                    if ws.get("area_path"):
                        config["area_path"] = ws["area_path"]
                elif ws_name:
                    print(
                        f"Warning: Workspace '{ws_name}' not found in config. "
                        f"Available: {', '.join(raw['workspaces'].keys())}",
                        file=sys.stderr,
                    )
            else:
                # Flat config (backward compatible)
                config = raw
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load config file: {e}", file=sys.stderr)

    # Override with environment variables
    if org := os.getenv("AZURE_DEVOPS_ORG_URL"):
        config["org"] = org
    elif ado_org := os.getenv("ADO_ORG"):
        # ADO_ORG is the org slug (e.g. "itsals"), convert to full URL
        if not ado_org.startswith("http"):
            config["org"] = f"https://dev.azure.com/{ado_org}"
        else:
            config["org"] = ado_org
    if project := os.getenv("AZURE_DEVOPS_PROJECT"):
        config["project"] = project

    # Try az devops configure if org or project still missing
    if not config.get("org") or not config.get("project"):
        try:
            wrapper = AzCliWrapper()
            result = wrapper.run(["az", "devops", "configure", "--list"])
            if result.success and result.stdout:
                # Parse output like: "organization = https://dev.azure.com/org"
                for line in result.stdout.splitlines():
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key == "organization" and not config.get("org"):
                            config["org"] = value
                        elif key == "project" and not config.get("project"):
                            config["project"] = value
        except Exception:
            pass  # Fall through to return partial config

    return config


def discover_project(org: str, work_item_id: int) -> str | None:
    """Discover the project for a work item by fetching its metadata.

    Args:
        org: Organization URL (e.g. https://dev.azure.com/itsals)
        work_item_id: Work item ID

    Returns:
        Project name or None if discovery fails
    """
    wrapper = AzCliWrapper()
    result = wrapper.run(
        ["az", "boards", "work-item", "show",
         "--id", str(work_item_id),
         "--org", org,
         "--output", "json"],
        timeout=30,
    )
    if result.success:
        try:
            data = json.loads(result.stdout)
            return data.get("fields", {}).get("System.TeamProject")
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def handle_error(
    message: str,
    exit_code: ExitCode = ExitCode.COMMAND_ERROR,
    details: str | None = None,
) -> None:
    """Print error message and exit.

    Args:
        message: Main error message
        exit_code: Exit code to use
        details: Optional additional details
    """
    print(f"Error: {message}", file=sys.stderr)
    if details:
        print(f"\nDetails:\n{details}", file=sys.stderr)
    sys.exit(exit_code)


def validate_work_item_id(work_item_id: str) -> int:
    """Validate and convert work item ID to integer.

    Args:
        work_item_id: Work item ID as string

    Returns:
        Work item ID as integer

    Raises:
        ValueError: If ID is not a valid positive integer
    """
    try:
        id_int = int(work_item_id)
        if id_int <= 0:
            raise ValueError("Work item ID must be positive")
        return id_int
    except ValueError as e:
        raise ValueError(f"Invalid work item ID '{work_item_id}': {e}")


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Format data as ASCII table.

    Args:
        headers: Column headers
        rows: Data rows

    Returns:
        Formatted table string
    """
    if not rows:
        return ""

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Format header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths, strict=False))
    separator = "-+-".join("-" * w for w in widths)

    # Format rows
    formatted_rows = [
        " | ".join(str(cell).ljust(w) for cell, w in zip(row, widths, strict=False)) for row in rows
    ]

    return "\n".join([header_line, separator] + formatted_rows)


__all__ = [
    "AzCliWrapper",
    "CommandResult",
    "ExitCode",
    "discover_project",
    "load_config",
    "handle_error",
    "validate_work_item_id",
    "format_table",
]
