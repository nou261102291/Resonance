#!/usr/bin/env bash
set -euo pipefail

python mcp_server.py > /tmp/mcp_server.log 2>&1 &
MCP_PID=$!

cleanup() {
  kill "$MCP_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
