"""Tests for common.load_config(workspace=...) with real temp files.

Uses tmp_path and writes real JSON config files. Environment variables
are patched so tests don't interact with the real environment.
The config_file= parameter is used to avoid touching ~/.azure-devops-tools.json.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from common import load_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_env():
    """Return a patch context that strips ADO env vars so they don't bleed in."""
    return patch.dict(os.environ, {
        "AZURE_DEVOPS_ORG_URL": "",
        "ADO_ORG": "",
        "AZURE_DEVOPS_PROJECT": "",
    }, clear=False)


# We also need to suppress `az devops configure --list` calls; patch AzCliWrapper.run
# to return a failed result so load_config doesn't block on the CLI.
def _no_az_cli():
    from common import CommandResult
    return patch(
        "common.AzCliWrapper.run",
        return_value=CommandResult(returncode=1, stdout="", stderr="", success=False),
    )


# ---------------------------------------------------------------------------
# Workspace resolution
# ---------------------------------------------------------------------------

class TestLoadConfigWorkspace:
    def test_workspace_alias_returns_org_and_project(self, tmp_path):
        cfg = {
            "workspaces": {
                "myboard": {
                    "org": "https://dev.azure.com/itsals",
                    "project": "Account Personalization",
                }
            }
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(cfg))

        with _clean_env(), _no_az_cli():
            result = load_config(config_file=str(config_file), workspace="myboard")

        assert result["org"] == "https://dev.azure.com/itsals"
        assert result["project"] == "Account Personalization"

    def test_missing_workspace_alias_prints_warning_and_returns_partial(self, tmp_path, capsys):
        cfg = {
            "workspaces": {
                "existing": {"org": "https://dev.azure.com/x", "project": "X"}
            }
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(cfg))

        with _clean_env(), _no_az_cli():
            result = load_config(config_file=str(config_file), workspace="missing")

        captured = capsys.readouterr()
        assert "missing" in captured.err.lower() or "not found" in captured.err.lower()
        # Result should still be a dict (may be empty or partial — not an exception)
        assert isinstance(result, dict)

    def test_default_workspace_used_when_no_workspace_arg(self, tmp_path):
        cfg = {
            "default": "preferred",
            "workspaces": {
                "preferred": {
                    "org": "https://dev.azure.com/preferred",
                    "project": "PreferredProject",
                },
                "other": {
                    "org": "https://dev.azure.com/other",
                    "project": "OtherProject",
                },
            },
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(cfg))

        with _clean_env(), _no_az_cli():
            result = load_config(config_file=str(config_file))

        assert result["org"] == "https://dev.azure.com/preferred"
        assert result["project"] == "PreferredProject"

    def test_workspace_with_area_path_included_in_result(self, tmp_path):
        cfg = {
            "workspaces": {
                "myboard": {
                    "org": "https://dev.azure.com/itsals",
                    "project": "Proj",
                    "area_path": "Proj\\Team Area",
                }
            }
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(cfg))

        with _clean_env(), _no_az_cli():
            result = load_config(config_file=str(config_file), workspace="myboard")

        assert result.get("area_path") == "Proj\\Team Area"


# ---------------------------------------------------------------------------
# Flat (backward-compatible) config
# ---------------------------------------------------------------------------

class TestLoadConfigFlatConfig:
    def test_flat_config_without_workspaces_key_returns_flat_values(self, tmp_path):
        cfg = {
            "org": "https://dev.azure.com/legacy",
            "project": "LegacyProject",
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(cfg))

        with _clean_env(), _no_az_cli():
            result = load_config(config_file=str(config_file))

        assert result["org"] == "https://dev.azure.com/legacy"
        assert result["project"] == "LegacyProject"

    def test_missing_config_file_returns_empty_or_partial_dict(self, tmp_path):
        config_file = tmp_path / "nonexistent.json"

        with _clean_env(), _no_az_cli():
            result = load_config(config_file=str(config_file))

        assert isinstance(result, dict)

    def test_malformed_json_config_file_returns_partial_dict(self, tmp_path, capsys):
        config_file = tmp_path / "config.json"
        config_file.write_text("{ this is not valid json !!")

        with _clean_env(), _no_az_cli():
            result = load_config(config_file=str(config_file))

        # Should not raise, and should print a warning
        captured = capsys.readouterr()
        assert "warning" in captured.err.lower() or "could not" in captured.err.lower()
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Environment variable overrides
# ---------------------------------------------------------------------------

class TestLoadConfigEnvOverrides:
    def test_azure_devops_org_url_overrides_config_file_org(self, tmp_path):
        cfg = {
            "workspaces": {
                "myboard": {
                    "org": "https://dev.azure.com/config-org",
                    "project": "ConfigProject",
                }
            }
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(cfg))

        with patch.dict(os.environ, {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/env-org",
            "ADO_ORG": "",
            "AZURE_DEVOPS_PROJECT": "",
        }), _no_az_cli():
            result = load_config(config_file=str(config_file), workspace="myboard")

        assert result["org"] == "https://dev.azure.com/env-org"

    def test_azure_devops_project_overrides_config_file_project(self, tmp_path):
        cfg = {
            "workspaces": {
                "myboard": {
                    "org": "https://dev.azure.com/itsals",
                    "project": "ConfigProject",
                }
            }
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(cfg))

        with patch.dict(os.environ, {
            "AZURE_DEVOPS_ORG_URL": "",
            "ADO_ORG": "",
            "AZURE_DEVOPS_PROJECT": "EnvProject",
        }), _no_az_cli():
            result = load_config(config_file=str(config_file), workspace="myboard")

        assert result["project"] == "EnvProject"

    def test_ado_org_slug_converted_to_full_url(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({}))

        with patch.dict(os.environ, {
            "AZURE_DEVOPS_ORG_URL": "",
            "ADO_ORG": "myslug",
            "AZURE_DEVOPS_PROJECT": "",
        }), _no_az_cli():
            result = load_config(config_file=str(config_file))

        assert result.get("org") == "https://dev.azure.com/myslug"

    def test_ado_org_full_url_used_as_is(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({}))

        with patch.dict(os.environ, {
            "AZURE_DEVOPS_ORG_URL": "",
            "ADO_ORG": "https://dev.azure.com/fullurl",
            "AZURE_DEVOPS_PROJECT": "",
        }), _no_az_cli():
            result = load_config(config_file=str(config_file))

        assert result.get("org") == "https://dev.azure.com/fullurl"
