# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.0] - 2026-05-28

### Added
- 9 tests covering happy path, snippet truncation at 500 chars, empty results, `max_results` clamping (high and low), filter inclusion in the query body, and OpenSearch connection failure with client singleton reset.
- `pyproject.toml` with version field.

### Changed
- fastmcp pin updated to `>=3.2.4,<4`.

### Fixed
- `_search_index` now wraps the OpenSearch call in a `try/except` — returns `[{"ok": False, "error": "OpenSearch unavailable: ..."}]` instead of propagating an unhandled exception when OpenSearch is unreachable.
- `_client` singleton is reset to `None` on connection failure so the next request retries the connection rather than reusing a broken client.
