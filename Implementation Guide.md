# Project Resonance: Technical Implementation Plan (v2.0 - Strict Execution)

## 🎯 Objective
Build a self-hosted Alexa+ MCP Server that orchestrates ambient wellness interventions by fusing biometric data (Bee), environmental context (Ring/Amazon Nova), and media actuation (Fire TV).

## 🛑 The 3 Golden Rules of this Hackathon
1. **Mock First, Integrate Later:** We will NOT wait on physical hardware or buggy SDKs. We build `mock_sensors.py` on Day 1. The MCP server only cares about the JSON payload.
2. **The Demo is the Product:** We build the Streamlit UI shell on Day 1. We do not wait until the end to visualize the agent. If we can't see it thinking, we can't debug it.
3. **Strict TDD via Copilot:** We write the `pytest` tests *before* the implementation. Copilot will generate the tests first, ensuring we stay exactly on track with the rubric.

## 🛠️ Core Tech Stack
- **Language:** Python 3.11+
- **MCP Framework:** Official MCP Python SDK (Streamable HTTP)
- **AI/Reasoning:** Amazon Bedrock (Claude 3.5 Sonnet for logic, Amazon Nova for multimodal vision)
- **API Framework:** FastAPI (for the MCP HTTP transport)
- **Demo UI:** Streamlit (Continuous visual feedback)
- **Testing:** `pytest` and `pytest-asyncio`

---

## 📅 Phase 1: Foundation, Mocks & The Visual Shell (Day 1)
**Goal:** Establish the MCP server, hardcode the mocks, and build the Streamlit UI shell. No AWS calls yet.

### Action Items
1. Initialize Python project (`pyproject.toml`).
2. **Rule #1:** Create `mock_sensors.py`. Write functions that return hardcoded JSON for Bee (biometrics), Ring (vision context), and Fire TV (actuation logs). 
3. **Rule #2:** Create `streamlit_app.py`. Build the 3-column layout (Biometrics | Agent Brain | Fire TV State). Wire it to read from a local JSON log file that the MCP server will write to.
4. Set up FastAPI and register the three empty MCP tools.

### 🤖 Copilot Prompts (Strict TDD)
> **Prompt 1 (Mocks):** *"Write a Python module `mock_sensors.py` with three async functions: `get_bee_state`, `get_ring_context`, and `trigger_fire_tv`. They should return predefined Pydantic models simulating a 'panic attack' scenario. Include `pytest` tests to ensure they return the correct schemas."*
> 
> **Prompt 2 (MCP Skeleton):** *"Using the MCP Python SDK, write a FastAPI app exposing an MCP Streamable HTTP endpoint. Define three tools. Write a `pytest` test using `httpx` to ensure the `/mcp` endpoint correctly handles the `initialize` and `tools/list` JSON-RPC requests."*

### ✅ Phase 1 Checkpoint
- [ ] `mock_sensors.py` passes all schema tests.
- [ ] Streamlit UI renders the 3 columns, even if the data is currently static/hardcoded.
- [ ] MCP Server starts locally and passes the `tools/list` test.

---

## 📅 Phase 2: The "Senses" & AWS Integration (Days 2-3)
**Goal:** Replace the mocks with real AWS Bedrock calls, but keep the mocks as a fallback.

### Action Items
1. Write the Amazon Nova (Bedrock) multimodal vision function.
2. Write the Fire TV actuation function (which writes to the Streamlit log).
3. **Rule #3:** Write the `pytest` tests using `moto` or `unittest.mock` to mock the AWS API responses *before* writing the actual `boto3` code.

### 🤖 Copilot Prompts (Strict TDD)
> **Prompt 1 (TDD for Nova):** *"I need to write a function that calls Amazon Bedrock's Amazon Nova model for image classification. First, write a `pytest` test using `unittest.mock` to patch `boto3.client`. The test should assert that when the mock returns a specific JSON, my function parses it into a `ContextSchema`. Then, write the actual function to pass the test."*
>
> **Prompt 2 (TDD for Actuation):** *"Write a `pytest` test that ensures my Fire TV actuation function correctly formats the JSON payload and appends it to a `demo_log.json` file so Streamlit can read it. Then write the function."*

### ✅ Phase 2 Checkpoint
- [ ] All AWS integration tests pass without actually hitting the AWS API (fully mocked).
- [ ] When running the real code, it successfully hits Bedrock and updates the Streamlit UI.

---

## 📅 Phase 3: Agentic Orchestration & Context Fusion (Day 4)
**Goal:** Connect the tools to Claude 3.5 Sonnet so it can reason, chain tools, and prevent false positives.

### Action Items
1. Implement the core agent loop using Amazon Bedrock (Claude 3.5 Sonnet).
2. Feed the MCP tool schemas into the Claude `system` prompt.
3. Write the logic to parse Claude's `toolUse` responses, execute the Python function, and feed the result back.

### 🤖 Copilot Prompts (Strict TDD)
> **Prompt 1 (Agent Loop TDD):** *"Write a `pytest` test for an agentic loop. Mock the Bedrock `converse` API to first return a `toolUse` block for `get_ring_context`, and then return a final text response. Assert that my agent loop correctly executes the tool, passes the result back to Bedrock, and returns the final text. Then, write the agent loop code to pass this test."*

### ✅ Phase 3 Checkpoint
- [ ] The agent successfully chains `get_bee_state` -> `get_ring_context` -> `trigger_fire_tv`.
- [ ] The "False Positive" test passes (Agent correctly aborts intervention if Ring context is "active/exercising").

---

## 📅 Phase 4: The Cinematic Demo & Open Source Polish (Day 5)
**Goal:** Make it beautiful, record the video, and package the Open Source Mini-Challenge.

### Action Items
1. **Demo Flow Scripting:** Write a Python script `run_demo_scenario.py` that automatically feeds the "Panic Attack" mock data into the MCP server over 60 seconds, allowing you to just hit "Record" on the Streamlit UI and walk away.
2. **Open Source Packaging:** Create `README.md`, add MIT License, and write the "How to add your own tools" guide.
3. **Devpost Submission:** Fill out the rubric, explicitly calling out the AWS Builder and Open Source mini-challenges.

### 🤖 Copilot Prompts
> *"Write a Python script using `asyncio` that simulates a user experiencing a panic attack. It should call the MCP server's biometric tool with escalating stress levels every 10 seconds, allowing me to record a seamless, automated demo for the Streamlit UI."*

---

## 🏆 Final Hackathon Alignment Checklist

- [ ] **Primary Track (Alexa+):** Is the core a self-hosted MCP server (Streamable HTTP)? *Yes.*
- [ ] **AWS Builder:** Are we using AWS services with documented integrations? *Yes, Bedrock (Claude & Nova).*
- [ ] **Open Source:** Is there a new, additional open-source project? *Yes, the `resonance-mcp-toolkit`.*
- [ ] **Design:** Is the interaction model intuitive? *Yes, the Streamlit UI makes the invisible agent reasoning visible.*
- [ ] **Impact:** Does it solve a credible need? *Yes, proactive cognitive load management.*