"""Tests for select_board.py pure-logic functions.

Covers: _levenshtein, _score, fuzzy_search, save_board, known_boards,
        load_config, save_config (round-trip).

No TTY interaction and no ADO calls are made in these tests.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the az-devops-tools directory is on the path so we can import
# select_board directly.
_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import select_board
from select_board import (
    _levenshtein,
    _score,
    fuzzy_search,
    known_boards,
    load_config,
    save_board,
    save_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patch_config_path(tmp_path: Path):
    """Return a context manager that redirects CONFIG_PATH to tmp_path."""
    config_file = tmp_path / ".azure-devops-tools.json"
    return patch.object(select_board, "CONFIG_PATH", config_file)


# ---------------------------------------------------------------------------
# _levenshtein
# ---------------------------------------------------------------------------

class TestLevenshtein:
    def test_identical_strings_returns_zero(self):
        assert _levenshtein("hello", "hello") == 0

    def test_case_insensitive_identical_returns_zero(self):
        # "Account Personalization" vs "account personalization"
        assert _levenshtein("Account Personalization", "account personalization") == 0

    def test_empty_string_vs_non_empty_equals_length(self):
        assert _levenshtein("", "abc") == 3

    def test_non_empty_vs_empty_equals_length(self):
        assert _levenshtein("abc", "") == 3

    def test_both_empty_returns_zero(self):
        assert _levenshtein("", "") == 0

    def test_completely_different_same_length_strings(self):
        # "abc" → "xyz" requires 3 substitutions
        assert _levenshtein("abc", "xyz") == 3

    def test_single_insertion(self):
        assert _levenshtein("cat", "cats") == 1

    def test_single_deletion(self):
        assert _levenshtein("cats", "cat") == 1

    def test_single_substitution(self):
        assert _levenshtein("cat", "bat") == 1

    def test_ado_typo_pair_is_small_distance(self):
        # Typo: "acount personlization" vs "account personalization"
        # Two missing letters — distance should be small (<=3) and definitely < 10
        dist = _levenshtein("acount personlization", "account personalization")
        assert dist <= 3

    def test_returns_integer(self):
        result = _levenshtein("foo", "bar")
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# _score
# ---------------------------------------------------------------------------

class TestScore:
    def _make_board(self, project: str, team: str) -> dict:
        return {"project": project, "team": team, "org": "https://dev.azure.com/test", "alias": f"{project}/{team}"}

    def test_substring_match_on_project_returns_zero(self):
        board = self._make_board("Account Personalization", "AP Team")
        assert _score("account", board) == 0.0

    def test_substring_match_on_team_returns_zero(self):
        board = self._make_board("Some Project", "Account Personalization Team")
        assert _score("account", board) == 0.0

    def test_exact_project_match_returns_zero(self):
        board = self._make_board("myproject", "myteam")
        assert _score("myproject", board) == 0.0

    def test_exact_team_match_returns_zero(self):
        board = self._make_board("SomeProject", "myteam")
        assert _score("myteam", board) == 0.0

    def test_takes_minimum_of_project_and_team_score(self):
        # Team is a perfect match → score should be 0.0 even if project doesn't match
        board = self._make_board("CompletelyDifferentProject", "myquery")
        assert _score("myquery", board) == 0.0

    def test_non_substring_returns_normalized_levenshtein(self):
        board = self._make_board("Alpha Bravo Charlie", "DeltaTeam")
        score = _score("xyzxyz", board)
        assert 0.0 < score <= 1.0

    def test_score_is_float(self):
        board = self._make_board("Project One", "Team One")
        result = _score("something", board)
        assert isinstance(result, float)

    def test_case_insensitive_match(self):
        board = self._make_board("Account Personalization", "AP Team")
        # Upper-case query should still hit substring
        assert _score("ACCOUNT", board) == 0.0


# ---------------------------------------------------------------------------
# fuzzy_search
# ---------------------------------------------------------------------------

SAMPLE_BOARDS = [
    {"org": "https://dev.azure.com/itsals", "project": "Account Personalization", "team": "AP Core", "alias": "Account Personalization/AP Core"},
    {"org": "https://dev.azure.com/itsals", "project": "Loyalty Platform", "team": "Miles Team", "alias": "Loyalty Platform/Miles Team"},
    {"org": "https://dev.azure.com/itsals", "project": "Crew Scheduling", "team": "Crew Alpha", "alias": "Crew Scheduling/Crew Alpha"},
    {"org": "https://dev.azure.com/itsals", "project": "Inflight Services", "team": "Cabin Team", "alias": "Inflight Services/Cabin Team"},
    {"org": "https://dev.azure.com/itsals", "project": "Finance Hub", "team": "Finance Team", "alias": "Finance Hub/Finance Team"},
    {"org": "https://dev.azure.com/itsals", "project": "HR Connect", "team": "HR Alpha", "alias": "HR Connect/HR Alpha"},
    {"org": "https://dev.azure.com/itsals", "project": "IT Operations", "team": "Ops Team", "alias": "IT Operations/Ops Team"},
]


class TestFuzzySearch:
    def test_returns_at_most_five_results(self):
        # All boards are candidates; query matches many
        results = fuzzy_search("team", SAMPLE_BOARDS, set())
        assert len(results) <= 5

    def test_excludes_boards_with_matching_alias(self):
        exclude = {"Account Personalization/AP Core"}
        results = fuzzy_search("account", SAMPLE_BOARDS, exclude)
        aliases = [b["alias"] for b in results]
        assert "Account Personalization/AP Core" not in aliases

    def test_substring_match_tops_list(self):
        # "account" substring in "Account Personalization"
        results = fuzzy_search("account", SAMPLE_BOARDS, set())
        assert len(results) >= 1
        assert results[0]["project"] == "Account Personalization"

    def test_results_sorted_ascending_by_score(self):
        results = fuzzy_search("loyalty", SAMPLE_BOARDS, set())
        scores = [_score("loyalty", b) for b in results]
        assert scores == sorted(scores)

    def test_high_score_boards_excluded_by_cutoff(self):
        # "zzzzzzzzz" should match nothing within the 0.65 cutoff
        results = fuzzy_search("zzzzzzzzz", SAMPLE_BOARDS, set())
        assert results == []

    def test_empty_boards_list_returns_empty(self):
        results = fuzzy_search("account", [], set())
        assert results == []

    def test_all_excluded_returns_empty(self):
        all_aliases = {b["alias"] for b in SAMPLE_BOARDS}
        results = fuzzy_search("account", SAMPLE_BOARDS, all_aliases)
        assert results == []

    def test_exact_team_in_exclude_aliases_skipped(self):
        board = {"org": "x", "project": "Loyalty Platform", "team": "Miles Team", "alias": "loyalty-alias"}
        results = fuzzy_search("loyalty", [board], {"loyalty-alias"})
        assert results == []


# ---------------------------------------------------------------------------
# save_board
# ---------------------------------------------------------------------------

class TestSaveBoard:
    def test_saves_board_and_returns_alias(self, tmp_path):
        with _patch_config_path(tmp_path):
            config = {"workspaces": {}}
            board = {
                "org": "https://dev.azure.com/itsals",
                "project": "My Project",
                "team": "My Team",
            }
            alias = save_board(config, board)
            assert alias in config["workspaces"]

    def test_uses_provided_alias_field(self, tmp_path):
        with _patch_config_path(tmp_path):
            config = {"workspaces": {}}
            board = {
                "org": "https://dev.azure.com/itsals",
                "project": "My Project",
                "team": "My Team",
                "alias": "custom-alias",
            }
            alias = save_board(config, board)
            assert alias == "custom-alias"

    def test_falls_back_to_project_slash_team_when_no_alias(self, tmp_path):
        with _patch_config_path(tmp_path):
            config = {"workspaces": {}}
            board = {
                "org": "https://dev.azure.com/itsals",
                "project": "My Project",
                "team": "My Team",
            }
            alias = save_board(config, board)
            assert alias == "My Project/My Team"

    def test_deduplicates_alias_with_suffix_2(self, tmp_path):
        with _patch_config_path(tmp_path):
            config = {
                "workspaces": {
                    "My Project/My Team": {"org": "x", "project": "x", "team": "x"}
                }
            }
            board = {
                "org": "https://dev.azure.com/itsals",
                "project": "My Project",
                "team": "My Team",
            }
            alias = save_board(config, board)
            assert alias == "My Project/My Team_2"

    def test_deduplicates_alias_with_suffix_3_when_2_already_exists(self, tmp_path):
        with _patch_config_path(tmp_path):
            config = {
                "workspaces": {
                    "slot": {"org": "x", "project": "x", "team": "x"},
                    "slot_2": {"org": "x", "project": "x", "team": "x"},
                }
            }
            board = {
                "org": "https://dev.azure.com/itsals",
                "project": "Irrelevant",
                "team": "Irrelevant",
                "alias": "slot",
            }
            alias = save_board(config, board)
            assert alias == "slot_3"

    def test_saved_board_contains_org_project_team(self, tmp_path):
        with _patch_config_path(tmp_path):
            config = {"workspaces": {}}
            board = {
                "org": "https://dev.azure.com/itsals",
                "project": "Proj",
                "team": "TeamX",
            }
            alias = save_board(config, board)
            saved = config["workspaces"][alias]
            assert saved["org"] == "https://dev.azure.com/itsals"
            assert saved["project"] == "Proj"
            assert saved["team"] == "TeamX"

    def test_returns_string_alias(self, tmp_path):
        with _patch_config_path(tmp_path):
            config = {"workspaces": {}}
            board = {"org": "x", "project": "P", "team": "T"}
            result = save_board(config, board)
            assert isinstance(result, str)


# ---------------------------------------------------------------------------
# known_boards
# ---------------------------------------------------------------------------

class TestKnownBoards:
    def test_returns_list_of_dicts_with_required_keys(self):
        config = {
            "workspaces": {
                "my-alias": {"org": "https://dev.azure.com/x", "project": "Proj", "team": "Team"}
            }
        }
        boards = known_boards(config)
        assert len(boards) == 1
        assert boards[0]["alias"] == "my-alias"
        assert boards[0]["org"] == "https://dev.azure.com/x"
        assert boards[0]["project"] == "Proj"
        assert boards[0]["team"] == "Team"

    def test_empty_if_no_workspaces_key(self):
        assert known_boards({}) == []

    def test_empty_if_workspaces_is_empty_dict(self):
        assert known_boards({"workspaces": {}}) == []

    def test_handles_missing_team_gracefully(self):
        config = {
            "workspaces": {
                "alias-no-team": {"org": "https://dev.azure.com/x", "project": "Proj"}
            }
        }
        boards = known_boards(config)
        assert boards[0]["team"] == ""

    def test_returns_multiple_boards(self):
        config = {
            "workspaces": {
                "a1": {"org": "o1", "project": "p1", "team": "t1"},
                "a2": {"org": "o2", "project": "p2", "team": "t2"},
            }
        }
        boards = known_boards(config)
        assert len(boards) == 2


# ---------------------------------------------------------------------------
# load_config / save_config round-trip
# ---------------------------------------------------------------------------

class TestConfigRoundTrip:
    def test_round_trip_save_then_load_returns_same_data(self, tmp_path):
        config_file = tmp_path / ".azure-devops-tools.json"
        with patch.object(select_board, "CONFIG_PATH", config_file):
            data = {
                "workspaces": {
                    "myboard": {"org": "https://dev.azure.com/itsals", "project": "Proj", "team": "T"}
                }
            }
            save_config(data)
            loaded = load_config()
            assert loaded["workspaces"]["myboard"]["org"] == "https://dev.azure.com/itsals"

    def test_missing_file_returns_empty_workspaces(self, tmp_path):
        config_file = tmp_path / "nonexistent.json"
        with patch.object(select_board, "CONFIG_PATH", config_file):
            result = load_config()
            assert result == {"workspaces": {}}

    def test_malformed_json_returns_empty_workspaces(self, tmp_path):
        config_file = tmp_path / ".azure-devops-tools.json"
        config_file.write_text("{ this is not valid json }")
        with patch.object(select_board, "CONFIG_PATH", config_file):
            result = load_config()
            assert result == {"workspaces": {}}

    def test_config_without_workspaces_key_gets_one_added(self, tmp_path):
        config_file = tmp_path / ".azure-devops-tools.json"
        config_file.write_text(json.dumps({"org": "https://dev.azure.com/legacy"}))
        with patch.object(select_board, "CONFIG_PATH", config_file):
            result = load_config()
            assert "workspaces" in result
