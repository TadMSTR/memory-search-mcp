module.exports = {
  apps: [{
    name: "memory-fulltext-mcp",
    // src/ layout + console entry point: requires `pip install -e .` in the venv.
    // The `-m` form matches the memsearch-mcp sibling; `memory-fulltext-mcp` (the
    // console script) is an equivalent launch once the package is installed.
    //
    // NOTE (sysadmin cutover): the venv is intentionally left at the existing
    // /opt/venvs/memory-search-mcp path to avoid recreating it. Rename to
    // /opt/venvs/memory-fulltext-mcp later if desired (optional, out of scope).
    script: "/opt/venvs/memory-search-mcp/bin/python3",
    args: ["-m", "memory_fulltext_mcp.server"],
    cwd: "/home/ted/repos/personal/memory-fulltext-mcp",
    interpreter: "none",

    restart_delay: 5000,
    max_restarts: 10,
    min_uptime: "10s",

    out_file: "/home/ted/logs/memory-fulltext-mcp.log",
    error_file: "/home/ted/logs/memory-fulltext-mcp.log",
    merge_logs: true,
    time: true,

    env: {
      LOG_LEVEL: "INFO",
      MCP_PORT: "8491",
      OPENSEARCH_URL: "http://127.0.0.1:9202",
    },
  }]
};
