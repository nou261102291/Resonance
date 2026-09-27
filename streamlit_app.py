"""Streamlit UI for Project Resonance - Phase 1 Visual Shell."""

from __future__ import annotations

import asyncio

import streamlit as st

from mock_sensors import (
    get_bee_state,
    get_ring_context,
    trigger_fire_tv,
    get_panic_attack_bee_state,
    get_panic_attack_ring_context,
    trigger_panic_attack_actuation,
)
from models import ActuationCommand, ArousalStateToken, ContextToken


# Page configuration
st.set_page_config(
    page_title="Project Resonance",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Custom CSS for clean styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .column-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    .metric-card {
        background: #f9fafb;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stMetric {
        background: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)


def run_async(coro):
    """Helper to run async functions in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def main():
    """Main Streamlit application."""
    # Header
    st.markdown(
        '<div class="main-header">Project Resonance: Ambient Cognitive Infrastructure</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Self-hosted Alexa+ MCP Server for proactive wellness interventions</div>',
        unsafe_allow_html=True,
    )

    # Three-column layout
    col1, col2, col3 = st.columns(3, gap="large")

    # ─── Column 1: Biometrics (Bee) ───
    with col1:
        st.markdown(
            '<div class="column-header">1. Biometrics (Bee)</div>',
            unsafe_allow_html=True,
        )

        # Fetch biometric data
        bee_state: ArousalStateToken = run_async(get_panic_attack_bee_state())

        # State metric with color coding
        state_colors = {
            "calm": "🟢",
            "elevated": "🟡",
            "critical": "🔴",
        }
        state_icon = state_colors.get(bee_state.state, "⚪")

        st.metric(
            label="Arousal State",
            value=f"{state_icon} {bee_state.state.upper()}",
            delta=f"Confidence: {bee_state.confidence:.0%}",
            delta_color="inverse" if bee_state.state == "critical" else "normal",
        )

        # Full payload
        with st.expander("Full Payload", expanded=True):
            st.json(bee_state.model_dump(), expanded=False)

        # Additional context
        st.caption(f"Timestamp: {bee_state.timestamp:.0f}")

    # ─── Column 2: Agent Brain (MCP) ───
    with col2:
        st.markdown(
            '<div class="column-header">2. Agent Brain (MCP)</div>',
            unsafe_allow_html=True,
        )

        st.info("Waiting for agent reasoning...", icon="🤖")

        # Placeholder for future agent reasoning display
        with st.expander("Agent Reasoning Trace", expanded=False):
            st.code(
                """
# Agent loop will execute here:
# 1. get_bee_state() → critical (0.94)
# 2. get_ring_context() → sedentary (0.89)
# 3. Reason: "User is sedentary but biometrics show panic"
# 4. trigger_fire_tv("play_calming_content")
                """.strip(),
                language="python",
            )

        # MCP Connection status
        st.divider()
        st.caption("MCP Server: http://localhost:8000/mcp")
        st.caption("Status: Connected ✅")

    # ─── Column 3: Actuation (Fire TV) ───
    with col3:
        st.markdown(
            '<div class="column-header">3. Actuation (Fire TV)</div>',
            unsafe_allow_html=True,
        )

        # Fetch actuation command
        actuation: ActuationCommand = run_async(trigger_panic_attack_actuation())

        # Status indicator
        status_colors = {
            "pending": "🟡",
            "executed": "🟢",
            "failed": "🔴",
        }
        status_icon = status_colors.get(actuation.status, "⚪")

        st.metric(
            label="Last Command",
            value=f"{status_icon} {actuation.action}",
            delta=f"Protocol: {actuation.protocol}",
        )

        # Full payload
        with st.expander("Full Payload", expanded=True):
            st.json(actuation.model_dump(), expanded=False)

        # Manual trigger for demo
        st.divider()
        if st.button("🎬 Trigger Calming Intervention", use_container_width=True, type="primary"):
            with st.spinner("Executing..."):
                result = run_async(trigger_fire_tv("play_calming_content", "alexa"))
                st.success(f"Executed: {result.action}")
                st.json(result.model_dump())

    # Footer
    st.divider()
    st.caption(
        "Project Resonance • Hackathon Demo • "
        "Zero-Knowledge Architecture • AWS Bedrock + MCP"
    )


if __name__ == "__main__":
    main()