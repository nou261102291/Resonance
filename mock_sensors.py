"""Mock sensor functions for Project Resonance - Phase 1 TDD."""

from __future__ import annotations

import asyncio
from datetime import datetime

from models import ActuationCommand, ArousalStateToken, ContextToken


async def get_bee_state() -> ArousalStateToken:
    """
    Mock function simulating Bee wearable biometric data.
    Returns a 'panic attack' scenario: critical arousal state.
    """
    await asyncio.sleep(0.01)  # Simulate async I/O
    return ArousalStateToken(
        state="critical",
        confidence=0.94,
        timestamp=datetime.now().timestamp(),
    )


async def get_ring_context() -> ContextToken:
    """
    Mock function simulating Ring camera + Nova vision analysis.
    Returns 'sedentary' scene (user is indoors, not exercising).
    """
    await asyncio.sleep(0.01)  # Simulate async I/O
    return ContextToken(
        scene="sedentary",
        confidence=0.89,
    )


async def trigger_fire_tv(action: str, protocol: str = "alexa") -> ActuationCommand:
    """
    Mock function simulating Fire TV actuation.
    Logs the command for Streamlit UI consumption.
    """
    await asyncio.sleep(0.01)  # Simulate async I/O
    return ActuationCommand(
        action=action,
        protocol=protocol,
        status="executed",
    )


# Predefined scenario data for the "panic attack" demo
PANIC_ATTACK_SCENARIO = {
    "bee": ArousalStateToken(state="critical", confidence=0.94, timestamp=0.0),
    "ring": ContextToken(scene="sedentary", confidence=0.89),
    "actuation": ActuationCommand(
        action="play_calming_content",
        protocol="alexa",
        status="executed",
    ),
}


async def get_panic_attack_bee_state() -> ArousalStateToken:
    """Returns the predefined panic attack biometric state."""
    await asyncio.sleep(0.01)
    token = PANIC_ATTACK_SCENARIO["bee"]
    return ArousalStateToken(
        state=token.state,
        confidence=token.confidence,
        timestamp=datetime.now().timestamp(),
    )


async def get_panic_attack_ring_context() -> ContextToken:
    """Returns the predefined panic attack environmental context."""
    await asyncio.sleep(0.01)
    token = PANIC_ATTACK_SCENARIO["ring"]
    return ContextToken(scene=token.scene, confidence=token.confidence)


async def trigger_panic_attack_actuation() -> ActuationCommand:
    """Returns the predefined panic attack actuation command."""
    await asyncio.sleep(0.01)
    token = PANIC_ATTACK_SCENARIO["actuation"]
    return ActuationCommand(
        action=token.action,
        protocol=token.protocol,
        status=token.status,
    )