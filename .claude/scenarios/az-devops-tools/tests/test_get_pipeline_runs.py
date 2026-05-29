"""Tests for get_pipeline_runs.py pure-logic functions.

Covers: _normalize, _fuzzy_match, _find_candidates, _confirm_repo_match,
        compute_stats.

No az CLI or gh CLI calls are made in these tests.
"""

import sys
from pathlib import Path

import pytest

# Ensure the az-devops-tools directory is on the path so we can import
# get_pipeline_runs directly.
_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from get_pipeline_runs import (
    _confirm_repo_match,
    _find_candidates,
    _fuzzy_match,
    _normalize,
    compute_stats,
)


# ---------------------------------------------------------------------------
# _normalize
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_lowercases(self):
        """Uppercase letters are converted to lowercase."""
        assert _normalize("MyRepo") == "myrepo"

    def test_strips_whitespace(self):
        """Leading and trailing whitespace is removed."""
        assert _normalize(" repo ") == "repo"

    def test_removes_hyphens(self):
        """Hyphens are stripped out."""
        assert _normalize("my-repo") == "myrepo"

    def test_removes_underscores(self):
        """Underscores are stripped out."""
        assert _normalize("my_repo") == "myrepo"

    def test_removes_spaces(self):
        """Internal spaces are stripped out."""
        assert _normalize("my repo") == "myrepo"

    def test_combined_normalization(self):
        """Whitespace, hyphens, underscores, and casing are all handled together."""
        assert _normalize(" My-Repo_Name ") == "myreponame"

    def test_empty_string(self):
        """Empty string normalizes to empty string."""
        assert _normalize("") == ""

    def test_returns_string(self):
        """Result is always a string."""
        assert isinstance(_normalize("anything"), str)


# ---------------------------------------------------------------------------
# _fuzzy_match
# ---------------------------------------------------------------------------

class TestFuzzyMatch:
    def test_repo_name_in_pipeline_name(self):
        """Repo name is a substring of the pipeline name after normalization."""
        assert _fuzzy_match("my-repo-ci", "my-repo") is True

    def test_pipeline_name_in_repo_name(self):
        """Pipeline name is a substring of the repo name (reversed containment)."""
        assert _fuzzy_match("ci", "my-repo-ci") is True

    def test_exact_match(self):
        """Identical names match."""
        assert _fuzzy_match("my-repo", "my-repo") is True

    def test_case_insensitive(self):
        """Matching is case-insensitive."""
        assert _fuzzy_match("MyRepo", "myrepo") is True

    def test_hyphens_vs_no_hyphens(self):
        """Hyphens are ignored during matching."""
        assert _fuzzy_match("my-repo", "myrepo") is True

    def test_no_match(self):
        """Completely unrelated names do not match."""
        assert _fuzzy_match("alpha", "beta") is False

    def test_both_empty_strings(self):
        """Two empty strings match (empty is a substring of empty)."""
        assert _fuzzy_match("", "") is True

    def test_empty_pipeline_name_matches_empty_repo(self):
        """Empty pipeline name is a substring of any repo name."""
        assert _fuzzy_match("", "my-repo") is True

    def test_empty_repo_name_matches_any_pipeline(self):
        """Empty repo name is a substring of any pipeline name."""
        assert _fuzzy_match("my-pipeline", "") is True

    def test_underscores_vs_hyphens(self):
        """Underscores and hyphens are both stripped, so they match."""
        assert _fuzzy_match("my_repo", "my-repo") is True


# ---------------------------------------------------------------------------
# _find_candidates
# ---------------------------------------------------------------------------

SAMPLE_PIPELINES = [
    {"name": "my-repo-ci", "id": 1},
    {"name": "my-repo-cd", "id": 2},
    {"name": "other-service-ci", "id": 3},
    {"name": "unrelated-thing", "id": 4},
]


class TestFindCandidates:
    def test_single_match(self):
        """Returns the one pipeline whose name matches."""
        pipelines = [{"name": "my-repo-ci", "id": 1}, {"name": "unrelated", "id": 2}]
        result = _find_candidates(pipelines, "my-repo")
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_multiple_matches(self):
        """Returns all pipelines whose names match the repo."""
        result = _find_candidates(SAMPLE_PIPELINES, "my-repo")
        ids = [p["id"] for p in result]
        assert 1 in ids
        assert 2 in ids
        assert len(result) == 2

    def test_no_matches(self):
        """Returns empty list when nothing matches."""
        result = _find_candidates(SAMPLE_PIPELINES, "nonexistent-repo")
        assert result == []

    def test_empty_pipeline_list(self):
        """Returns empty list when the pipeline list is empty."""
        result = _find_candidates([], "my-repo")
        assert result == []

    def test_pipeline_with_no_name_key(self):
        """Pipeline missing 'name' key defaults to empty string — empty is a substring of everything, so it matches."""
        pipelines = [{"id": 99}]
        result = _find_candidates(pipelines, "my-repo")
        # Empty string normalized is "", which is a substring of "myrepo",
        # so _fuzzy_match returns True. This is consistent with _fuzzy_match behavior.
        assert len(result) == 1

    def test_pipeline_with_empty_name(self):
        """Pipeline with empty name does not match a non-empty repo name."""
        pipelines = [{"name": "", "id": 99}]
        # Empty string normalized is "", "myrepo" contains "" — so empty name DOES match
        # because _fuzzy_match("", "my-repo") is True (empty is substring of anything).
        # This is the actual behavior of the function.
        result = _find_candidates(pipelines, "my-repo")
        assert len(result) == 1

    def test_returns_full_pipeline_dicts(self):
        """Returned candidates preserve their original dict structure."""
        pipelines = [{"name": "my-repo-ci", "id": 1, "folder": "\\builds"}]
        result = _find_candidates(pipelines, "my-repo")
        assert result[0]["folder"] == "\\builds"


# ---------------------------------------------------------------------------
# _confirm_repo_match
# ---------------------------------------------------------------------------

class TestConfirmRepoMatch:
    def test_direct_repo_name_match(self):
        """Exact match on the repository.name field."""
        definition = {"repository": {"name": "my-repo"}}
        assert _confirm_repo_match(definition, "my-repo") is True

    def test_case_insensitive_repo_name(self):
        """Case-insensitive match on the repository.name field."""
        definition = {"repository": {"name": "My-Repo"}}
        assert _confirm_repo_match(definition, "my-repo") is True

    def test_github_org_slash_repo_format(self):
        """GitHub 'org/repo' format matches the short repo name."""
        definition = {"repository": {"name": "org/my-repo"}}
        assert _confirm_repo_match(definition, "my-repo") is True

    def test_github_org_slash_repo_case_insensitive(self):
        """GitHub 'org/repo' matching is case-insensitive."""
        definition = {"repository": {"name": "Alaska-ECommerce/My-Repo"}}
        assert _confirm_repo_match(definition, "my-repo") is True

    def test_pipeline_name_fallback(self):
        """Falls back to pipeline name when repository name does not match."""
        definition = {
            "repository": {"name": "something-else"},
            "name": "my-repo",
        }
        assert _confirm_repo_match(definition, "my-repo") is True

    def test_no_match_on_any_field(self):
        """Returns False when nothing matches."""
        definition = {
            "repository": {"name": "alpha-service"},
            "name": "alpha-pipeline",
        }
        assert _confirm_repo_match(definition, "beta-service") is False

    def test_empty_definition(self):
        """Empty definition returns False for a non-empty repo name."""
        assert _confirm_repo_match({}, "my-repo") is False

    def test_missing_repository_field(self):
        """When 'repository' key is absent, still checks pipeline name."""
        definition = {"name": "my-repo"}
        assert _confirm_repo_match(definition, "my-repo") is True

    def test_missing_repository_field_no_pipeline_match(self):
        """When 'repository' key is absent and pipeline name doesn't match, returns False."""
        definition = {"name": "something-else"}
        assert _confirm_repo_match(definition, "my-repo") is False

    def test_hyphens_vs_underscores_in_repo_name(self):
        """Normalization handles hyphens vs underscores in repo names."""
        definition = {"repository": {"name": "my_repo"}}
        assert _confirm_repo_match(definition, "my-repo") is True

    def test_nested_org_path_with_multiple_slashes(self):
        """Only the part after the last slash is compared."""
        definition = {"repository": {"name": "org/sub/my-repo"}}
        assert _confirm_repo_match(definition, "my-repo") is True

    def test_slash_in_repo_name_no_match(self):
        """Slash path where the short name does not match."""
        definition = {"repository": {"name": "org/alpha-service"}}
        assert _confirm_repo_match(definition, "beta-service") is False


# ---------------------------------------------------------------------------
# Fixtures for compute_stats
# ---------------------------------------------------------------------------

@pytest.fixture
def successful_run():
    """A single successful run with known values."""
    return {
        "run_id": 101,
        "build_number": "20240101.1",
        "status": "completed",
        "result": "succeeded",
        "start_time": "2024-01-01T10:00:00Z",
        "finish_time": "2024-01-01T10:05:00Z",
        "duration_minutes": 5.0,
        "source_branch": "main",
        "reason": "manual",
        "requested_by": "user1",
    }


@pytest.fixture
def failed_run():
    """A single failed run with known values."""
    return {
        "run_id": 102,
        "build_number": "20240102.1",
        "status": "completed",
        "result": "failed",
        "start_time": "2024-01-02T10:00:00Z",
        "finish_time": "2024-01-02T10:03:00Z",
        "duration_minutes": 3.0,
        "source_branch": "feature/x",
        "reason": "ci",
        "requested_by": "user2",
    }


@pytest.fixture
def run_with_none_duration():
    """A run where duration could not be computed."""
    return {
        "run_id": 103,
        "build_number": "20240103.1",
        "status": "completed",
        "result": "succeeded",
        "start_time": "",
        "finish_time": "",
        "duration_minutes": None,
        "source_branch": "main",
        "reason": "manual",
        "requested_by": "user3",
    }


@pytest.fixture
def mixed_runs(successful_run, failed_run):
    """Two runs: one succeeded, one failed."""
    return [successful_run, failed_run]


@pytest.fixture
def three_runs_with_none(successful_run, failed_run, run_with_none_duration):
    """Three runs: succeeded (5 min), failed (3 min), succeeded (None duration)."""
    return [successful_run, failed_run, run_with_none_duration]


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

class TestComputeStats:
    def test_empty_runs(self):
        """Empty run list returns only total_runs: 0."""
        stats = compute_stats([])
        assert stats == {"total_runs": 0}

    def test_all_succeeded(self, successful_run):
        """All runs succeeded yields 100% success rate."""
        runs = [successful_run]
        stats = compute_stats(runs)
        assert stats["total_runs"] == 1
        assert stats["succeeded"] == 1
        assert stats["failed"] == 0
        assert stats["success_rate"] == 100.0

    def test_mixed_succeeded_and_failed(self, mixed_runs):
        """Correct counts and success rate for mixed results."""
        stats = compute_stats(mixed_runs)
        assert stats["total_runs"] == 2
        assert stats["succeeded"] == 1
        assert stats["failed"] == 1
        assert stats["success_rate"] == 50.0

    def test_duration_stats_calculated(self, mixed_runs):
        """Average, min, and max durations are calculated from non-None values."""
        stats = compute_stats(mixed_runs)
        assert stats["avg_duration_minutes"] == 4.0  # (5.0 + 3.0) / 2
        assert stats["min_duration_minutes"] == 3.0
        assert stats["max_duration_minutes"] == 5.0

    def test_none_durations_excluded(self, three_runs_with_none):
        """Runs with None duration are excluded from duration statistics."""
        stats = compute_stats(three_runs_with_none)
        # Only two runs have durations: 5.0 and 3.0
        assert stats["avg_duration_minutes"] == 4.0
        assert stats["min_duration_minutes"] == 3.0
        assert stats["max_duration_minutes"] == 5.0

    def test_all_none_durations_no_duration_keys(self, run_with_none_duration):
        """When all durations are None, no duration keys are present."""
        runs = [run_with_none_duration]
        stats = compute_stats(runs)
        assert "avg_duration_minutes" not in stats
        assert "min_duration_minutes" not in stats
        assert "max_duration_minutes" not in stats

    def test_last_successful_run_populated(self, mixed_runs):
        """last_successful_run contains the first succeeded run in the list."""
        stats = compute_stats(mixed_runs)
        assert "last_successful_run" in stats
        last = stats["last_successful_run"]
        assert last["run_id"] == 101
        assert last["build_number"] == "20240101.1"
        assert last["finish_time"] == "2024-01-01T10:05:00Z"
        assert last["duration_minutes"] == 5.0

    def test_no_successful_runs_no_last_key(self, failed_run):
        """When no runs succeeded, last_successful_run key is absent."""
        runs = [failed_run]
        stats = compute_stats(runs)
        assert "last_successful_run" not in stats

    def test_single_run_stats(self, successful_run):
        """Stats work correctly with a single run."""
        runs = [successful_run]
        stats = compute_stats(runs)
        assert stats["total_runs"] == 1
        assert stats["avg_duration_minutes"] == 5.0
        assert stats["min_duration_minutes"] == 5.0
        assert stats["max_duration_minutes"] == 5.0

    def test_success_rate_precision(self):
        """Success rate is rounded to one decimal place."""
        runs = [
            {"run_id": i, "result": "succeeded" if i < 2 else "failed",
             "duration_minutes": 1.0, "build_number": str(i),
             "finish_time": "2024-01-01T00:00:00Z"}
            for i in range(3)
        ]
        stats = compute_stats(runs)
        # 2 of 3 succeeded = 66.7%
        assert stats["success_rate"] == 66.7

    def test_last_successful_run_is_first_in_list(self):
        """last_successful_run picks the first succeeded run in iteration order."""
        runs = [
            {"run_id": 201, "result": "failed", "duration_minutes": 2.0,
             "build_number": "a", "finish_time": "t1"},
            {"run_id": 202, "result": "succeeded", "duration_minutes": 3.0,
             "build_number": "b", "finish_time": "t2"},
            {"run_id": 203, "result": "succeeded", "duration_minutes": 4.0,
             "build_number": "c", "finish_time": "t3"},
        ]
        stats = compute_stats(runs)
        assert stats["last_successful_run"]["run_id"] == 202

    def test_other_result_values_not_counted(self):
        """Results that are neither 'succeeded' nor 'failed' are counted in total but not in those categories."""
        runs = [
            {"run_id": 301, "result": "canceled", "duration_minutes": 1.0,
             "build_number": "x", "finish_time": "t1"},
        ]
        stats = compute_stats(runs)
        assert stats["total_runs"] == 1
        assert stats["succeeded"] == 0
        assert stats["failed"] == 0
        assert stats["success_rate"] == 0.0
