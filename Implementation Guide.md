# Project Resonance: Technical Implementation Plan (v2.0 - Strict Execution)

## 🎯 Objective
Build a self-hosted Alexa+ MCP server prototype using synthetic biometric/context data, model reasoning, and simulated media actuation.

## Current Status

- **MCP:** `mcp==1.26.0`; local Streamable HTTP handshake verifies protocol `2025-11-25`. Public deployment remains unverified.
- **Bedrock:** Claude 3.7 Converse request path exists; Nova Lite image classification is implemented but not wired into the demo. AWS access is blocked, so no live call has been verified.
- **Agent loop:** Claude can return a tool-use request, but the application does not execute it and return a `toolResult` to Bedrock. Demo actuation remains local simulation.
- **Privacy/hardware:** Sensor and context values are synthetic; no Bee, Ring, or Fire TV device integration exists. Edge privacy is a design goal, not a verified guarantee.
- **Open-source mini-challenge:** The planned `resonance-mcp-toolkit` has not been packaged or published.
- **Verification:** `pytest -q` passes 47 tests with MCP 1.26.0; AWS calls are mocked. CloudFormation deployment and live Bedrock access are unverified.

The linked Devpost rules page returned HTTP 403 in this environment. Recheck current track criteria and submission deliverables on Devpost. See [BEDROCK_INTEGRATION.md](BEDROCK_INTEGRATION.md) for Bedrock implementation boundaries, setup, IAM, and privacy notes.

The plan below is retained as historical implementation context; its original dates and checklist states do not supersede the current status above.

## 🔧 Critical Fixes Applied (2026-10-02)

### 1. MCP 1.x FastMCP Registration Fix (`mcp_server.py`)
**Problem:** The server was registered using `add_request_handler()`, which is not part of the pinned MCP 1.11.0 API. The module failed during import.

**Root Cause:** MCP 1.11.0's low-level `Server` registers handlers through its `list_tools()` and `call_tool()` decorators, while `streamable_http_app()` is provided by `FastMCP`. The server mixed APIs from different MCP SDK interfaces.

**Fix Applied:**
- Use `FastMCP` for tool registration and the Streamable HTTP application.
- Keep standalone handler functions for direct unit tests and the FastAPI proxy route.
- Retain the dispatcher compatibility with both string tool names and `CallToolRequestParams`.
- Exercise the standard `/mcp/` initialize, `tools/list`, and `tools/call` flow in an integration test.

**Files Changed:** `mcp_server.py`, `test_mcp.py`

### 2. Invalid MCP Version Pin Fix (`requirements.txt`, `pyproject.toml`)
**Problem:** The requirements originally pinned a nonexistent MCP SDK version.

**Fix Applied:**
- Initially corrected the pin to `mcp==1.11.0`; later upgraded to `mcp==1.26.0` to negotiate the Alexa+ protocol version.

**Files Changed:** `requirements.txt`, `pyproject.toml`

### 3. Test Compatibility Layer
**Problem:** Existing tests in `test_mcp.py` pass `CallToolRequestParams` objects to `handle_call_tool`, but the MCP handler expects a string name.

**Fix Applied:**
- Updated `handle_call_tool` signature to accept `Union[str, CallToolRequestParams]`
- Added runtime type detection to extract `name` and `arguments` from either format
- Historical test compatibility fix; see current verification above for the current suite count.

**Verification (2026-10-18):**
- ✅ MCP server imports with pinned MCP 1.26.0
- ✅ Standard Streamable HTTP `initialize`, `tools/list`, and `tools/call` requests pass
- ✅ `pytest -q` - 47 tests pass (AWS calls mocked)
- ✅ Streamlit AppTest and local HTTP smoke test pass

## 🛑 The 3 Golden Rules of this Hackathon
1. **Mock First, Integrate Later:** We will NOT wait on physical hardware or buggy SDKs. We build `mock_sensors.py` on Day 1. The MCP server only cares about the JSON payload.
2. **The Demo is the Product:** We build the Streamlit UI shell on Day 1. We do not wait until the end to visualize the agent. If we can't see it thinking, we can't debug it.
3. **Strict TDD via Copilot:** We write the `pytest` tests *before* the implementation. Copilot will generate the tests first, ensuring we stay exactly on track with the rubric.

## 🛠️ Core Tech Stack
- **Language:** Python 3.12+
- **MCP Framework:** Official MCP Python SDK (Streamable HTTP)
- **AI/Reasoning:** Bedrock Converse (Claude 3.7 reasoning request and Nova Lite classifier; live access unverified)
- **API Framework:** FastAPI (for the MCP HTTP transport)
- **Demo UI:** Streamlit (Continuous visual feedback)
- **Testing:** `pytest` and `pytest-asyncio`

---

## 📅 Phase 1: Foundation, Mocks & The Visual Shell (Day 1)
**Goal:** Establish the MCP server, hardcode the mocks, and build the Streamlit UI shell. No AWS calls yet.

### Action Items
1. ~~Initialize Python project (`pyproject.toml`).~~ (Using inline dependencies)
2. **Rule #1:** ✅ Create `mock_sensors.py`. Write functions that return hardcoded JSON for Bee (biometrics), Ring (vision context), and Fire TV (actuation logs). 
3. **Rule #2:** ✅ Create `streamlit_app.py`. Build the 3-column layout (Biometrics | Agent Brain | Fire TV State). Wire it to read from a local JSON log file that the MCP server will write to.
4. ✅ Set up FastAPI and register the three MCP tools with handler unit tests.

### 🤖 Copilot Prompts (Strict TDD) — ✅ COMPLETED
> **Prompt 1 (Mocks):** *"Write a Python module `mock_sensors.py` with three async functions: `get_bee_state`, `get_ring_context`, and `trigger_fire_tv`. They should return predefined Pydantic models simulating a 'panic attack' scenario. Include `pytest` tests to ensure they return the correct schemas."*
> 
> **Prompt 2 (MCP Skeleton):** *"Using the MCP Python SDK, write a FastAPI app exposing an MCP Streamable HTTP endpoint. Define three tools. Write a `pytest` test using `httpx` to ensure the `/mcp` endpoint correctly handles the `initialize` and `tools/list` JSON-RPC requests."*
>
> **Result:** All prompts executed. Created `models.py`, `mock_sensors.py`, `test_mocks.py`, `mcp_server.py`, `test_mcp.py`, `streamlit_app.py`. 28 tests passing.

---

## 📅 Phase 2: The "Senses" & AWS Integration (Days 2-3)
**Goal:** Replace the mocks with real AWS Bedrock calls, but keep the mocks as a fallback.

### Action Items
1. ✅ Write the Amazon Nova (Bedrock) multimodal vision function (`aws_services.py`).
2. [ ] Write the Fire TV actuation function (which writes to the Streamlit log).
3. **Rule #3:** ✅ Write the `pytest` tests using `unittest.mock` to mock the AWS API responses *before* writing the actual `boto3` code.

### 🤖 Copilot Prompts (Strict TDD) — ✅ COMPLETED (Nova)
> **Prompt 1 (TDD for Nova):** *"I need to write a function that calls Amazon Bedrock's Amazon Nova model for image classification. First, write a `pytest` test using `unittest.mock` to patch `boto3.client`. The test should assert that when the mock returns a specific JSON, my function parses it into a `ContextSchema`. Then, write the actual function to pass the test."*
>
> **Prompt 2 (TDD for Actuation):** *"Write a `pytest` test that ensures my Fire TV actuation function correctly formats the JSON payload and appends it to a `demo_log.json` file so Streamlit can read it. Then write the function."*
>
> **Result:** Prompt 1 executed. Created `aws_services.py` with `analyze_image_context()` and `test_aws.py` (5 tests passing). Prompt 2 pending (Fire TV actuation logging).

### ✅ Phase 2 Checkpoint
- [x] Amazon Nova (Bedrock) multimodal vision function implemented (`aws_services.py`).
- [x] All AWS integration tests pass without actually hitting the AWS API.
- [x] Demo fallback paths keep the UI usable when AWS model access is blocked.

---

## 📅 Phase 3: Agentic Orchestration & Context Fusion (Day 4)
**Historical goal:** Connect the tools to Claude 3.7 Sonnet so it can reason, chain tools, and prevent false positives. The complete tool-execution loop remains unimplemented.

### Action Items
1. Complete the core agent loop using Amazon Bedrock (Claude 3.7 Sonnet).
2. Feed the MCP tool schemas into the Claude `system` prompt.
3. Write the logic to parse Claude's `toolUse` responses, execute the Python function, and feed the result back.

### 🤖 Copilot Prompts (Strict TDD)
> **Prompt 1 (Agent Loop TDD):** *"Write a `pytest` test for an agentic loop. Mock the Bedrock `converse` API to first return a `toolUse` block for `get_ring_context`, and then return a final text response. Assert that my agent loop correctly executes the tool, passes the result back to Bedrock, and returns the final text. Then, write the agent loop code to pass this test."*

### ✅ Phase 3 Checkpoint
- [x] The agent returns structured tool calls for intervention scenarios.
- [x] The agent returns safe text for non-intervention scenarios.
- [x] The agent handles retired model versions and non-recoverable AWS errors explicitly.

---

## 📅 Phase 4: The Cinematic Demo & Open Source Polish (Day 5)
**Goal:** Make it beautiful, record the video, and package the Open Source Mini-Challenge.

### Action Items
1. **Demo Flow Scripting:** Write a Python script `run_demo_scenario.py` that automatically feeds the "Panic Attack" mock data into the MCP server over 60 seconds, allowing you to just hit "Record" on the Streamlit UI and walk away.
2. **Open Source Packaging:** Create `README.md`, add MIT License, and write the "How to add your own tools" guide.
3. **Devpost Submission:** Fill out the rubric, explicitly calling out the AWS Builder and Open Source mini-challenges.

### 🤖 Copilot Prompts
> *"Write a Python script using `asyncio` that simulates a user experiencing a panic attack. It should call the MCP server's biometric tool with escalating stress levels every 10 seconds, allowing me to record a seamless, automated demo for the Streamlit UI."*

### ✅ Phase 4 Checkpoint
- [x] Demo script runs end-to-end for the panic scenario.
- [x] Streamlit demo continues operating when AWS calls are blocked or unavailable.
- [x] Reasoning traces no longer crash on fallback payloads.

---

## 🏆 Hackathon Alignment Notes

- **Primary Alexa+ protocol:** Local MCP handshake negotiates `2025-11-25`; public deployment and other submission criteria remain unverified.
- **AWS Builder:** Bedrock code paths are documented, but live calls and AWS deployment are unverified; Nova is not wired into the demo.
- **Open Source mini-challenge:** The additional `resonance-mcp-toolkit` project is not implemented or published.
- **Eligibility, judging, and external submission deliverables:** Confirm against the current Devpost rules and submission page; they cannot be verified from this repository.