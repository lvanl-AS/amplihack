"""Tests for get_linked_prs.py pure-logic functions.

Covers: extract_pr_refs_from_relations, format_pr_summary, format_github_pr_summary.

No az CLI calls, no gh CLI calls, no subprocess invocations in these tests.
"""

import sys
from pathlib import Path

import pytest

# Ensure the az-devops-tools directory is on the path so we can import
# get_linked_prs directly.
_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from get_linked_prs import (
    extract_pr_refs_from_relations,
    format_github_pr_summary,
    format_pr_summary,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ado_artifact_relation():
    """ADO Git PR artifact link relation."""
    return {
        "rel": "ArtifactLink",
        "url": "vstfs:///Git/PullRequestId/aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb/cccccccc-4444-5555-6666-dddddddddddd/42",
        "attributes": {"name": "Pull Request"},
    }


@pytest.fixture
def github_artifact_relation():
    """GitHub PR artifact link relation."""
    return {
        "rel": "ArtifactLink",
        "url": "vstfs:///GitHub/PullRequest/abcdef01-2345-6789-abcd-ef0123456789%2f99",
        "attributes": {"name": "Pull Request"},
    }


@pytest.fixture
def rest_api_relation():
    """REST API style PR link relation."""
    return {
        "rel": "Hyperlink",
        "url": "https://dev.azure.com/myorg/myproject/_apis/git/repositories/my-repo/pullRequests/7",
        "attributes": {"name": "Some Link"},
    }


@pytest.fixture
def named_pr_relation():
    """Relation matched by name='Pull Request' with REST URL."""
    return {
        "rel": "SomeOtherType",
        "url": "https://dev.azure.com/myorg/myproject/_apis/git/repositories/repo-abc/pullRequests/15",
        "attributes": {"name": "Pull Request"},
    }


@pytest.fixture
def non_pr_relation():
    """A relation that is not a PR link."""
    return {
        "rel": "ArtifactLink",
        "url": "vstfs:///Build/Build/12345",
        "attributes": {"name": "Build"},
    }


@pytest.fixture
def full_ado_pr_data():
    """Complete ADO PR data dict for format_pr_summary."""
    return {
        "pullRequestId": 42,
        "title": "Add new feature",
        "description": "This PR adds a new feature to the system.",
        "status": "completed",
        "sourceRefName": "refs/heads/feature/new-thing",
        "targetRefName": "refs/heads/main",
        "repository": {
            "id": "repo-guid-1234",
            "name": "my-repo",
        },
        "createdBy": {
            "displayName": "Jane Developer",
        },
        "creationDate": "2025-01-15T10:30:00Z",
        "mergeStatus": "succeeded",
        "isDraft": False,
        "url": "https://dev.azure.com/org/project/_apis/git/repositories/my-repo/pullRequests/42",
    }


@pytest.fixture
def full_github_pr_data():
    """Complete GitHub PR data dict for format_github_pr_summary."""
    return {
        "number": 99,
        "title": "Fix login bug",
        "body": "Resolves the login timeout issue.",
        "state": "MERGED",
        "headRefName": "fix/login-timeout",
        "baseRefName": "main",
        "changedFiles": 3,
        "additions": 45,
        "deletions": 12,
        "author": {"login": "jdeveloper"},
        "createdAt": "2025-02-10T08:00:00Z",
        "mergedAt": "2025-02-11T14:00:00Z",
        "isDraft": False,
        "url": "https://github.com/MyOrg/MyRepo/pull/99",
    }


# ---------------------------------------------------------------------------
# extract_pr_refs_from_relations
# ---------------------------------------------------------------------------

class TestExtractPrRefsFromRelations:
    """Tests for extract_pr_refs_from_relations."""

    def test_ado_artifact_link_extracts_repo_and_pr_id(self, ado_artifact_relation):
        """ADO vstfs PR artifact link yields repo_id and pr_id."""
        refs = extract_pr_refs_from_relations([ado_artifact_relation])
        assert len(refs) == 1
        assert refs[0]["repo_id"] == "cccccccc-4444-5555-6666-dddddddddddd"
        assert refs[0]["pr_id"] == "42"
        assert "source" not in refs[0]

    def test_github_artifact_link_extracts_connection_and_pr_number(self, github_artifact_relation):
        """GitHub vstfs PR artifact link yields connection_id, pr_number, and source='github'."""
        refs = extract_pr_refs_from_relations([github_artifact_relation])
        assert len(refs) == 1
        assert refs[0]["repo_id"] == "abcdef01-2345-6789-abcd-ef0123456789"
        assert refs[0]["pr_id"] == "99"
        assert refs[0]["source"] == "github"

    def test_github_artifact_link_uppercase_separator(self):
        """GitHub link with uppercase %2F separator is also matched."""
        rel = {
            "rel": "ArtifactLink",
            "url": "vstfs:///GitHub/PullRequest/abcdef01-2345-6789-abcd-ef0123456789%2F55",
            "attributes": {"name": "Pull Request"},
        }
        refs = extract_pr_refs_from_relations([rel])
        assert len(refs) == 1
        assert refs[0]["pr_id"] == "55"
        assert refs[0]["source"] == "github"

    def test_rest_api_url_extracts_repo_and_pr_id(self, rest_api_relation):
        """REST API style PR link yields repo_id and pr_id."""
        refs = extract_pr_refs_from_relations([rest_api_relation])
        assert len(refs) == 1
        assert refs[0]["repo_id"] == "my-repo"
        assert refs[0]["pr_id"] == "7"

    def test_named_pull_request_relation_with_rest_url(self, named_pr_relation):
        """Relation with name='Pull Request' and a REST URL is extracted."""
        refs = extract_pr_refs_from_relations([named_pr_relation])
        assert len(refs) == 1
        assert refs[0]["repo_id"] == "repo-abc"
        assert refs[0]["pr_id"] == "15"

    def test_duplicate_prs_are_deduplicated(self, ado_artifact_relation):
        """Identical PR refs appearing in multiple relations produce one entry."""
        refs = extract_pr_refs_from_relations([ado_artifact_relation, ado_artifact_relation])
        assert len(refs) == 1

    def test_non_pr_relations_are_ignored(self, non_pr_relation):
        """Relations that are not PR links produce no refs."""
        refs = extract_pr_refs_from_relations([non_pr_relation])
        assert refs == []

    def test_empty_relations_returns_empty_list(self):
        """Empty relations list returns empty list."""
        refs = extract_pr_refs_from_relations([])
        assert refs == []

    def test_mixed_ado_and_github_prs_both_extracted(
        self, ado_artifact_relation, github_artifact_relation
    ):
        """Both ADO and GitHub PR relations are extracted together."""
        refs = extract_pr_refs_from_relations([ado_artifact_relation, github_artifact_relation])
        assert len(refs) == 2
        sources = {ref.get("source") for ref in refs}
        # One ADO (no "source" key) and one GitHub (source="github")
        assert "github" in sources

    def test_relation_with_empty_url_is_skipped(self):
        """Relation with an empty URL string produces no refs."""
        rel = {
            "rel": "ArtifactLink",
            "url": "",
            "attributes": {"name": "Pull Request"},
        }
        refs = extract_pr_refs_from_relations([rel])
        assert refs == []

    def test_relation_missing_url_key_is_skipped(self):
        """Relation without a 'url' key at all produces no refs."""
        rel = {
            "rel": "ArtifactLink",
            "attributes": {"name": "Pull Request"},
        }
        refs = extract_pr_refs_from_relations([rel])
        assert refs == []

    def test_cross_type_dedup_rest_and_artifact(self):
        """ADO artifact link and REST link pointing to the same repo/PR are deduplicated."""
        artifact = {
            "rel": "ArtifactLink",
            "url": "vstfs:///Git/PullRequestId/proj-id/repo-x/10",
            "attributes": {"name": "Pull Request"},
        }
        rest = {
            "rel": "Hyperlink",
            "url": "https://dev.azure.com/org/proj/_apis/git/repositories/repo-x/pullRequests/10",
            "attributes": {"name": "Link"},
        }
        refs = extract_pr_refs_from_relations([artifact, rest])
        assert len(refs) == 1
        assert refs[0]["repo_id"] == "repo-x"
        assert refs[0]["pr_id"] == "10"


# ---------------------------------------------------------------------------
# format_pr_summary
# ---------------------------------------------------------------------------

class TestFormatPrSummary:
    """Tests for format_pr_summary."""

    def test_full_pr_data_maps_all_fields(self, full_ado_pr_data):
        """All fields from a complete PR data dict are mapped correctly."""
        summary = format_pr_summary(full_ado_pr_data)
        assert summary["pr_id"] == 42
        assert summary["title"] == "Add new feature"
        assert summary["description"] == "This PR adds a new feature to the system."
        assert summary["status"] == "completed"
        assert summary["source_branch"] == "feature/new-thing"
        assert summary["target_branch"] == "main"
        assert summary["repository"] == "my-repo"
        assert summary["repository_id"] == "repo-guid-1234"
        assert summary["created_by"] == "Jane Developer"
        assert summary["creation_date"] == "2025-01-15T10:30:00Z"
        assert summary["merge_status"] == "succeeded"
        assert summary["is_draft"] is False
        assert "pullRequests/42" in summary["url"]

    def test_branch_refs_are_stripped(self):
        """refs/heads/ prefix is removed from branch names."""
        pr_data = {
            "sourceRefName": "refs/heads/feature/branch-name",
            "targetRefName": "refs/heads/develop",
        }
        summary = format_pr_summary(pr_data)
        assert summary["source_branch"] == "feature/branch-name"
        assert summary["target_branch"] == "develop"

    def test_long_description_truncated_at_2000_chars(self):
        """Descriptions longer than 2000 characters are truncated with a suffix."""
        pr_data = {"description": "x" * 3000}
        summary = format_pr_summary(pr_data)
        assert len(summary["description"]) < 3000
        assert summary["description"].endswith("... (truncated)")
        # The first 2000 chars are preserved
        assert summary["description"][:2000] == "x" * 2000

    def test_description_exactly_2000_chars_not_truncated(self):
        """A description of exactly 2000 characters is not truncated."""
        pr_data = {"description": "y" * 2000}
        summary = format_pr_summary(pr_data)
        assert summary["description"] == "y" * 2000
        assert "truncated" not in summary["description"]

    def test_none_description_becomes_empty_string(self):
        """A None description is coerced to empty string."""
        pr_data = {"description": None}
        summary = format_pr_summary(pr_data)
        assert summary["description"] == ""

    def test_missing_description_key_becomes_empty_string(self):
        """Missing description key defaults to empty string."""
        summary = format_pr_summary({})
        assert summary["description"] == ""

    def test_missing_repository_nested_fields(self):
        """Missing repository dict results in empty strings for repo fields."""
        summary = format_pr_summary({})
        assert summary["repository"] == ""
        assert summary["repository_id"] == ""

    def test_missing_created_by_nested_fields(self):
        """Missing createdBy dict results in empty string for created_by."""
        summary = format_pr_summary({})
        assert summary["created_by"] == ""

    def test_is_draft_defaults_to_false(self):
        """isDraft defaults to False when not present."""
        summary = format_pr_summary({})
        assert summary["is_draft"] is False

    def test_is_draft_true_preserved(self):
        """isDraft=True is preserved in the output."""
        pr_data = {"isDraft": True}
        summary = format_pr_summary(pr_data)
        assert summary["is_draft"] is True

    def test_branches_without_refs_prefix_unchanged(self):
        """Branch names that don't start with refs/heads/ are left alone."""
        pr_data = {
            "sourceRefName": "main",
            "targetRefName": "develop",
        }
        summary = format_pr_summary(pr_data)
        assert summary["source_branch"] == "main"
        assert summary["target_branch"] == "develop"


# ---------------------------------------------------------------------------
# format_github_pr_summary
# ---------------------------------------------------------------------------

class TestFormatGithubPrSummary:
    """Tests for format_github_pr_summary."""

    def test_merged_state_maps_to_completed_and_succeeded(self, full_github_pr_data):
        """MERGED state maps to status='completed' and merge_status='succeeded'."""
        summary = format_github_pr_summary(full_github_pr_data, "MyOrg/MyRepo")
        assert summary["status"] == "completed"
        assert summary["merge_status"] == "succeeded"

    def test_open_state_maps_to_active(self):
        """OPEN state maps to status='active'."""
        pr_data = {"state": "OPEN"}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["status"] == "active"
        assert summary["merge_status"] == ""

    def test_closed_state_maps_to_abandoned(self):
        """CLOSED state maps to status='abandoned'."""
        pr_data = {"state": "CLOSED"}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["status"] == "abandoned"
        assert summary["merge_status"] == ""

    def test_full_data_maps_all_fields(self, full_github_pr_data):
        """All fields from complete GitHub PR data are mapped correctly."""
        summary = format_github_pr_summary(full_github_pr_data, "MyOrg/MyRepo")
        assert summary["pr_id"] == 99
        assert summary["title"] == "Fix login bug"
        assert summary["description"] == "Resolves the login timeout issue."
        assert summary["source_branch"] == "fix/login-timeout"
        assert summary["target_branch"] == "main"
        assert summary["repository"] == "MyRepo"
        assert summary["repository_id"] == "MyOrg/MyRepo"
        assert summary["created_by"] == "jdeveloper"
        assert summary["creation_date"] == "2025-02-10T08:00:00Z"
        assert summary["is_draft"] is False
        assert summary["url"] == "https://github.com/MyOrg/MyRepo/pull/99"
        assert summary["source"] == "github"
        assert summary["additions"] == 45
        assert summary["deletions"] == 12

    def test_with_files_populates_file_changes(self):
        """When 'files' field is present, file_changes and files_changed_count are set."""
        pr_data = {
            "state": "OPEN",
            "files": [
                {"path": "src/main.py", "additions": 10, "deletions": 2},
                {"path": "tests/test_main.py", "additions": 20, "deletions": 0},
            ],
        }
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert "file_changes" in summary
        assert len(summary["file_changes"]) == 2
        assert summary["files_changed_count"] == 2
        assert summary["file_changes"][0]["path"] == "src/main.py"
        assert summary["file_changes"][0]["additions"] == 10
        assert summary["file_changes"][1]["path"] == "tests/test_main.py"

    def test_without_files_no_file_changes_key(self):
        """When 'files' field is absent, file_changes key is not in summary."""
        pr_data = {"state": "OPEN"}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert "file_changes" not in summary
        assert "files_changed_count" not in summary

    def test_repo_full_name_with_slash_extracts_short_name(self):
        """Repo full name 'org/repo-name' extracts 'repo-name' for repository field."""
        pr_data = {"state": "OPEN"}
        summary = format_github_pr_summary(pr_data, "Alaska-ECommerce/PlatformFrontDoor")
        assert summary["repository"] == "PlatformFrontDoor"
        assert summary["repository_id"] == "Alaska-ECommerce/PlatformFrontDoor"

    def test_repo_full_name_without_slash_used_as_is(self):
        """Repo name without slash is used directly for both fields."""
        pr_data = {"state": "OPEN"}
        summary = format_github_pr_summary(pr_data, "standalone-repo")
        assert summary["repository"] == "standalone-repo"
        assert summary["repository_id"] == "standalone-repo"

    def test_long_body_truncated_at_2000_chars(self):
        """Body longer than 2000 characters is truncated."""
        pr_data = {"state": "OPEN", "body": "z" * 3000}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["description"].endswith("... (truncated)")
        assert summary["description"][:2000] == "z" * 2000

    def test_body_exactly_2000_chars_not_truncated(self):
        """Body of exactly 2000 characters is not truncated."""
        pr_data = {"state": "OPEN", "body": "a" * 2000}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["description"] == "a" * 2000
        assert "truncated" not in summary["description"]

    def test_none_body_becomes_empty_string(self):
        """None body is coerced to empty string."""
        pr_data = {"state": "OPEN", "body": None}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["description"] == ""

    def test_source_field_is_always_github(self):
        """The source field is always set to 'github'."""
        pr_data = {"state": "OPEN"}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["source"] == "github"

    def test_unknown_state_lowercased(self):
        """An unknown state value is lowercased as fallback."""
        pr_data = {"state": "PENDING_REVIEW"}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["status"] == "pending_review"

    def test_empty_files_list_produces_empty_file_changes(self):
        """An empty files list produces file_changes=[] and files_changed_count=0."""
        pr_data = {"state": "OPEN", "files": []}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["file_changes"] == []
        assert summary["files_changed_count"] == 0

    def test_missing_author_defaults_to_empty(self):
        """Missing author dict results in empty created_by."""
        pr_data = {"state": "OPEN"}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["created_by"] == ""

    def test_is_draft_true_preserved(self):
        """isDraft=True from GitHub data is preserved."""
        pr_data = {"state": "OPEN", "isDraft": True}
        summary = format_github_pr_summary(pr_data, "org/repo")
        assert summary["is_draft"] is True
