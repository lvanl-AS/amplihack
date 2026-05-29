"""Tests for pure stdin/stdout scripts used in the CR workflow.

Covers: combine_ids.py, extract_parent_ids.py, extract_repo_names.py,
        parse_checkpoint.py.

These scripts are standard-library-only text/JSON parsers — no external
service mocking needed.
"""

import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from combine_ids import main as combine_main
from extract_parent_ids import extract_parent_ids
from extract_repo_names import extract_repos_from_pr_data
from parse_checkpoint import parse_additional_data


# ---------------------------------------------------------------------------
# combine_ids.py
# ---------------------------------------------------------------------------


def _run_combine(stdin_text: str) -> str:
    """Run combine_ids.main() with mocked stdin/stdout, return stdout."""
    buf = io.StringIO()
    with patch("sys.stdin", io.StringIO(stdin_text)), patch("sys.stdout", buf):
        combine_main()
    return buf.getvalue().strip()


class TestCombineIds:
    def test_basic_dedup_and_sort(self):
        assert _run_combine("123,456\n456,789") == "123,456,789"

    def test_empty_input(self):
        assert _run_combine("") == ""

    def test_non_numeric_tokens_ignored(self):
        assert _run_combine("123,abc,456") == "123,456"

    def test_whitespace_handled(self):
        assert _run_combine(" 123 , 456 ") == "123,456"

    def test_single_id(self):
        assert _run_combine("42") == "42"

    def test_duplicates_removed(self):
        assert _run_combine("1,1,1") == "1"

    def test_multiple_lines(self):
        assert _run_combine("10,20\n30,40\n20,50") == "10,20,30,40,50"

    def test_blank_lines_ignored(self):
        assert _run_combine("1,2\n\n3,4\n") == "1,2,3,4"

    def test_negative_numbers_ignored(self):
        # "-5" is not .isdigit() so it's filtered out
        assert _run_combine("-5,10") == "10"


# ---------------------------------------------------------------------------
# extract_parent_ids.py
# ---------------------------------------------------------------------------


def _make_work_item(item_id: int, parent_urls: list[str]) -> dict:
    """Build a minimal work item dict with Hierarchy-Reverse relations."""
    relations = [
        {"rel": "System.LinkTypes.Hierarchy-Reverse", "url": url}
        for url in parent_urls
    ]
    return {"id": item_id, "relations": relations}


class TestExtractParentIds:
    def test_single_parent(self):
        items = [_make_work_item(100, ["https://dev.azure.com/_apis/wit/workItems/99"])]
        assert extract_parent_ids(items) == [99]

    def test_multiple_parents_from_multiple_items(self):
        items = [
            _make_work_item(1, ["https://example.com/_apis/wit/workItems/50"]),
            _make_work_item(2, ["https://example.com/_apis/wit/workItems/60"]),
        ]
        assert extract_parent_ids(items) == [50, 60]

    def test_deduplicates_parents(self):
        items = [
            _make_work_item(1, ["https://x.com/workItems/50"]),
            _make_work_item(2, ["https://x.com/workItems/50"]),
        ]
        assert extract_parent_ids(items) == [50]

    def test_sorted_output(self):
        items = [
            _make_work_item(1, ["https://x.com/workItems/100"]),
            _make_work_item(2, ["https://x.com/workItems/50"]),
        ]
        assert extract_parent_ids(items) == [50, 100]

    def test_no_relations(self):
        assert extract_parent_ids([{"id": 1, "relations": []}]) == []

    def test_none_relations(self):
        assert extract_parent_ids([{"id": 1, "relations": None}]) == []

    def test_missing_relations_key(self):
        assert extract_parent_ids([{"id": 1}]) == []

    def test_wrong_relation_type_ignored(self):
        items = [{
            "id": 1,
            "relations": [
                {"rel": "System.LinkTypes.Hierarchy-Forward", "url": "https://x.com/workItems/99"}
            ],
        }]
        assert extract_parent_ids(items) == []

    def test_empty_url_skipped(self):
        items = [{
            "id": 1,
            "relations": [
                {"rel": "System.LinkTypes.Hierarchy-Reverse", "url": ""}
            ],
        }]
        assert extract_parent_ids(items) == []

    def test_trailing_slash_handled(self):
        items = [_make_work_item(1, ["https://x.com/workItems/42/"])]
        assert extract_parent_ids(items) == [42]

    def test_non_numeric_url_segment_skipped(self):
        items = [_make_work_item(1, ["https://x.com/workItems/notanumber"])]
        assert extract_parent_ids(items) == []

    def test_empty_items_list(self):
        assert extract_parent_ids([]) == []


# ---------------------------------------------------------------------------
# extract_repo_names.py
# ---------------------------------------------------------------------------


class TestExtractReposFromPrData:
    def test_valid_json_with_repos(self):
        data = json.dumps({"all_prs": [
            {"repository": "repo-a"},
            {"repository": "repo-b"},
        ]})
        assert extract_repos_from_pr_data(data) == {"repo-a", "repo-b"}

    def test_empty_string(self):
        assert extract_repos_from_pr_data("") == set()

    def test_whitespace_only(self):
        assert extract_repos_from_pr_data("   ") == set()

    def test_invalid_json(self):
        assert extract_repos_from_pr_data("{not valid}") == set()

    def test_no_all_prs_key(self):
        assert extract_repos_from_pr_data('{"other": []}') == set()

    def test_empty_repo_name_skipped(self):
        data = json.dumps({"all_prs": [{"repository": ""}, {"repository": "repo-a"}]})
        assert extract_repos_from_pr_data(data) == {"repo-a"}

    def test_deduplicates_repos(self):
        data = json.dumps({"all_prs": [
            {"repository": "repo-a"},
            {"repository": "repo-a"},
        ]})
        assert extract_repos_from_pr_data(data) == {"repo-a"}

    def test_pr_missing_repository_key(self):
        data = json.dumps({"all_prs": [{"title": "PR 1"}]})
        assert extract_repos_from_pr_data(data) == set()

    def test_all_prs_not_a_list(self):
        data = json.dumps({"all_prs": "not a list"})
        assert extract_repos_from_pr_data(data) == set()


class TestExtractRepoNamesMain:
    """Test main() with ===SOURCE=== delimiters via stdin mock."""

    def _run_main(self, stdin_text: str) -> str:
        from extract_repo_names import main as repo_main
        buf = io.StringIO()
        with patch("sys.stdin", io.StringIO(stdin_text)), patch("sys.stdout", buf):
            repo_main()
        return buf.getvalue().strip()

    def test_two_sources_with_overlap(self):
        source1 = json.dumps({"all_prs": [{"repository": "repo-a"}, {"repository": "repo-b"}]})
        source2 = json.dumps({"all_prs": [{"repository": "repo-b"}, {"repository": "repo-c"}]})
        result = self._run_main(f"{source1}\n===SOURCE===\n{source2}")
        assert result == "repo-a,repo-b,repo-c"

    def test_single_source_no_delimiter(self):
        source = json.dumps({"all_prs": [{"repository": "repo-x"}]})
        result = self._run_main(source)
        assert result == "repo-x"

    def test_empty_source_handled(self):
        source1 = json.dumps({"all_prs": [{"repository": "repo-a"}]})
        result = self._run_main(f"{source1}\n===SOURCE===\n\n")
        assert result == "repo-a"

    def test_all_empty_sources(self):
        result = self._run_main("===SOURCE===\n")
        assert result == ""


# ---------------------------------------------------------------------------
# parse_checkpoint.py
# ---------------------------------------------------------------------------


class TestParseAdditionalData:
    def test_full_block_with_both_fields(self):
        text = """Some agent output here.

===ADDITIONAL_DATA===
STORIES: 111,222
PRS: 333,444
===END_ADDITIONAL_DATA===

More output after."""
        result = parse_additional_data(text)
        assert result["stories"] == "111,222"
        assert result["prs"] == "333,444"

    def test_only_prs(self):
        text = """===ADDITIONAL_DATA===
PRS: 100,200
===END_ADDITIONAL_DATA==="""
        result = parse_additional_data(text)
        assert result["stories"] == ""
        assert result["prs"] == "100,200"

    def test_only_stories(self):
        text = """===ADDITIONAL_DATA===
STORIES: 500
===END_ADDITIONAL_DATA==="""
        result = parse_additional_data(text)
        assert result["stories"] == "500"
        assert result["prs"] == ""

    def test_no_markers(self):
        result = parse_additional_data("Just some text without any markers.")
        assert result == {"stories": "", "prs": ""}

    def test_non_numeric_ids_filtered(self):
        text = """===ADDITIONAL_DATA===
PRS: 123, abc, 456, , xyz
===END_ADDITIONAL_DATA==="""
        result = parse_additional_data(text)
        assert result["prs"] == "123,456"

    def test_case_insensitive_field_names(self):
        text = """===ADDITIONAL_DATA===
stories: 10,20
prs: 30,40
===END_ADDITIONAL_DATA==="""
        result = parse_additional_data(text)
        assert result["stories"] == "10,20"
        assert result["prs"] == "30,40"

    def test_extra_whitespace_in_markers(self):
        text = """===ADDITIONAL_DATA===
PRS: 99
   ===END_ADDITIONAL_DATA==="""
        result = parse_additional_data(text)
        assert result["prs"] == "99"

    def test_empty_block(self):
        text = """===ADDITIONAL_DATA===

===END_ADDITIONAL_DATA==="""
        result = parse_additional_data(text)
        assert result == {"stories": "", "prs": ""}

    def test_empty_field_values(self):
        text = """===ADDITIONAL_DATA===
PRS:
STORIES:
===END_ADDITIONAL_DATA==="""
        result = parse_additional_data(text)
        assert result["stories"] == ""
        assert result["prs"] == ""

    def test_text_before_and_after_markers(self):
        text = """Here is my analysis of the PRs:
- PR #100 is for feature X
- PR #200 is for feature Y

These are all the PRs I found.

===ADDITIONAL_DATA===
PRS: 100,200
===END_ADDITIONAL_DATA===

Thank you for confirming."""
        result = parse_additional_data(text)
        assert result["prs"] == "100,200"
