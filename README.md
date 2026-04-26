# memory-search-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Built with FastMCP](https://img.shields.io/badge/Built%20with-FastMCP-orange)](https://github.com/jlowin/fastmcp)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-enabled-blueviolet)](https://claude.ai/code)

Full-text memory search MCP server backed by OpenSearch. Designed for personal-agent scope — exposes body-level keyword search over the Claude Code memory corpus without surfacing it to shared agents or LibreChat. Part of the [homelab-agent](https://github.com/TadMSTR/homelab-agent) memory lifecycle system.

## What It Does

Claude Code agents accumulate memory notes in `~/.claude/memory/`. This server indexes body excerpts (first 2KB per note) into OpenSearch and exposes a single `search_memory` tool for full-text, relevance-ranked queries across the entire corpus.

It is the body-search counterpart to [memory-metadata-mcp](https://github.com/TadMSTR/memory-metadata-mcp), which handles structured metadata queries without touching note bodies.

## Tool

| Tool | What It Does |
|------|-------------|
| `search_memory` | Full-text search across all memory note body excerpts. Supports filtering by `category`, `tier`, and `created` date range. Returns ranked results with snippets. |

### Result shape

```json
{
  "index": "claude-memory",
  "path": "/home/user/.claude/memory/shared/2026-04-01-decision.md",
  "title": "Decision: use SQLite for metadata index",
  "category": "decision-record",
  "tier": "working",
  "created": "2026-04-01",
  "snippet": "First 500 chars of the matching body passage...",
  "score": 4.321
}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | required | Full-text search string |
| `category` | str | — | Filter by lifecycle category |
| `tier` | str | — | Filter by memory tier (`session`, `working`, `distilled`) |
| `max_results` | int | 10 | Max results (1–50) |
| `created_after` | str | — | ISO date lower bound (e.g. `2026-01-01`) |
| `created_before` | str | — | ISO date upper bound |

### Categories

| Category | Expires |
|----------|---------|
| `transient-finding` | 90 days |
| `session-summary` | 30 days |
| `decision-record` | Never |
| `design-document` | Never |
| `research-finding-permanent` | Never |
| `competitive-snapshot` | Never |

## Architecture

```
~/.claude/memory/**/*.md
        │
        │  (memory-os-sync PM2 daemon, 30s batches)
        ▼
OpenSearch 127.0.0.1:9200
index: claude-memory
fields: path, title, category, tier, created, body_excerpt (first 2KB)
        │
        │  (this server)
        ▼
MCP tool: search_memory → ranked results with snippets
```

The OpenSearch container runs on a dedicated single-member Docker network (`memory-search-net`) — isolated from the shared agent network. `memory-search-mcp` reaches it via host loopback (`127.0.0.1:9200`).

## Scope

**Personal-agent only.** This server is intentionally *not* registered in the global `~/.claude/settings.json` MCP list. It is added only to the personal-agent scoped manifest (`~/.claude/manifests/personal-agent.yml`).

Rationale: body excerpts from memory notes could contain sensitive context (internal hostnames, partial configs, work-in-progress decisions). Keeping full-text search out of shared agents and LibreChat prevents accidental exposure through tool call results.

`memory-metadata-mcp` (port 8490) provides path/metadata queries without body content and is safe for all agents.

## Setup

**Requires:** OpenSearch running on `127.0.0.1:9200` with a `claude-memory` index populated by the companion `memory-os-sync` sync daemon.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run directly:

```bash
python server.py
```

Or via PM2:

```js
// ecosystem.config.js
{
  name: "memory-search-mcp",
  script: "/home/user/repos/memory-search-mcp/.venv/bin/python",
  args: "server.py",
  cwd: "/home/user/repos/memory-search-mcp",
  env: {
    OPENSEARCH_URL: "http://127.0.0.1:9200",
    MCP_PORT: "8491",
  },
}
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `OPENSEARCH_URL` | `http://127.0.0.1:9200` | OpenSearch endpoint |
| `MCP_PORT` | `8491` | HTTP port (binds to `127.0.0.1`) |

## Wiring to Claude Code

Add to your personal-agent scoped manifest (not the global settings):

```yaml
# ~/.claude/manifests/personal-agent.yml
modules:
  memory-search:
    mcp:
      memory-search:
        type: http
        url: http://127.0.0.1:8491/mcp
```

## Extensibility

The `_search_index(index_name, query, filters, max_results)` helper is intentionally generic. Adding search over a second OpenSearch index (e.g. `agent-events`, `task-history`) means adding a new `@mcp.tool` that calls `_search_index` with a different index name — the result shape is shared.

## Security

- **Loopback-only** — binds to `127.0.0.1`; OpenSearch container on a dedicated isolated network
- **No write tools** — read-only search only; no index modification
- **Snippet truncation** — body excerpts capped at 500 chars in tool output regardless of index content
- **Input bounds** — `max_results` clamped to 1–50

## Related

- [memory-metadata-mcp](https://github.com/TadMSTR/memory-metadata-mcp) — structured metadata queries (category/tier/tag filters, no body content; safe for all agents)
- [homelab-agent](https://github.com/TadMSTR/homelab-agent) — full platform docs, including [memory-lifecycle](https://github.com/TadMSTR/homelab-agent/blob/main/docs/components/memory-lifecycle.md)

## License

MIT
