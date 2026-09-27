"""Pytest tests for mock_sensors.py - Strict TDD Phase 1."""

from __future__ import annotations

import pytest

from mock_sensors import (
    get_bee_state,
    get_ring_context,
    trigger_fire_tv,
    get_panic_attack_bee_state,
    get_panic_attack_ring_context,
    trigger_panic_attack_actuation,
)
from models import ArousalStateToken, ContextToken, ActuationCommand


class TestArousalStateToken:
    """Tests for ArousalStateToken schema validation."""

    def test_valid_states(self):
        """Test all valid literal states are accepted."""
        for state in ["calm", "elevated", "critical"]:
            token = ArousalStateToken(state=state, confidence=0.5, timestamp=1234567890.0)
            assert token.state == state

    def test_invalid_state_raises(self):
        """Test invalid state raises validation error."""
        with pytest.raises(ValueError):
            ArousalStateToken(state="invalid", confidence=0.5, timestamp=1234567890.0)

    def test_confidence_bounds(self):
        """Test confidence must be 0.0-1.0."""
        ArousalStateToken(state="calm", confidence=0.0, timestamp=1234567890.0)
        ArousalStateToken(state="calm", confidence=1.0, timestamp=1234567890.0)

        with pytest.raises(ValueError):
            ArousalStateToken(state="calm", confidence=-0.1, timestamp=1234567890.0)
        with pytest.raises(ValueError):
            ArousalStateToken(state="calm", confidence=1.1, timestamp=1234567890.0)

    def test_timestamp_auto_generates(self):
        """Test timestamp defaults to current time if not provided."""
        import time

        before = time.time()
        token = ArousalStateToken(state="calm", confidence=0.5)
        after = time.time()
        assert before <= token.timestamp <= after


class TestContextToken:
    """Tests for ContextToken schema validation."""

    def test_valid_scenes(self):
        """Test all valid literal scenes are accepted."""
        for scene in ["sedentary", "active", "outdoor", "unknown"]:
            token = ContextToken(scene=scene, confidence=0.5)
            assert token.scene == scene

    def test_invalid_scene_raises(self):
        """Test invalid scene raises validation error."""
        with pytest.raises(ValueError):
            ContextToken(scene="invalid", confidence=0.5)

    def test_confidence_bounds(self):
        """Test confidence must be 0.0-1.0."""
        ContextToken(scene="sedentary", confidence=0.0)
        ContextToken(scene="sedentary", confidence=1.0)

        with pytest.raises(ValueError):
            ContextToken(scene="sedentary", confidence=-0.1)
        with pytest.raises(ValueError):
            ContextToken(scene="sedentary", confidence=1.1)


class TestActuationCommand:
    """Tests for ActuationCommand schema."""

    def test_default_status(self):
        """Test status defaults to 'pending'."""
        cmd = ActuationCommand(action="test", protocol="alexa")
        assert cmd.status == "pending"

    def test_custom_status(self):
        """Test custom status is accepted."""
        cmd = ActuationCommand(action="test", protocol="alexa", status="executed")
        assert cmd.status == "executed"


class TestMockSensors:
    """Tests for mock sensor async functions."""

    @pytest.mark.asyncio
    async def test_get_bee_state_returns_correct_schema(self):
        """Test get_bee_state returns ArousalStateToken with panic attack data."""
        result = await get_bee_state()

        assert isinstance(result, ArousalStateToken)
        assert result.state == "critical"
        assert result.confidence == 0.94
        assert isinstance(result.timestamp, float)

    @pytest.mark.asyncio
    async def test_get_ring_context_returns_correct_schema(self):
        """Test get_ring_context returns ContextToken with sedentary scene."""
        result = await get_ring_context()

        assert isinstance(result, ContextToken)
        assert result.scene == "sedentary"
        assert result.confidence == 0.89

    @pytest.mark.asyncio
    async def test_trigger_fire_tv_returns_correct_schema(self):
        """Test trigger_fire_tv returns ActuationCommand."""
        result = await trigger_fire_tv("play_calming_content", "alexa")

        assert isinstance(result, ActuationCommand)
        assert result.action == "play_calming_content"
        assert result.protocol == "alexa"
        assert result.status == "executed"

    @pytest.mark.asyncio
    async def test_panic_attack_bee_state_matches_scenario(self):
        """Test panic attack bee state matches predefined scenario."""
        result = await get_panic_attack_bee_state()

        assert isinstance(result, ArousalStateToken)
        assert result.state == "critical"
        assert result.confidence == 0.94

    @pytest.mark.asyncio
    async def test_panic_attack_ring_context_matches_scenario(self):
        """Test panic attack ring context matches predefined scenario."""
        result = await get_panic_attack_ring_context()

        assert isinstance(result, ContextToken)
        assert result.scene == "sedentary"
        assert result.confidence == 0.89

    @pytest.mark.asyncio
    async def test_panic_attack_actuation_matches_scenario(self):
        """Test panic attack actuation matches predefined scenario."""
        result = await trigger_panic_attack_actuation()

        assert isinstance(result, ActuationCommand)
        assert result.action == "play_calming_content"
        assert result.protocol == "alexa"
        assert result.status == "executed"

    @pytest.mark.asyncio
    async def test_all_mocks_are_async(self):
        """Verify all mock functions are actually async (awaitable)."""
        import inspect

        assert inspect.iscoroutinefunction(get_bee_state)
        assert inspect.iscoroutinefunction(get_ring_context)
        assert inspect.iscoroutinefunction(trigger_fire_tv)
        assert inspect.iscoroutinefunction(get_panic_attack_bee_state)
        assert inspect.iscoroutinefunction(get_panic_attack_ring_context)
        assert inspect.iscoroutinefunction(trigger_panic_attack_actuation)