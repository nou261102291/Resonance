"""Pytest tests for MCP Tool Handlers - Strict TDD Phase 1 Part B (Option C)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from mcp.types import CallToolResult, TextContent
from models import ArousalStateToken, ContextToken, ActuationCommand


class TestHandleGetBeeState:
    """Tests for handle_get_bee_state handler."""

    @pytest.mark.asyncio
    async def test_handle_get_bee_state_returns_call_tool_result(self):
        """Test handle_get_bee_state returns CallToolResult with ArousalStateToken."""
        from mcp_server import handle_get_bee_state

        # Mock the underlying sensor call
        mock_token = ArousalStateToken(
            state="critical",
            confidence=0.94,
            timestamp=1234567890.0,
        )

        with patch("mcp_server.get_panic_attack_bee_state", new_callable=AsyncMock) as mock_sensor:
            mock_sensor.return_value = mock_token

            result = await handle_get_bee_state()

            # Verify result structure
            assert isinstance(result, CallToolResult)
            assert len(result.content) == 1
            assert isinstance(result.content[0], TextContent)
            assert result.content[0].type == "text"

            # Verify the JSON content matches our schema
            content_json = json.loads(result.content[0].text)
            assert content_json["state"] == "critical"
            assert content_json["confidence"] == 0.94
            assert content_json["timestamp"] == 1234567890.0

            # Verify sensor was called
            mock_sensor.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_get_bee_state_handles_different_states(self):
        """Test handle_get_bee_state works with all valid arousal states."""
        from mcp_server import handle_get_bee_state

        for state in ["calm", "elevated", "critical"]:
            mock_token = ArousalStateToken(
                state=state,
                confidence=0.8,
                timestamp=1234567890.0,
            )

            with patch("mcp_server.get_panic_attack_bee_state", new_callable=AsyncMock) as mock_sensor:
                mock_sensor.return_value = mock_token

                result = await handle_get_bee_state()

                content_json = json.loads(result.content[0].text)
                assert content_json["state"] == state


class TestHandleGetRingContext:
    """Tests for handle_get_ring_context handler."""

    @pytest.mark.asyncio
    async def test_handle_get_ring_context_returns_call_tool_result(self):
        """Test handle_get_ring_context returns CallToolResult with ContextToken."""
        from mcp_server import handle_get_ring_context

        mock_token = ContextToken(
            scene="sedentary",
            confidence=0.89,
        )

        with patch("mcp_server.get_panic_attack_ring_context", new_callable=AsyncMock) as mock_sensor:
            mock_sensor.return_value = mock_token

            result = await handle_get_ring_context()

            assert isinstance(result, CallToolResult)
            assert len(result.content) == 1
            assert isinstance(result.content[0], TextContent)

            content_json = json.loads(result.content[0].text)
            assert content_json["scene"] == "sedentary"
            assert content_json["confidence"] == 0.89

            mock_sensor.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_get_ring_context_handles_all_scenes(self):
        """Test handle_get_ring_context works with all valid scene types."""
        from mcp_server import handle_get_ring_context

        for scene in ["sedentary", "active", "outdoor", "unknown"]:
            mock_token = ContextToken(scene=scene, confidence=0.9)

            with patch("mcp_server.get_panic_attack_ring_context", new_callable=AsyncMock) as mock_sensor:
                mock_sensor.return_value = mock_token

                result = await handle_get_ring_context()

                content_json = json.loads(result.content[0].text)
                assert content_json["scene"] == scene


class TestHandleTriggerFireTV:
    """Tests for handle_trigger_fire_tv handler."""

    @pytest.mark.asyncio
    async def test_handle_trigger_fire_tv_returns_call_tool_result(self):
        """Test handle_trigger_fire_tv returns CallToolResult with ActuationCommand."""
        from mcp_server import handle_trigger_fire_tv

        mock_token = ActuationCommand(
            action="play_calming_content",
            protocol="alexa",
            status="executed",
        )

        with patch("mcp_server.trigger_panic_attack_actuation", new_callable=AsyncMock) as mock_sensor:
            mock_sensor.return_value = mock_token

            result = await handle_trigger_fire_tv({"action": "play_calming_content", "protocol": "alexa"})

            assert isinstance(result, CallToolResult)
            assert len(result.content) == 1
            assert isinstance(result.content[0], TextContent)

            content_json = json.loads(result.content[0].text)
            assert content_json["action"] == "play_calming_content"
            assert content_json["protocol"] == "alexa"
            assert content_json["status"] == "executed"

            mock_sensor.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_trigger_fire_tv_uses_defaults(self):
        """Test handle_trigger_fire_tv uses default action/protocol when not provided."""
        from mcp_server import handle_trigger_fire_tv

        mock_token = ActuationCommand(
            action="play_calming_content",
            protocol="alexa",
            status="executed",
        )

        with patch("mcp_server.trigger_panic_attack_actuation", new_callable=AsyncMock) as mock_sensor:
            mock_sensor.return_value = mock_token

            # Call with no arguments
            result = await handle_trigger_fire_tv(None)

            content_json = json.loads(result.content[0].text)
            assert content_json["action"] == "play_calming_content"
            assert content_json["protocol"] == "alexa"

    @pytest.mark.asyncio
    async def test_handle_trigger_fire_tv_custom_action(self):
        """Test handle_trigger_fire_tv accepts custom action."""
        from mcp_server import handle_trigger_fire_tv

        mock_token = ActuationCommand(
            action="pause_content",
            protocol="alexa",
            status="executed",
        )

        with patch("mcp_server.trigger_panic_attack_actuation", new_callable=AsyncMock) as mock_sensor:
            mock_sensor.return_value = mock_token

            result = await handle_trigger_fire_tv({"action": "pause_content"})

            content_json = json.loads(result.content[0].text)
            assert content_json["action"] == "pause_content"


class TestHandleCallToolDispatcher:
    """Tests for the main handle_call_tool dispatcher."""

    @pytest.mark.asyncio
    async def test_handle_call_tool_dispatches_to_get_bee_state(self):
        """Test handle_call_tool dispatches get_bee_state to correct handler."""
        from mcp_server import handle_call_tool
        from mcp.types import CallToolRequestParams

        mock_token = ArousalStateToken(state="critical", confidence=0.94, timestamp=1234567890.0)

        with patch("mcp_server.get_panic_attack_bee_state", new_callable=AsyncMock) as mock_sensor:
            mock_sensor.return_value = mock_token

            params = CallToolRequestParams(name="get_bee_state", arguments={})
            result = await handle_call_tool(params)

            content_json = json.loads(result.content[0].text)
            assert content_json["state"] == "critical"

    @pytest.mark.asyncio
    async def test_handle_call_tool_dispatches_to_get_ring_context(self):
        """Test handle_call_tool dispatches get_ring_context to correct handler."""
        from mcp_server import handle_call_tool
        from mcp.types import CallToolRequestParams

        mock_token = ContextToken(scene="sedentary", confidence=0.89)

        with patch("mcp_server.get_panic_attack_ring_context", new_callable=AsyncMock) as mock_sensor:
            mock_sensor.return_value = mock_token

            params = CallToolRequestParams(name="get_ring_context", arguments={})
            result = await handle_call_tool(params)

            content_json = json.loads(result.content[0].text)
            assert content_json["scene"] == "sedentary"

    @pytest.mark.asyncio
    async def test_handle_call_tool_dispatches_to_trigger_fire_tv(self):
        """Test handle_call_tool dispatches trigger_fire_tv to correct handler."""
        from mcp_server import handle_call_tool
        from mcp.types import CallToolRequestParams

        mock_token = ActuationCommand(action="play_calming_content", protocol="alexa", status="executed")

        with patch("mcp_server.trigger_panic_attack_actuation", new_callable=AsyncMock) as mock_sensor:
            mock_sensor.return_value = mock_token

            params = CallToolRequestParams(
                name="trigger_fire_tv",
                arguments={"action": "play_calming_content", "protocol": "alexa"},
            )
            result = await handle_call_tool(params)

            content_json = json.loads(result.content[0].text)
            assert content_json["action"] == "play_calming_content"

    @pytest.mark.asyncio
    async def test_handle_call_tool_raises_on_unknown_tool(self):
        """Test handle_call_tool raises ValueError for unknown tool."""
        from mcp_server import handle_call_tool
        from mcp.types import CallToolRequestParams

        params = CallToolRequestParams(name="unknown_tool", arguments={})

        with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
            await handle_call_tool(params)