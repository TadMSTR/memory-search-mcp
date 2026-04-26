# memory-search-mcp

**Scope:** Personal-agent ONLY. Not registered in the global `~/.claude/settings.json`.

FastMCP server exposing full-text memory search against the OpenSearch `claude-memory` index.

## Tool surface (v1)

| Tool | Description |
|------|-------------|
| `search_memory` | Search memory notes by content; filter by category/tier/date range |

## Result shape

Every tool returns a list of:
```json
{
  "index": "claude-memory",
  "path": "/home/ted/.claude/memory/shared/2026-04-01-decision.md",
  "title": "Decision: use SQLite for metadata index",
  "category": "decision-record",
  "tier": "working",
  "created": "2026-04-01",
  "snippet": "First 500 chars of body...",
  "score": 4.321
}
```

## Extensibility

`_search_index(index_name, query, filters, max_results)` is the shared helper.
Add `search_agent_events`, `search_tasks`, etc. in v1.5 by calling it with different index names.

## Config

| Env var | Default | Purpose |
|---------|---------|---------|
| `OPENSEARCH_URL` | `http://127.0.0.1:9200` | OpenSearch endpoint |
| `MCP_PORT` | `8491` | HTTP port |

## PM2

```bash
pm2 start server.py --name memory-search-mcp --interpreter python3 \
  --env MCP_PORT=8491
pm2 save
```

## Manifest

Registered in `~/.claude/manifests/personal-agent.yml` under `modules.memory-search`.
NOT in `~/.claude/settings.json`.
