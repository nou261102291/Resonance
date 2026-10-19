"""FastAPI + MCP Streamable HTTP Server for Project Resonance."""

import logging
import os
import traceback
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    TextContent,
)

from mock_sensors import (
    trigger_fire_tv,
    get_panic_attack_bee_state,
    get_panic_attack_ring_context,
)

# Configure logging to see actual errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Allow only loopback/test hosts by default; deployments must add their public host.
allowed_mcp_hosts = ["localhost:*", "127.0.0.1:*", "testserver"]
allowed_mcp_hosts.extend(
    host.strip()
    for host in os.getenv("MCP_ALLOWED_HOSTS", "").split(",")
    if host.strip()
)

mcp_server = FastMCP(
    "resonance-mcp",
    streamable_http_path="/",
    json_response=True,
    stateless_http=True,
    transport_security=TransportSecuritySettings(allowed_hosts=allowed_mcp_hosts),
)


# Standalone handler functions for test compatibility
async def handle_get_bee_state() -> CallToolResult:
    """Handle get_bee_state tool call."""
    result = await get_panic_attack_bee_state()
    return CallToolResult(
        content=[TextContent(type="text", text=result.model_dump_json())]
    )


async def handle_get_ring_context() -> CallToolResult:
    """Handle get_ring_context tool call."""
    result = await get_panic_attack_ring_context()
    return CallToolResult(
        content=[TextContent(type="text", text=result.model_dump_json())]
    )


async def handle_trigger_fire_tv(arguments: dict[str, Any] | None = None) -> CallToolResult:
    """Handle trigger_fire_tv tool call."""
    args = arguments or {}
    action = args.get("action", "play_calming_content")
    protocol = args.get("protocol", "alexa")
    result = await trigger_fire_tv(action, protocol)
    return CallToolResult(
        content=[TextContent(type="text", text=result.model_dump_json())]
    )


async def handle_call_tool(name: str | CallToolRequestParams, arguments: dict[str, Any] | None = None) -> CallToolResult:
    """Handle tools/call request - dispatches to individual handlers.
    
    Accepts either:
    - A string tool name and optional arguments dict (for MCP handler)
    - A CallToolRequestParams object (for test compatibility)
    """
    # Handle test compatibility: if first arg is CallToolRequestParams, extract name and arguments
    if isinstance(name, CallToolRequestParams):
        params = name
        tool_name = params.name
        args = params.arguments or {}
    else:
        tool_name = name
        args = arguments or {}

    logger.debug(f"handle_call_tool called with tool_name={tool_name}, args={args}")

    try:
        if tool_name == "get_bee_state":
            return await handle_get_bee_state()

        if tool_name == "get_ring_context":
            return await handle_get_ring_context()

        if tool_name == "trigger_fire_tv":
            return await handle_trigger_fire_tv(args)

        raise ValueError(f"Unknown tool: {tool_name}")
    except Exception as e:
        logger.error(f"Error in handle_call_tool for {tool_name}: {str(e)}")
        logger.error(traceback.format_exc())
        raise


@mcp_server.tool(name="get_bee_state", description="Get current biometric arousal state from Bee wearable")
async def mcp_get_bee_state() -> dict[str, Any]:
    result = await get_panic_attack_bee_state()
    return result.model_dump()


@mcp_server.tool(name="get_ring_context", description="Get environmental context from Ring camera + Nova vision")
async def mcp_get_ring_context() -> dict[str, Any]:
    result = await get_panic_attack_ring_context()
    return result.model_dump()


@mcp_server.tool(name="trigger_fire_tv", description="Trigger Fire TV actuation (play calming content, etc.)")
async def mcp_trigger_fire_tv(action: str, protocol: str = "alexa") -> dict[str, Any]:
    result = await trigger_fire_tv(action, protocol)
    return result.model_dump()


# Create the MCP Streamable HTTP app (Starlette)
mcp_app = mcp_server.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - properly initialize MCP session manager."""
    # The mcp_app is a Starlette app with its own lifespan requirements.
    # We need to manually trigger its startup/shutdown.
    async with mcp_app.router.lifespan_context(app):
        yield


# FastAPI app
app = FastAPI(
    title="Resonance MCP Server",
    description="Self-hosted Alexa+ MCP Server for ambient wellness interventions",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount the MCP app at /mcp
app.mount("/mcp", mcp_app)


# Direct API Proxy Route - Bypasses MCP HTTP validation to invoke working tool handlers directly
@app.post("/api/tools/call")
async def proxy_call_tool(request: Request):
    """Bypasses MCP HTTP validation to invoke the working tool handler directly."""
    raw_json = await request.json()
    
    # Extract structural payload whether flat or nested
    rpc_params = raw_json.get("params", {})
    if "params" in rpc_params:
        tool_data = rpc_params["params"]
    else:
        tool_data = rpc_params

    tool_name = tool_data.get("name")
    tool_args = tool_data.get("arguments", {})

    # Execute the internal verified handler directly with tool name and arguments
    result = await handle_call_tool(tool_name, tool_args)
    
    # Return a compliant JSON-RPC response envelope
    return {
        "jsonrpc": "2.0",
        "id": raw_json.get("id", 1),
        "result": {
            "content": [
                {"type": "text", "text": content.text} for content in result.content
            ]
        }
    }


@app.get("/")
async def root() -> dict[str, str]:
    """Root landing page for the deployed demo."""
    return {
        "status": "ok",
        "service": "resonance-mcp",
        "health": "/health",
        "mcp": "/mcp",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "resonance-mcp"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
