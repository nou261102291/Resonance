#!/usr/bin/env python3
"""
Automated Demo Scenario — Panic Attack Progression

This script simulates a 60-second panic attack scenario by calling the MCP server's
tools with escalating biometric stress levels. It feeds data to the MCP server
every 10 seconds, allowing hands-free demo recording for the Streamlit UI.

Usage:
    python run_demo_scenario.py [--mcp-url URL] [--speed FACTOR]

    --mcp-url: MCP server endpoint (default: http://localhost:8000/mcp)
    --speed:   Time compression factor (default: 1.0, use 10.0 for 6s demo)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class DemoStep:
    """A single step in the demo progression."""
    time_sec: float
    biometric_state: str
    biometric_confidence: float
    context_scene: str
    context_confidence: float
    description: str


# Panic attack scenario: 60 seconds, 7 steps (every 10 seconds)
DEMO_SCENARIO = [
    DemoStep(
        time_sec=0,
        biometric_state="calm",
        biometric_confidence=0.12,
        context_scene="sedentary",
        context_confidence=0.91,
        description="Baseline — user at rest, normal vitals"
    ),
    DemoStep(
        time_sec=10,
        biometric_state="elevated",
        biometric_confidence=0.67,
        context_scene="sedentary",
        context_confidence=0.89,
        description="Early stress — heart rate rising, HRV dropping"
    ),
    DemoStep(
        time_sec=20,
        biometric_state="elevated",
        biometric_confidence=0.78,
        context_scene="sedentary",
        context_confidence=0.88,
        description="Escalating — sustained elevated state, pre-intervention"
    ),
    DemoStep(
        time_sec=30,
        biometric_state="critical",
        biometric_confidence=0.91,
        context_scene="sedentary",
        context_confidence=0.89,
        description="🚨 PANIC ATTACK — critical biometrics, sedentary context → TRIGGER INTERVENTION"
    ),
    DemoStep(
        time_sec=40,
        biometric_state="critical",
        biometric_confidence=0.94,
        context_scene="sedentary",
        context_confidence=0.89,
        description="Sustained intervention — calming content playing on Fire TV"
    ),
    DemoStep(
        time_sec=50,
        biometric_state="elevated",
        biometric_confidence=0.72,
        context_scene="sedentary",
        context_confidence=0.90,
        description="Tapering — biometrics improving, intervention continues"
    ),
    DemoStep(
        time_sec=60,
        biometric_state="calm",
        biometric_confidence=0.21,
        context_scene="sedentary",
        context_confidence=0.92,
        description="Recovery — vitals normalized, monitoring resumes"
    ),
]


class MCPDemoClient:
    """Client for calling MCP tools via Streamable HTTP."""

    def __init__(self, mcp_url: str):
        self.mcp_url = mcp_url.rstrip("/")
        # Ensure trailing slash for MCP streamable HTTP endpoint
        if not self.mcp_url.endswith("/"):
            self.mcp_url += "/"
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.request_id = 0

    async def close(self):
        await self.client.aclose()

    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id

    async def initialize(self) -> dict[str, Any]:
        """Send MCP initialize request."""
        response = await self.client.post(
            self.mcp_url,
            json={
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "resonance-demo", "version": "1.0"}
                }
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def list_tools(self) -> dict[str, Any]:
        """List available MCP tools."""
        response = await self.client.post(
            self.mcp_url,
            json={
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/list",
                "params": {}
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call an MCP tool."""
        response = await self.client.post(
            self.mcp_url,
            json={
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {
                    "name": name,
                    "arguments": arguments or {}
                }
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    async def simulate_biometric(self, state: str, confidence: float) -> dict[str, Any]:
        """Simulate a biometric reading by calling get_bee_state.
        
        Note: The actual MCP tools return predefined panic attack data.
        This simulates the progression by calling the tool and showing
        what the agent would see at each stage.
        """
        # In a real scenario, this would be a custom tool or the mock would
        # return different values. For demo purposes, we call the tool
        # and annotate the output with our scenario state.
        result = await self.call_tool("get_bee_state")
        return result

    async def simulate_context(self, scene: str, confidence: float) -> dict[str, Any]:
        """Simulate environmental context by calling get_ring_context."""
        result = await self.call_tool("get_ring_context")
        return result

    async def trigger_intervention(self, action: str = "play_calming_content") -> dict[str, Any]:
        """Trigger Fire TV actuation."""
        result = await self.call_tool("trigger_fire_tv", {"action": action, "protocol": "alexa"})
        return result


async def run_demo(mcp_url: str, speed_factor: float = 1.0):
    """Run the automated demo scenario."""
    print(f"🎬 Starting Project Resonance Demo")
    print(f"   MCP Endpoint: {mcp_url}")
    print(f"   Speed Factor: {speed_factor}x (60s → {60/speed_factor:.1f}s)")
    print()

    client = MCPDemoClient(mcp_url)

    try:
        # Initialize MCP connection
        print("🔌 Initializing MCP connection...")
        init_result = await client.initialize()
        print(f"   ✅ Initialized: {init_result.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}")

        # List tools
        tools_result = await client.list_tools()
        tools = tools_result.get("result", {}).get("tools", [])
        print(f"   🔧 Available tools: {[t['name'] for t in tools]}")
        print()

        # Run each step
        for i, step in enumerate(DEMO_SCENARIO):
            elapsed = step.time_sec / speed_factor
            if i > 0:
                prev_elapsed = DEMO_SCENARIO[i-1].time_sec / speed_factor
                wait_time = elapsed - prev_elapsed
                print(f"⏳ Waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)

            print(f"\n{'='*60}")
            print(f"📍 STEP {i+1}/7 — T+{step.time_sec:.0f}s — {step.description}")
            print(f"{'='*60}")

            # Show biometric state
            print(f"\n📊 BIOMETRICS (Bee):")
            print(f"   State: {step.biometric_state.upper()} (confidence: {step.biometric_confidence:.0%})")
            
            # Call get_bee_state
            bee_result = await client.simulate_biometric(step.biometric_state, step.biometric_confidence)
            print(f"   MCP Response: {json.dumps(bee_result, indent=6)}")

            # Show environmental context
            print(f"\n🏠 ENVIRONMENTAL CONTEXT (Ring + Nova):")
            print(f"   Scene: {step.context_scene} (confidence: {step.context_confidence:.0%})")
            
            # Call get_ring_context
            ring_result = await client.simulate_context(step.context_scene, step.context_confidence)
            print(f"   MCP Response: {json.dumps(ring_result, indent=6)}")

            # Agent reasoning (simulated)
            print(f"\n🤖 AGENT REASONING:")
            if step.biometric_state == "critical" and step.context_scene == "sedentary":
                print(f"   🚨 CRITICAL + SEDENTARY → INTERVENTION REQUIRED")
                print(f"   Reasoning: User shows panic-level biometrics but is sedentary")
                print(f"   (not exercising). False positive prevented: not a workout.")
                
                # Trigger intervention
                print(f"\n📺 ACTUATION (Fire TV):")
                fire_result = await client.trigger_intervention("play_calming_content")
                print(f"   Action: play_calming_content via Alexa")
                print(f"   MCP Response: {json.dumps(fire_result, indent=6)}")
                print(f"   ✅ Calming intervention EXECUTED")
            elif step.biometric_state == "elevated" and step.context_scene == "sedentary":
                print(f"   ⚠️ ELEVATED + SEDENTARY → Heightened monitoring")
                print(f"   Reasoning: Stress detected but not yet critical. Pre-intervention.")
            else:
                print(f"   ✅ {step.biometric_state.upper()} + {step.context_scene.upper()} → No intervention needed")
                print(f"   Reasoning: Normal state or context explains biometrics.")

        print(f"\n{'='*60}")
        print(f"🎬 DEMO COMPLETE — 60-second panic attack scenario finished")
        print(f"{'='*60}")

    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text[:200]}")
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"❌ Connection Error: {e}")
        print(f"   Make sure MCP server is running at {mcp_url}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(
        description="Run automated panic attack demo for Project Resonance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--mcp-url",
        default="http://localhost:8000/mcp",
        help="MCP server endpoint (default: http://localhost:8000/mcp)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Time compression factor (default: 1.0, use 10.0 for 6s demo)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print scenario steps without calling MCP server"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN — Demo Scenario Steps:")
        print("=" * 60)
        for step in DEMO_SCENARIO:
            print(f"T+{step.time_sec:>3.0f}s | {step.biometric_state:>8} ({step.biometric_confidence:.0%}) | "
                  f"{step.context_scene:>10} ({step.context_confidence:.0%}) | {step.description}")
        return

    asyncio.run(run_demo(args.mcp_url, args.speed))


if __name__ == "__main__":
    main()