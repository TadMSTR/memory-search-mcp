"""Tests for memory-search-mcp using mocked OpenSearch client."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import server as ms


def _make_hit(path: str, title: str, score: float = 1.0, body: str = "excerpt") -> dict:
    return {
        "_score": score,
        "_source": {
            "path": path,
            "title": title,
            "category": "decision-record",
            "tier": "working",
            "created": "2026-01-01",
            "body_excerpt": body,
        },
    }


@pytest.fixture(autouse=True)
def reset_client(monkeypatch):
    """Reset the singleton between tests."""
    monkeypatch.setattr(ms, "_client", None)
    yield
    monkeypatch.setattr(ms, "_client", None)


# ── happy path ────────────────────────────────────────────────────────────────


def test_search_memory_returns_results():
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "hits": {"hits": [_make_hit("/mem/a.md", "Arch Decision")]}
    }
    with patch.object(ms, "_get_client", return_value=mock_client):
        results = ms.search_memory(query="arch")
    assert len(results) == 1
    assert results[0]["path"] == "/mem/a.md"
    assert results[0]["title"] == "Arch Decision"
    assert results[0]["score"] == 1.0


def test_search_memory_snippet_truncated_at_500():
    long_body = "x" * 600
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "hits": {"hits": [_make_hit("/mem/a.md", "T", body=long_body)]}
    }
    with patch.object(ms, "_get_client", return_value=mock_client):
        results = ms.search_memory(query="x")
    assert len(results[0]["snippet"]) == 500


def test_search_memory_empty_results():
    mock_client = MagicMock()
    mock_client.search.return_value = {"hits": {"hits": []}}
    with patch.object(ms, "_get_client", return_value=mock_client):
        results = ms.search_memory(query="nothing")
    assert results == []


# ── max_results clamping ──────────────────────────────────────────────────────


def test_search_memory_max_results_clamped_high():
    mock_client = MagicMock()
    mock_client.search.return_value = {"hits": {"hits": []}}
    with patch.object(ms, "_get_client", return_value=mock_client):
        ms.search_memory(query="q", max_results=200)
    call_kwargs = mock_client.search.call_args
    body = call_kwargs[1]["body"] if "body" in call_kwargs[1] else call_kwargs[0][1]
    assert body["size"] == 50


def test_search_memory_max_results_clamped_low():
    mock_client = MagicMock()
    mock_client.search.return_value = {"hits": {"hits": []}}
    with patch.object(ms, "_get_client", return_value=mock_client):
        ms.search_memory(query="q", max_results=0)
    call_kwargs = mock_client.search.call_args
    body = call_kwargs[1]["body"] if "body" in call_kwargs[1] else call_kwargs[0][1]
    assert body["size"] == 1


# ── filters ───────────────────────────────────────────────────────────────────


def test_search_memory_filter_category_included_in_query():
    mock_client = MagicMock()
    mock_client.search.return_value = {"hits": {"hits": []}}
    with patch.object(ms, "_get_client", return_value=mock_client):
        ms.search_memory(query="q", category="decision-record")
    body = mock_client.search.call_args[1]["body"]
    filters = body["query"]["bool"]["filter"]
    assert any(f.get("term", {}).get("category") == "decision-record" for f in filters)


def test_search_memory_filter_tier_included_in_query():
    mock_client = MagicMock()
    mock_client.search.return_value = {"hits": {"hits": []}}
    with patch.object(ms, "_get_client", return_value=mock_client):
        ms.search_memory(query="q", tier="working")
    body = mock_client.search.call_args[1]["body"]
    filters = body["query"]["bool"]["filter"]
    assert any(f.get("term", {}).get("tier") == "working" for f in filters)


# ── OpenSearch down ───────────────────────────────────────────────────────────


def test_search_memory_opensearch_down_returns_error_dict(monkeypatch):
    mock_client = MagicMock()
    mock_client.search.side_effect = ConnectionError("refused")
    monkeypatch.setattr(ms, "_client", mock_client)

    results = ms.search_memory(query="q")

    assert len(results) == 1
    assert results[0]["ok"] is False
    assert "OpenSearch unavailable" in results[0]["error"]


def test_search_memory_opensearch_down_resets_client(monkeypatch):
    mock_client = MagicMock()
    mock_client.search.side_effect = ConnectionError("refused")
    monkeypatch.setattr(ms, "_client", mock_client)

    ms.search_memory(query="q")

    assert ms._client is None
