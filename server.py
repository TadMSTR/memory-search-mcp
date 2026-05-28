"""memory-search-mcp — Personal-agent full-text memory search via OpenSearch.

Scope: personal-agent ONLY. Not registered in ~/.claude/settings.json global MCP list.
       Add new indexes in v1.5+ via the _search_index helper; common result shape is
       shared across all future tools.
"""

import os
from datetime import datetime, timezone
from typing import Optional

from fastmcp import FastMCP
from opensearchpy import OpenSearch, RequestsHttpConnection

OS_URL = os.environ.get("OPENSEARCH_URL", "http://127.0.0.1:9200")
OS_INDEX_MEMORY = "claude-memory"

_client: Optional[OpenSearch] = None


def _get_client() -> OpenSearch:
    global _client
    if _client is None:
        _client = OpenSearch(
            hosts=[OS_URL],
            connection_class=RequestsHttpConnection,
            use_ssl=False,
            verify_certs=False,  # no-op: connection is plain HTTP, not TLS
            timeout=10,
        )
    return _client


def _search_index(
    index_name: str,
    query: str,
    filters: dict,
    max_results: int,
) -> list[dict]:
    """Shared search helper — reuse for future indexes (search_agent_events, etc.)."""
    global _client

    must_clauses = [
        {
            "multi_match": {
                "query": query,
                "fields": ["body_excerpt^3", "title^2", "path"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }
    ]
    filter_clauses = []

    if filters.get("category"):
        filter_clauses.append({"term": {"category": filters["category"]}})
    if filters.get("tier"):
        filter_clauses.append({"term": {"tier": filters["tier"]}})
    if filters.get("created_after"):
        filter_clauses.append({"range": {"created": {"gte": filters["created_after"]}}})
    if filters.get("created_before"):
        filter_clauses.append({"range": {"created": {"lte": filters["created_before"]}}})

    body = {
        "query": {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
            }
        },
        "_source": ["path", "title", "category", "tier", "created", "body_excerpt"],
        "size": max_results,
    }

    try:
        resp = _get_client().search(index=index_name, body=body)
    except Exception as exc:
        _client = None  # reset singleton so next call retries the connection
        return [{"ok": False, "error": f"OpenSearch unavailable: {exc}"}]

    results = []
    for hit in resp["hits"]["hits"]:
        src = hit["_source"]
        results.append(
            {
                "index": index_name,
                "path": src.get("path", ""),
                "title": src.get("title", ""),
                "category": src.get("category", ""),
                "tier": src.get("tier", ""),
                "created": src.get("created", ""),
                "snippet": src.get("body_excerpt", "")[:500],
                "score": round(hit["_score"], 3),
            }
        )
    return results


mcp = FastMCP(
    "memory-search-mcp",
    instructions=(
        "Full-text search across Claude Code agent memory notes stored in OpenSearch. "
        "Personal-agent ONLY — not available to other agents. "
        "Use search_memory to find notes by content; filter by category or tier to narrow results."
    ),
)


@mcp.tool
def search_memory(
    query: str,
    category: Optional[str] = None,
    tier: Optional[str] = None,
    max_results: int = 10,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
) -> list[dict]:
    """Search agent memory notes by content.

    Args:
        query: Full-text search string.
        category: Filter by lifecycle category (transient-finding, session-summary,
                  decision-record, design-document, research-finding-permanent,
                  competitive-snapshot).
        tier: Filter by memory tier (session, working, distilled).
        max_results: Max results to return (1–50, default 10).
        created_after: ISO date lower bound for created field (e.g. 2026-01-01).
        created_before: ISO date upper bound for created field.

    Returns:
        List of dicts with: index, path, title, category, tier, created, snippet, score.
    """
    max_results = max(1, min(50, max_results))
    filters = {
        "category": category,
        "tier": tier,
        "created_after": created_after,
        "created_before": created_before,
    }
    return _search_index(OS_INDEX_MEMORY, query, filters, max_results)


if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", "8491"))
    mcp.run(transport="streamable-http", host="127.0.0.1", port=port)
