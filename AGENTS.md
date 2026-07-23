# memory-fulltext-mcp

**Scope:** Personal-agent ONLY. Not registered in the global `~/.claude/settings.json`.

FastMCP server exposing lexical full-text memory search against the OpenSearch
`claude-memory` index. The lexical counterpart to `memsearch-mcp` (semantic/hybrid).

> Renamed from `memory-search-mcp`; tool `search_memory` → `search_memory_fulltext`.

## Tool surface

| Tool | Description |
|------|-------------|
| `search_memory_fulltext` | Search memory notes by content; filter by category/tier/date range |

## Result shape

Every tool returns a list of:
```json
{
  "index": "claude-memory",
  "path": "/home/user/.claude/memory/shared/2026-04-01-decision.md",
  "title": "Decision: use SQLite for metadata index",
  "category": "decision-record",
  "tier": "working",
  "created": "2026-04-01",
  "snippet": "First 500 chars of body...",
  "score": 4.321
}
```

## Structure

```
src/memory_fulltext_mcp/
  __init__.py
  server.py         FastMCP server — search tool, OpenSearch client, logging, main()
tests/              pytest tests (mocked OpenSearch)
ecosystem.config.js PM2 config
pyproject.toml
```

## Extensibility

`_search_index(index_name, query, filters, max_results)` is the shared helper.
Add more `search_*` tools by calling it with different index names.

## Config

| Env var | Default | Purpose |
|---------|---------|---------|
| `OPENSEARCH_URL` | `http://127.0.0.1:9202` | OpenSearch endpoint |
| `MCP_PORT` | `8491` | HTTP port |
| `LOG_LEVEL` | `INFO` | structlog log level |

## PM2

Runs from `ecosystem.config.js` via `-m memory_fulltext_mcp.server` out of the
`/opt/venvs/memory-search-mcp` virtualenv (needs `pip install -e .` in the venv).

## Manifest

Registered in `~/.claude/manifests/personal-agent.yml` under `modules.memory-fulltext`.
NOT in `~/.claude/settings.json`.

## Git workflow

Branch before editing — do not commit directly to `main`.
