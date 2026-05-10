"""Tests for discover_boards.py cache logic.

No real ADO calls are made. fetch_all_boards is always mocked.
CACHE_PATH is redirected to tmp_path for every test.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_TOOLS_DIR = Path(__file__).resolve().parent.parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import discover_boards
from discover_boards import (
    CACHE_TTL_DAYS,
    get_boards,
    load_cache,
    save_cache,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_BOARDS = [
    {"org": "https://dev.azure.com/itsals", "project": "Alpha", "team": "Team A", "alias": "Alpha/Team A"},
    {"org": "https://dev.azure.com/itsals", "project": "Beta",  "team": "Team B", "alias": "Beta/Team B"},
]


def _patch_cache_path(tmp_path: Path):
    """Redirect CACHE_PATH to a temp file for the duration of a test."""
    cache_file = tmp_path / ".azure-devops-tools-cache.json"
    return patch.object(discover_boards, "CACHE_PATH", cache_file)


def _write_cache(cache_file: Path, boards: list, age_days: float = 0.0) -> None:
    """Write a cache file with a synthetic cached_at timestamp."""
    ts = datetime.now() - timedelta(days=age_days)
    cache_file.write_text(json.dumps({
        "cached_at": ts.isoformat(),
        "org": "https://dev.azure.com/itsals",
        "boards": boards,
    }, indent=2))


# ---------------------------------------------------------------------------
# load_cache
# ---------------------------------------------------------------------------

class TestLoadCache:
    def test_returns_none_when_cache_file_missing(self, tmp_path):
        with _patch_cache_path(tmp_path):
            result = load_cache()
        assert result is None

    def test_returns_none_when_cache_is_stale(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            _write_cache(cache_file, SAMPLE_BOARDS, age_days=CACHE_TTL_DAYS + 1)
            result = load_cache()
        assert result is None

    def test_returns_boards_when_cache_is_fresh(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            _write_cache(cache_file, SAMPLE_BOARDS, age_days=0.0)
            result = load_cache()
        assert result == SAMPLE_BOARDS

    def test_returns_boards_when_cache_is_just_within_ttl(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            _write_cache(cache_file, SAMPLE_BOARDS, age_days=CACHE_TTL_DAYS - 0.01)
            result = load_cache()
        assert result == SAMPLE_BOARDS

    def test_returns_none_on_malformed_json(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        cache_file.write_text("{ not valid json")
        with _patch_cache_path(tmp_path):
            result = load_cache()
        assert result is None

    def test_returns_none_when_cached_at_is_missing(self, tmp_path):
        # cached_at defaults to "2000-01-01" which is certainly stale
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        cache_file.write_text(json.dumps({"boards": SAMPLE_BOARDS}))
        with _patch_cache_path(tmp_path):
            result = load_cache()
        assert result is None


# ---------------------------------------------------------------------------
# save_cache
# ---------------------------------------------------------------------------

class TestSaveCache:
    def test_writes_json_with_cached_at_key(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            save_cache(SAMPLE_BOARDS)
            raw = json.loads(cache_file.read_text())
        assert "cached_at" in raw

    def test_writes_json_with_org_key(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            save_cache(SAMPLE_BOARDS)
            raw = json.loads(cache_file.read_text())
        assert "org" in raw

    def test_writes_json_with_boards_key(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            save_cache(SAMPLE_BOARDS)
            raw = json.loads(cache_file.read_text())
        assert raw["boards"] == SAMPLE_BOARDS

    def test_subsequent_load_cache_returns_same_boards(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            save_cache(SAMPLE_BOARDS)
            result = load_cache()
        assert result == SAMPLE_BOARDS

    def test_cached_at_is_iso_format_string(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            save_cache(SAMPLE_BOARDS)
            raw = json.loads(cache_file.read_text())
        # Must be parseable as ISO datetime
        dt = datetime.fromisoformat(raw["cached_at"])
        assert isinstance(dt, datetime)


# ---------------------------------------------------------------------------
# get_boards
# ---------------------------------------------------------------------------

class TestGetBoards:
    def test_returns_cached_boards_when_cache_is_fresh(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        with _patch_cache_path(tmp_path):
            _write_cache(cache_file, SAMPLE_BOARDS, age_days=0.0)
            with patch.object(discover_boards, "fetch_all_boards") as mock_fetch:
                result = get_boards(refresh=False)
                mock_fetch.assert_not_called()
        assert result == SAMPLE_BOARDS

    def test_calls_fetch_when_cache_is_stale(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        fresh_boards = [{"org": "x", "project": "New", "team": "T", "alias": "New/T"}]
        with _patch_cache_path(tmp_path):
            _write_cache(cache_file, SAMPLE_BOARDS, age_days=CACHE_TTL_DAYS + 1)
            with patch.object(discover_boards, "fetch_all_boards", return_value=fresh_boards) as mock_fetch:
                result = get_boards(refresh=False)
                mock_fetch.assert_called_once()
        assert result == fresh_boards

    def test_calls_fetch_when_cache_missing(self, tmp_path):
        fresh_boards = [{"org": "x", "project": "Fresh", "team": "T", "alias": "Fresh/T"}]
        with _patch_cache_path(tmp_path):
            with patch.object(discover_boards, "fetch_all_boards", return_value=fresh_boards) as mock_fetch:
                result = get_boards(refresh=False)
                mock_fetch.assert_called_once()
        assert result == fresh_boards

    def test_refresh_true_skips_fresh_cache(self, tmp_path):
        cache_file = tmp_path / ".azure-devops-tools-cache.json"
        new_boards = [{"org": "x", "project": "Refreshed", "team": "T", "alias": "Refreshed/T"}]
        with _patch_cache_path(tmp_path):
            _write_cache(cache_file, SAMPLE_BOARDS, age_days=0.0)
            with patch.object(discover_boards, "fetch_all_boards", return_value=new_boards) as mock_fetch:
                result = get_boards(refresh=True)
                mock_fetch.assert_called_once()
        assert result == new_boards

    def test_get_boards_saves_fetched_boards_to_cache(self, tmp_path):
        fresh_boards = [{"org": "x", "project": "Saved", "team": "T", "alias": "Saved/T"}]
        with _patch_cache_path(tmp_path):
            with patch.object(discover_boards, "fetch_all_boards", return_value=fresh_boards):
                get_boards(refresh=True)
            # Cache should now be loadable and contain fresh_boards
            result = load_cache()
        assert result == fresh_boards
