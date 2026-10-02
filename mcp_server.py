"""FastAPI + MCP Streamable HTTP Server for Project Resonance."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    CallToolRequestParams,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from models import ArousalStateToken, ContextToken, ActuationCommand
from mock_sensors import (
    get_bee_state,
    get_ring_context,
    trigger_fire_tv,
    get_panic_attack_bee_state,
    get_panic_attack_ring_context,
    trigger_panic_attack_actuation,
)


# MCP Server instance
mcp_server = Server("resonance-mcp")


# Tool definitions
TOOLS = [
    Tool(
        name="get_bee_state",
        description="Get current biometric arousal state from Bee wearable",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="get_ring_context",
        description="Get environmental context from Ring camera + Nova vision",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="trigger_fire_tv",
        description="Trigger Fire TV actuation (play calming content, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action to perform"},
                "protocol": {"type": "string", "description": "Protocol to use (default: alexa)"},
            },
            "required": ["action"],
        },
    ),
]


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
    result = await trigger_panic_attack_actuation()
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

    if tool_name == "get_bee_state":
        return await handle_get_bee_state()

    if tool_name == "get_ring_context":
        return await handle_get_ring_context()

    if tool_name == "trigger_fire_tv":
        return await handle_trigger_fire_tv(args)

    raise ValueError(f"Unknown tool: {tool_name}")


# MCP request handlers using MCP 1.x add_request_handler API
async def handle_list_tools(ctx, params: ListToolsRequest) -> ListToolsResult:
    """Handle tools/list request."""
    return ListToolsResult(tools=TOOLS)


async def handle_call_tool_request(ctx, params: CallToolRequest) -> CallToolResult:
    """Handle tools/call request."""
    return await handle_call_tool(params.name, params.arguments)


# Register request handlers
mcp_server.add_request_handler("tools/list", ListToolsRequest, handle_list_tools)
mcp_server.add_request_handler("tools/call", CallToolRequest, handle_call_tool_request)


# Create the MCP Streamable HTTP app (Starlette)
mcp_app = mcp_server.streamable_http_app(
    streamable_http_path="/",
    json_response=True,
    stateless_http=True,
)


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
