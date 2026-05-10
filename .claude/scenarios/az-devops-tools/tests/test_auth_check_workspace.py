"""Tests for the --workspace resolution logic in auth_check.main().

The key logic under test:
    org = args.org
    project = args.project
    if args.workspace:
        ws_config = load_config(workspace=args.workspace)
        org = org or ws_config.get("org")
        project = project or ws_config.get("project")
    status = check_auth(org=org, project=project)

All ADO calls are mocked. sys.argv is patched to supply CLI arguments.
main() calls sys.exit(), so every call is wrapped with pytest.raises(SystemExit).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import auth_check
from auth_check import AuthStatus, main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ready_status() -> AuthStatus:
    """Return a fully-ready AuthStatus so main() exits with code 0."""
    return AuthStatus(
        az_cli_installed=True,
        logged_in=True,
        devops_extension_installed=True,
        org_configured=True,
        project_configured=True,
        org_accessible=True,
        project_accessible=True,
    )


def _run_main(argv: list[str]):
    """Patch sys.argv and call main(), capturing SystemExit."""
    with patch.object(sys, "argv", ["auth_check.py"] + argv):
        with pytest.raises(SystemExit) as exc_info:
            main()
    return exc_info.value.code


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestWorkspaceResolution:
    def test_workspace_loads_org_and_project_from_config(self):
        ws_config = {"org": "https://dev.azure.com/myorg", "project": "MyProject"}
        status = _make_ready_status()

        with patch.object(auth_check, "load_config", return_value=ws_config) as mock_load, \
             patch.object(auth_check, "check_auth", return_value=status) as mock_check:
            _run_main(["--workspace", "myboard", "--quiet"])

        mock_load.assert_called_once_with(workspace="myboard")
        mock_check.assert_called_once_with(
            org="https://dev.azure.com/myorg",
            project="MyProject",
        )

    def test_explicit_org_flag_wins_over_workspace(self):
        ws_config = {"org": "https://dev.azure.com/workspace-org", "project": "WorkspaceProject"}
        status = _make_ready_status()

        with patch.object(auth_check, "load_config", return_value=ws_config), \
             patch.object(auth_check, "check_auth", return_value=status) as mock_check:
            _run_main(["--workspace", "myboard", "--org", "https://override.com", "--quiet"])

        # --org should override the workspace org
        mock_check.assert_called_once_with(
            org="https://override.com",
            project="WorkspaceProject",
        )

    def test_missing_workspace_alias_passes_none_to_check_auth(self):
        # load_config returns empty dict → workspace not found
        status = _make_ready_status()

        with patch.object(auth_check, "load_config", return_value={}) as mock_load, \
             patch.object(auth_check, "check_auth", return_value=status) as mock_check:
            _run_main(["--workspace", "missing-alias", "--quiet"])

        mock_load.assert_called_once_with(workspace="missing-alias")
        # Both org and project should fall through to None
        mock_check.assert_called_once_with(org=None, project=None)

    def test_no_workspace_flag_does_not_call_load_config_with_workspace(self):
        status = _make_ready_status()

        with patch.object(auth_check, "load_config") as mock_load, \
             patch.object(auth_check, "check_auth", return_value=status) as mock_check:
            _run_main(["--quiet"])

        # load_config should NOT be called with workspace= keyword when --workspace is absent
        for call_args in mock_load.call_args_list:
            assert "workspace" not in call_args.kwargs or call_args.kwargs.get("workspace") is None

        # check_auth receives whatever args.org / args.project are (None by default)
        mock_check.assert_called_once_with(org=None, project=None)

    def test_workspace_with_only_org_in_config_project_stays_none(self):
        ws_config = {"org": "https://dev.azure.com/partial-org"}
        status = _make_ready_status()

        with patch.object(auth_check, "load_config", return_value=ws_config), \
             patch.object(auth_check, "check_auth", return_value=status) as mock_check:
            _run_main(["--workspace", "partial", "--quiet"])

        mock_check.assert_called_once_with(
            org="https://dev.azure.com/partial-org",
            project=None,
        )

    def test_explicit_project_flag_wins_over_workspace_project(self):
        ws_config = {"org": "https://dev.azure.com/myorg", "project": "WorkspaceProject"}
        status = _make_ready_status()

        with patch.object(auth_check, "load_config", return_value=ws_config), \
             patch.object(auth_check, "check_auth", return_value=status) as mock_check:
            _run_main(["--workspace", "myboard", "--project", "ExplicitProject", "--quiet"])

        mock_check.assert_called_once_with(
            org="https://dev.azure.com/myorg",
            project="ExplicitProject",
        )
