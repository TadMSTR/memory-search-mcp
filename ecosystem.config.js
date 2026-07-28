module.exports = {
  apps: [{
    name: "memory-fulltext-mcp",
    // src/ layout. The venv holds a NON-EDITABLE install as of 2026-07-28
    // (venv-install-standardization-2026-07): deploy with
    // host-forge/scripts/scripts/venv-deploy.sh, which installs from a reviewed
    // tag and verifies the resulting dist-info version. Do not `pip install -e`
    // here as a matter of course — editable is a temporary build-time state only.
    //
    // The venv directory was renamed /opt/venvs/memory-search-mcp ->
    // /opt/venvs/memory-fulltext-mcp on 2026-07-28, completing the repo rename of
    // 2026-07-23. Changing this path requires `pm2 delete` + `pm2 start` rather
    // than `pm2 restart`: restart reuses PM2's cached script/interpreter, so it
    // would silently keep launching the old path.
    script: "/opt/venvs/memory-fulltext-mcp/bin/python3",
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
