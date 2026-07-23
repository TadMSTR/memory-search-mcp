# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.3.0] - 2026-07-23

### Changed
- **BREAKING — repo/server renamed** `memory-search-mcp` → `memory-fulltext-mcp`, and the
  tool `search_memory` → `search_memory_fulltext`. Names the function (lexical full-text)
  and disambiguates the agent-facing scoped-mcp prefix from `memsearch-mcp`'s semantic
  `search_memory`. The scoped-mcp manifest key and PM2 process name change accordingly
  (coordinated cutover); the HTTP port (`127.0.0.1:8491`) is unchanged.
- **Repo brought to the forge Python-MCP standard.** Migrated to a `src/memory_fulltext_mcp/`
  layout with a console entry point (`memory-fulltext-mcp` = `memory_fulltext_mcp.server:main`).
  PM2 launch becomes `-m memory_fulltext_mcp.server` (see `ecosystem.config.js`).
- Added `structlog` JSON logging (level via `LOG_LEVEL`).

### Fixed
- `OPENSEARCH_URL` default corrected `http://127.0.0.1:9200` → `http://127.0.0.1:9202`
  (forge maps the OpenSearch container's `:9200` to host `:9202`). A bare run previously
  hit the wrong port; the live PM2 proc already set this via env. (I-2)

### Added
- CI workflow (`.github/workflows/ci.yml`) — 3.11/3.12/3.13 matrix, SHA-pinned actions;
  `ruff check` + `ruff format --check` + `pytest --cov` (fail-under 80) + `pip-audit --strict`.
- `ruff` + coverage config in `pyproject.toml`; `.gitleaks.toml`; `CONTRIBUTING.md`;
  `ARCHITECTURE.md`; committed `ecosystem.config.js`.
- Tests for the OpenSearch client singleton, logging config, and `main()` entry point.

## [0.2.0] - 2026-05-28

### Added
- 9 tests covering happy path, snippet truncation at 500 chars, empty results, `max_results` clamping (high and low), filter inclusion in the query body, and OpenSearch connection failure with client singleton reset.
- `pyproject.toml` with version field.

### Changed
- fastmcp pin updated to `>=3.2.4,<4`.

### Fixed
- `_search_index` now wraps the OpenSearch call in a `try/except` — returns `[{"ok": False, "error": "OpenSearch unavailable: ..."}]` instead of propagating an unhandled exception when OpenSearch is unreachable.
- `_client` singleton is reset to `None` on connection failure so the next request retries the connection rather than reusing a broken client.
