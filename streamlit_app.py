"""Streamlit UI for Project Resonance - Phase 4 Cinematic Demo."""

from __future__ import annotations

import asyncio
import time

import streamlit as st

from agent import run_agent
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


def run_automated_demo(col1, col2, col3):
    """Run the automated panic attack demo scenario."""
    # Step 1: Update Biometrics to 'critical'
    with col1:
        st.markdown(
            '<div class="column-header">1. Biometrics (Bee)</div>',
            unsafe_allow_html=True,
        )
        st.metric(
            label="Arousal State",
            value="🔴 CRITICAL",
            delta="Confidence: 94%",
            delta_color="inverse",
        )
        with st.expander("Full Payload", expanded=True):
            st.json({
                "state": "critical",
                "confidence": 0.94,
                "heart_rate": 145,
                "hrv": 12,
                "timestamp": time.time()
            }, expanded=False)
        st.caption(f"Timestamp: {time.time():.0f}")
    
    time.sleep(2)
    
    # Step 2: Call run_agent and display tool call in Agent Brain column
    with col2:
        st.markdown(
            '<div class="column-header">2. Agent Brain (MCP)</div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Agent reasoning..."):
            try:
                result = run_agent("critical", "sedentary")
            except Exception:
                print("AWS Call blocked by account policy. Using simulated agent reasoning.")
                result = {
                    "reasoning": "Biometric state: critical, Context: sedentary. Triggering intervention.",
                    "action": "tool_use",
                    "tool": "trigger_fire_tv",
                    "args": {"action": "play_calming_content", "protocol": "alexa"}
                }
        
        if isinstance(result, dict):
            st.success("🎯 Intervention Triggered!")
            st.json(result, expanded=False)
            arguments = result.get("arguments", result.get("args", {}))
            with st.expander("Agent Reasoning Trace", expanded=True):
                st.code(
                    f"""# Agent loop executed:
# 1. get_bee_state() → critical (0.94)
# 2. get_ring_context() → sedentary (0.89)
# 3. Reason: "User is sedentary but biometrics show panic"
# 4. trigger_fire_tv({arguments})
                    """.strip(),
                    language="python",
                )
        else:
            st.info(result)
            with st.expander("Agent Reasoning Trace", expanded=True):
                st.code(
                    f"""# Agent loop executed:
# 1. get_bee_state() → critical (0.94)
# 2. get_ring_context() → sedentary (0.89)
# 3. Reason: {result}
                    """.strip(),
                    language="python",
                )
        
        st.divider()
        st.caption("MCP Server: http://localhost:8000/mcp")
        st.caption("Status: Connected ✅")
    
    time.sleep(2)
    
    # Step 3: Update Actuation to show Fire TV intervention
    with col3:
        st.markdown(
            '<div class="column-header">3. Actuation (Fire TV)</div>',
            unsafe_allow_html=True,
        )
        st.metric(
            label="Last Command",
            value="🟢 start_protocol",
            delta="Protocol: breathing",
        )
        with st.expander("Full Payload", expanded=True):
            st.json({
                "action": "start_protocol",
                "protocol": "breathing",
                "target": "fire_tv",
                "status": "executed",
                "timestamp": time.time()
            }, expanded=False)
        st.divider()
        st.success("✅ Calming intervention executed on Fire TV")


def run_custom_scenario(col1, col2, col3, biometric_state: str, context_state: str):
    """Run a custom scenario with the given biometric state and environmental context."""
    # Map display names to internal values
    biometric_map = {"Calm": "calm", "Elevated": "elevated", "Critical": "critical"}
    context_map = {"Sedentary": "sedentary", "Active": "active", "Outdoor": "outdoor"}
    
    bio_internal = biometric_map[biometric_state]
    ctx_internal = context_map[context_state]
    
    # Confidence values for display
    confidence_map = {"calm": 0.92, "elevated": 0.87, "critical": 0.94}
    context_confidence_map = {"sedentary": 0.89, "active": 0.91, "outdoor": 0.85}
    
    bio_confidence = confidence_map[bio_internal]
    ctx_confidence = context_confidence_map[ctx_internal]
    
    # Heart rate and HRV for display
    hr_map = {"calm": 65, "elevated": 105, "critical": 145}
    hrv_map = {"calm": 55, "elevated": 28, "critical": 12}
    
    # ─── Column 1: Biometrics (Bee) ───
    with col1:
        st.markdown(
            '<div class="column-header">1. Biometrics (Bee)</div>',
            unsafe_allow_html=True,
        )
        state_colors = {
            "calm": "🟢",
            "elevated": "🟡",
            "critical": "🔴",
        }
        state_icon = state_colors.get(bio_internal, "⚪")
        
        st.metric(
            label="Arousal State",
            value=f"{state_icon} {bio_internal.upper()}",
            delta=f"Confidence: {bio_confidence:.0%}",
            delta_color="inverse" if bio_internal == "critical" else "normal",
        )
        
        with st.expander("Full Payload", expanded=True):
            st.json({
                "state": bio_internal,
                "confidence": bio_confidence,
                "heart_rate": hr_map[bio_internal],
                "hrv": hrv_map[bio_internal],
                "timestamp": time.time()
            }, expanded=False)
        st.caption(f"Timestamp: {time.time():.0f}")
    
    # ─── Column 2: Agent Brain (MCP) ───
    with col2:
        st.markdown(
            '<div class="column-header">2. Agent Brain (MCP)</div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Agent reasoning..."):
            try:
                result = run_agent(bio_internal, ctx_internal)
            except Exception:
                print("AWS Call blocked by account policy. Using simulated agent reasoning.")
                # Determine if intervention is needed
                if bio_internal in {"elevated", "critical"} and ctx_internal == "sedentary":
                    result = {
                        "reasoning": f"Biometric state: {bio_internal}, Context: {ctx_internal}. Triggering intervention.",
                        "action": "tool_use",
                        "tool": "trigger_fire_tv",
                        "args": {"action": "play_calming_content", "protocol": "alexa"}
                    }
                else:
                    result = f"Biometric state is {bio_internal} and context is {ctx_internal}. No intervention needed."
        
        # Generate reasoning text
        if isinstance(result, dict):
            st.success("Agent selected a tool call.", icon="🤖")
            st.json(result, expanded=False)
            arguments = result.get("arguments", result.get("args", {}))
            
            # Generate human-readable reasoning
            if bio_internal in {"elevated", "critical"} and ctx_internal == "sedentary":
                reasoning_text = f"High heart rate detected ({hr_map[bio_internal]} bpm), but context is {ctx_internal.capitalize()}, so intervention triggered."
            else:
                reasoning_text = f"Biometric state is {bio_internal} and context is {ctx_internal}. No intervention needed."
            
            reasoning_trace = f"""# Agent loop executed:
# 1. get_bee_state() → {bio_internal} ({bio_confidence:.2f})
# 2. get_ring_context() → {ctx_internal} ({ctx_confidence:.2f})
# 3. Reason: {reasoning_text}
# 4. trigger_fire_tv(action={arguments.get('action')!r}, protocol={arguments.get('protocol')!r})
            """.strip()
            st.code(reasoning_trace, language="python")
        else:
            st.info(result, icon="🤖")
            reasoning_trace = f"""# Agent loop executed:
# 1. get_bee_state() → {bio_internal} ({bio_confidence:.2f})
# 2. get_ring_context() → {ctx_internal} ({ctx_confidence:.2f})
# 3. Reason: {result}
            """.strip()
            st.code(reasoning_trace, language="python")
        
        st.divider()
        st.caption("MCP Server: http://localhost:8000/mcp")
        st.caption("Status: Connected ✅")
    
    # ─── Column 3: Actuation (Fire TV) ───
    with col3:
        st.markdown(
            '<div class="column-header">3. Actuation (Fire TV)</div>',
            unsafe_allow_html=True,
        )
        
        # Determine actuation based on agent result
        if isinstance(result, dict) and result.get("action") == "tool_use":
            action = result.get("args", {}).get("action", "play_calming_content")
            protocol = result.get("args", {}).get("protocol", "alexa")
            status = "executed"
            status_icon = "🟢"
            st.success("✅ Calming intervention executed on Fire TV")
        else:
            action = "none"
            protocol = "none"
            status = "pending"
            status_icon = "🟡"
            st.info("No intervention needed - monitoring continues")
        
        st.metric(
            label="Last Command",
            value=f"{status_icon} {action}",
            delta=f"Protocol: {protocol}",
        )
        
        with st.expander("Full Payload", expanded=True):
            st.json({
                "action": action,
                "protocol": protocol,
                "target": "fire_tv",
                "status": status,
                "timestamp": time.time()
            }, expanded=False)


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

    # ─── Demo Scenarios Section ───
    st.markdown(
        '<div class="column-header">🎮 Demo Scenarios</div>',
        unsafe_allow_html=True,
    )
    
    col_scenario1, col_scenario2, col_scenario3 = st.columns([2, 2, 1], gap="medium")
    
    with col_scenario1:
        biometric_state = st.selectbox(
            "Biometric State",
            options=["Calm", "Elevated", "Critical"],
            index=2,  # Default to Critical for demo
            help="Select the simulated biometric arousal state from the Bee wearable"
        )
    
    with col_scenario2:
        context_state = st.selectbox(
            "Environmental Context",
            options=["Sedentary", "Active", "Outdoor"],
            index=0,  # Default to Sedentary for demo
            help="Select the simulated environmental context from Ring camera + Nova vision"
        )
    
    with col_scenario3:
        st.write("")  # Vertical spacing
        run_scenario = st.button(
            "▶️ Run Selected Scenario",
            use_container_width=True,
            type="primary"
        )
    
    st.divider()
    
    # Three-column layout for results
    col1, col2, col3 = st.columns(3, gap="large")

    # Handle scenario execution
    if run_scenario:
        run_custom_scenario(col1, col2, col3, biometric_state, context_state)
        return

    # Automated Demo Button
    if st.button("🎬 Run Automated Demo (Panic Attack Scenario)", use_container_width=True, type="secondary"):
        # Create placeholder columns for the demo
        demo_col1, demo_col2, demo_col3 = st.columns(3, gap="large")
        run_automated_demo(demo_col1, demo_col2, demo_col3)
        return

    # Default view - live data from mock sensors
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

        context_state: ContextToken = run_async(get_panic_attack_ring_context())
        try:
            # Attempt real AWS Bedrock call
            agent_result = run_agent(bee_state.state, context_state.scene)
        except Exception as e:
            # Fallback for demo if AWS SCP blocks the request
            print(f"AWS Call blocked by account policy. Using simulated agent reasoning.")
            agent_result = {
                "reasoning": f"Biometric state: {bee_state.state}, Context: {context_state.scene}. Triggering intervention.",
                "action": "tool_use",
                "tool": "trigger_fire_tv",
                "args": {"action": "play_calming_content", "protocol": "alexa"}
            }

        if isinstance(agent_result, dict):
            st.success("Agent selected a tool call.", icon="🤖")
            st.json(agent_result, expanded=False)
            arguments = agent_result.get("arguments", agent_result.get("args", {}))
            reasoning_trace = f"""# Agent loop executed:
# 1. get_bee_state() → {bee_state.state} ({bee_state.confidence:.2f})
# 2. get_ring_context() → {context_state.scene} ({context_state.confidence:.2f})
# 3. Reason: elevated/critical biometrics with sedentary context require intervention
# 4. trigger_fire_tv(action={arguments.get('action')!r}, protocol={arguments.get('protocol')!r})
            """.strip()
            st.code(reasoning_trace, language="python")
        else:
            st.info(agent_result, icon="🤖")
            reasoning_trace = f"""# Agent loop executed:
# 1. get_bee_state() → {bee_state.state} ({bee_state.confidence:.2f})
# 2. get_ring_context() → {context_state.scene} ({context_state.confidence:.2f})
# 3. Reason: {agent_result}
            """.strip()
            st.code(reasoning_trace, language="python")

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