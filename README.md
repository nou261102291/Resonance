# Project Resonance

> **Self-hosted Alexa+ MCP Server for Ambient Wellness Interventions**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-green.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Streamable%20HTTP-orange.svg)](https://modelcontextprotocol.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64+-red.svg)](https://streamlit.io)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-yellow.svg)](https://aws.amazon.com/bedrock/)
[![Tests](https://img.shields.io/badge/Tests-47%20passing-brightgreen.svg)](https://pytest.org)

---

## 🎯 Overview

Project Resonance is a **self-hosted MCP (Model Context Protocol) server** that orchestrates proactive wellness interventions by fusing three data streams:

| Stream | Intended source | Current prototype |
|--------|-----------------|--------------------|
| **Biometrics** | "Bee" wearable | Synthetic `ArousalStateToken` from local mocks |
| **Environmental Context** | Ring camera + Amazon Nova | Synthetic `ContextToken`; Nova classifier is implemented but not wired into the demo |
| **Actuation** | Fire TV | Local simulated actuation; no Fire TV integration |

**Privacy-oriented design goal**: Classify sensitive sensor data at the edge and pass only `ArousalStateToken` and `ContextToken` values to the reasoning agent. The current demo uses hardcoded/mock sensor values; it does not include a real wearable, camera, or edge-classification integration, so this is an intended architecture rather than a verified privacy guarantee.

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Bee       │     │   Ring      │     │  Fire TV    │
│  Wearable   │     │  + Nova     │     │  Actuation  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              MCP Server (FastAPI)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ get_bee_    │  │ get_ring_   │  │ trigger_    │  │
│  │ state       │  │ context     │  │ fire_tv     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│         Bedrock reasoning (Claude 3.7 Sonnet)        │
│  • Can return a tool-use request; no full loop       │
│  • False-positive prevention (exercise = no alert)  │
│  • Outputs actuation commands                       │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│           Streamlit Dashboard (3-Column)            │
│  Biometrics  │  Agent Brain  │  Actuation           │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- AWS Bedrock access is optional; the local demo uses synthetic data and mock actuation
- `uv` or `pip` for dependency management

### Installation

```bash
# Clone the repository
git clone https://github.com/nou261102291/Resonance.git
cd resonance

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies (`requirements.txt`)

```txt
fastapi==0.141.1
uvicorn==0.54.0
mcp==1.26.0
streamlit==1.64.0
boto3==1.43.103
pydantic==2.13.5
pytest==9.1.1
pytest-asyncio==1.4.0
httpx==0.28.1
```

---

## 🏃 Running the Demo

### 1. Start the MCP Server

```bash
# Terminal 1
python mcp_server.py
# Server runs at http://localhost:8000
# MCP endpoint: http://localhost:8000/mcp
# Health check: http://localhost:8000/health
```

### 2. Launch the Streamlit Dashboard

```bash
# Terminal 2
streamlit run streamlit_app.py
# Opens at http://localhost:8501
```

### 3. Run the Automated Demo Scenario

```bash
# Terminal 3 (optional - for cinematic demo)
python run_demo_scenario.py
# Runs a scripted demo against an MCP server; see --help for options
```

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run focused suites (AWS calls are mocked)
pytest test_mcp.py test_aws.py test_agent.py test_streamlit_app.py -v
```

**Current Status**: 47 tests passing; Bedrock calls are mocked in tests. ✅

## Amazon Bedrock Integration Status

Bedrock code exists, but this is not a live, end-to-end AWS integration:

| Path | Implementation | Current status |
|------|----------------|----------------|
| Claude reasoning | `agent.py` calls `bedrock-runtime` Converse using `anthropic.claude-3-7-sonnet-20250219-v1:0` and explicitly limits output to 512 tokens. | Live-capable call; tests mock AWS. When the model call is unavailable, the app can use simulated reasoning. |
| Nova image classification | `aws_services.py` calls Converse with Nova Lite by default (`amazon.nova-lite-v1:0`), decodes base64 JPEG input to bytes, and limits output to 100 tokens. | Implemented, but not connected to the MCP tools or Streamlit demo; no live image is captured or sent. |
| Tool execution | Claude may return a Fire TV tool-use request. | The agent function does not execute the requested tool or send a tool-result round trip. The demo simulates actuation locally; no Fire TV device is controlled. |

The ordinary demo works without AWS credentials and uses synthetic sensor/context values. Live Bedrock invocation requires model access in the configured region and AWS credentials; no live invocation or AWS deployment has been verified because account access is blocked. Image inputs sent to the Nova function would leave the application for Bedrock processing, so do not send real camera images until consent, retention, privacy, and logging controls are designed and tested.

See [BEDROCK_INTEGRATION.md](BEDROCK_INTEGRATION.md) for model flow, setup, permissions, fallbacks, data handling, and known gaps.

---

## 📁 Project Structure

```
resonance/
├── models.py              # Pydantic schemas for classified demo tokens
├── mock_sensors.py        # Mock sensor functions (Phase 1)
├── test_mocks.py          # Schema & mock tests (16 tests)
├── mcp_server.py          # FastAPI + MCP Streamable HTTP server
├── test_mcp.py            # MCP handler unit tests (12 tests)
├── aws_services.py        # Live-capable, currently unwired Bedrock Nova classifier
├── test_aws.py            # Bedrock request/response tests (mocked)
├── streamlit_app.py       # 3-column dashboard UI
├── run_demo_scenario.py   # Automated demo script (Phase 4)
├── requirements.txt       # Python dependencies
├── Implementation Guide.md # Technical implementation plan
└── README.md              # This file
```

---

## 🔧 MCP Tools Reference

### `get_bee_state`
Returns current biometric arousal state.

**Input**: `{}`  
**Output**: `ArousalStateToken`
```json
{
  "state": "critical",
  "confidence": 0.94,
  "timestamp": 1727456789.123
}
```

### `get_ring_context`
Returns environmental context from vision analysis.

**Input**: `{}`  
**Output**: `ContextToken`
```json
{
  "scene": "sedentary",
  "confidence": 0.89
}
```

### `trigger_fire_tv`
Triggers Fire TV actuation.

**Input**: 
```json
{
  "action": "play_calming_content",
  "protocol": "alexa"
}
```
**Output**: `ActuationCommand`
```json
{
  "action": "play_calming_content",
  "protocol": "alexa",
  "status": "executed"
}
```

---

## ☁️ AWS Deployment

The repo now includes a deployable AWS setup for a live demo link:

- **Exact service choice:** Amazon ECS on AWS Fargate behind an Application Load Balancer.
- **Source control linkage:** AWS CodeConnections connected to the GitHub repo.
- **Build and deploy:** AWS CodePipeline orchestrates AWS CodeBuild, Amazon ECR, and ECS deployment.
- **Container layout:** one demo container runs both `mcp_server.py` and `streamlit_app.py`.

See [deploy/README.md](deploy/README.md) for the deployment flow, required AWS resources, and the live demo architecture.

---

## 🎬 Demo Script: "Panic Attack Scenario"

The automated demo (`run_demo_scenario.py`) simulates a 60-second panic attack progression:

| Time | Biometric State | Context | Agent Action |
|------|-----------------|---------|--------------|
| 0s   | calm (0.12)     | sedentary | Monitor |
| 10s  | elevated (0.67) | sedentary | Heightened awareness |
| 20s  | elevated (0.78) | sedentary | Pre-intervention |
| 30s  | **critical (0.91)** | sedentary | **Trigger calming content** |
| 40s  | critical (0.94) | sedentary | Sustained intervention |
| 50s  | elevated (0.72) | sedentary | Tapering |
| 60s  | calm (0.21)     | sedentary | Recovery |

**False Positive Prevention**: If Ring context returns `active` (user exercising), agent **aborts** intervention even with critical biometrics.

---

## 🔐 Privacy Model (Design Target)

```
Raw Biometrics (HR, HRV, SpO2) 
         │
         ▼
┌────────────────────────┐
│   Edge Classification  │  ← Never leaves device
│   (Bee firmware)       │
└────────────────────────┘
         │
         ▼
   ArousalStateToken
   { state, confidence, timestamp }
   ── NO raw values ──► MCP Server
```

The demo currently generates synthetic classified tokens and labels them in the UI. It does not process live biometric measurements or establish that raw data is handled on-device. A real deployment must keep raw biometric and image data at the edge, transmit only the classified tokens, and verify that no sensitive values enter MCP requests, logs, or telemetry. The zero-knowledge properties shown above are design requirements, not guarantees demonstrated by this prototype.

---

## 🛠️ Development

### Adding New MCP Tools

1. Define Pydantic model in `models.py`
2. Add mock function in `mock_sensors.py`
3. Create handler in `mcp_server.py`:
   ```python
   async def handle_my_new_tool(arguments: dict) -> CallToolResult:
       result = await my_new_function(arguments)
       return CallToolResult(content=[TextContent(type="text", text=result.model_dump_json())])
   ```
4. Register in `handle_call_tool` dispatcher
5. Add unit tests in `test_mcp.py`

### Optional: Running the Claude Reasoning Path with AWS

```bash
# Configure AWS credentials
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1

# Enable access to the model in the selected region:
# - anthropic.claude-3-7-sonnet-20250219-v1:0 (reasoning)
# - amazon.nova-lite-v1:0 (image classifier; not wired to the demo)
```

The Claude call currently pins `us-east-1` in `agent.py`; the Nova classifier uses the boto3-configured region. The ECS task role currently grants `bedrock:Converse` and `bedrock:InvokeModel` on `"*"`. This is demo-only broad access, not a production policy. Scope permissions to required model resources and actions before deployment. See [BEDROCK_INTEGRATION.md](BEDROCK_INTEGRATION.md).

---

## 📋 Hackathon Alignment

| Track | Requirement | Status |
|-------|-------------|--------|
| **Primary (Alexa+)** | Self-hosted MCP server using Streamable HTTP; server negotiates protocol `2025-11-25` | ✅ Local protocol handshake verified; separate public deployment remains pending |
| **AWS Builder** | Demonstrable use of AWS services / Bedrock | 🟡 Bedrock invocation code exists, but AWS access is blocked, calls are unverified live, and Nova is unwired. Do not claim a live AWS deployment. |
| **Open Source mini-challenge** | Additional open-source project/toolkit | ❌ `resonance-mcp-toolkit` has not been packaged or published |
| **Design / impact** | Product and impact claims | Project intent only; judging outcome and submission eligibility cannot be verified from this repository |

The official [AppDev 2026 rules](https://amazonappdev2026.devpost.com/rules) could not be fetched from this environment (HTTP 403). Re-check the exact track criteria, eligibility, deadlines, public-repository requirement, and video/submission deliverables on Devpost before submitting. Protocol support is now aligned to the `2025-11-25` requirement reported for Alexa+; this local check does not establish that the submission meets all other criteria.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Write tests first (TDD)
4. Implement feature
5. Run tests: `pytest -v`
6. Submit PR

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **MCP Team** — Model Context Protocol specification
- **AWS Bedrock** — Claude 3.7 Sonnet & Amazon Nova (code paths; live use unverified)
- **Anthropic** — Constitutional AI principles
- **Streamlit** — Rapid dashboard prototyping

---

## 📞 Contact

- **Project Lead**: nou261102291@noun.edu.ng
- **Issues**: [GitHub Issues](https://github.com/nou261102291/Resonance/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nou261102291/Resonance/discussions)

---

> Built with ❤️ for the Alexa+ Hackathon — *"Making the invisible agent reasoning visible"*
