# Architecture

`memory-fulltext-mcp` is a small FastMCP server that exposes **lexical full-text**
search over Claude Code agent memory notes indexed in OpenSearch. It is the lexical
counterpart to `memsearch-mcp` (semantic/hybrid search over Milvus).

## Retention tier

The backing `claude-memory` index is the **permanent, lexical (BM25) retention tier**
for agent-authored memory notes — the cold-storage / exact-match layer the semantic
stores do not provide:

| Tier | Store | Retrieval | Scope | Lifetime |
|------|-------|-----------|-------|----------|
| Hot  | memsearch | semantic | recent session/working | rolls with the working set |
| Warm | qmd | semantic | distilled notes + cached docs | current |
| **Cold / retention** | **this server (OpenSearch)** | **lexical BM25, full body** | **agent notes only** | **permanent, no expiry** |

Two properties follow from that role, and are owned by the `memory-os-sync` daemon that
feeds the index (in `host-forge/scripts`), not by this server:

- **Full body is indexed** — the `body` field holds the entire note (no truncation), so a
  phrase anywhere in a note is findable. (Search responses still cap the returned `snippet`
  at 500 chars.)
- **No deletes — DELIBERATE.** When a note expires or is purged from disk it REMAINS in the
  index forever. A future "cleanup" that deletes orphaned docs would defeat the retention
  purpose. Only notes under `shared/` and `agents/` are ingested (cached docs, `.expired/`,
  and `quarantine/` are excluded at the sync layer).

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
| `search_memory_fulltext` | Lexical `multi_match` over `body`/`title`/`path` in the `claude-memory` index, with optional category/tier/date filters. Returns index, path, title, category, tier, created, snippet (≤500 chars), score. |

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
