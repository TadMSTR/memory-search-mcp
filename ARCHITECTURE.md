# Architecture

`memory-fulltext-mcp` is a small FastMCP server that exposes **lexical full-text**
search over Claude Code agent memory notes indexed in OpenSearch. It is the lexical
counterpart to `memsearch-mcp` (semantic/hybrid search over Milvus).

## Components

```
src/memory_fulltext_mcp/
  __init__.py        # package version
  server.py          # FastMCP app, search tool, OpenSearch client, logging, main()
```

- **Transport:** streamable-HTTP, bound to `127.0.0.1:8491` (loopback only).
- **Framework:** FastMCP (`fastmcp>=3.2.4,<4`).
- **Backend:** OpenSearch (`opensearch-py`), index `claude-memory`.
- **Logging:** `structlog`, JSON output, level from `LOG_LEVEL`.

## Backend connection

`OPENSEARCH_URL` defaults to `http://127.0.0.1:9202` (forge maps the OpenSearch
container's `:9200` to host `:9202`). The client is a lazily-constructed singleton;
on a connection failure it is reset to `None` so the next request retries.

## Tools

| Tool | Description |
|------|-------------|
| `search_memory_fulltext` | Lexical `multi_match` over `body_excerpt`/`title`/`path` in the `claude-memory` index, with optional category/tier/date filters. Returns index, path, title, category, tier, created, snippet (≤500 chars), score. |

`_search_index` is a shared helper so additional indexes can be added later with the
same result shape. OpenSearch errors are returned as `[{"ok": False, "error": ...}]`,
never raised.

## Naming

Renamed from `memory-search-mcp` → `memory-fulltext-mcp` (and the tool
`search_memory` → `search_memory_fulltext`) so the agent-facing scoped-mcp prefix
(`memory-fulltext-mcp_search_memory_fulltext`) is unambiguous against
`memsearch-mcp`'s semantic `search_memory`.

## Security model

- **Loopback-only** — binds to `127.0.0.1`.
- **Personal-agent scope** — not registered in the global MCP list; only wired into
  the personal agent's scoped-mcp manifest.
- **Read-only** — search only; no write/index tools.

## Deployment

Runs as a PM2 process (`ecosystem.config.js`) via `-m memory_fulltext_mcp.server` out
of the `/opt/venvs/memory-search-mcp` virtualenv (venv path unchanged by the rename).
