# Project Resonance

> **Self-hosted Alexa+ MCP Server for Ambient Wellness Interventions**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-green.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Streamable%20HTTP-orange.svg)](https://modelcontextprotocol.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64+-red.svg)](https://streamlit.io)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-yellow.svg)](https://aws.amazon.com/bedrock/)
[![Tests](https://img.shields.io/badge/Tests-38%20passing-brightgreen.svg)](https://pytest.org)

---

## 🎯 Overview

Project Resonance is a **self-hosted MCP (Model Context Protocol) server** that orchestrates proactive wellness interventions by fusing three data streams:

| Stream | Source | Purpose |
|--------|--------|---------|
| **Biometrics** | "Bee" Wearable | Heart rate, HRV, stress levels → `ArousalStateToken` |
| **Environmental Context** | Ring Camera + Amazon Nova | Vision classification: `sedentary` \| `active` \| `outdoor` \| `unknown` |
| **Actuation** | Fire TV | Play calming content, adjust ambient lighting |

**Core Innovation**: Zero-knowledge architecture; raw biometric data never leaves the edge. Only classified tokens (`ArousalStateToken`, `ContextToken`) flow through the MCP server to the reasoning agent.

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
│           Agent Loop (Claude 3.5 Sonnet)            │
│  • Chains tools: bee → ring → fire_tv               │
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

- Python 3.11+
- AWS Account with Bedrock access (for Phase 2+)
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
mcp==1.11.0
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
# Feeds escalating panic attack data over 60 seconds
```

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run specific test suites
pytest test_mocks.py -v      # 16 tests - Pydantic schemas & mock sensors
pytest test_mcp.py -v        # 12 tests - MCP tool handlers (unit)
pytest test_aws.py -v        # 5 tests  - AWS Bedrock integration (mocked)
```

**Current Status**: 38 tests passing ✅

---

## 📁 Project Structure

```
resonance/
├── models.py              # Pydantic schemas (Zero-Knowledge tokens)
├── mock_sensors.py        # Mock sensor functions (Phase 1)
├── test_mocks.py          # Schema & mock tests (16 tests)
├── mcp_server.py          # FastAPI + MCP Streamable HTTP server
├── test_mcp.py            # MCP handler unit tests (12 tests)
├── aws_services.py        # Bedrock Nova integration (Phase 2)
├── test_aws.py            # AWS integration tests (5 tests)
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

## 🔐 Zero-Knowledge Architecture

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

**Privacy Guarantees**:
- Raw biometrics processed on-device
- Only classified tokens transmitted
- No PII in MCP payloads
- Audit trail via `demo_log.json`

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

### Running with Real AWS (Phase 2+)

```bash
# Configure AWS credentials
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1

# Enable Bedrock models in AWS Console:
# - amazon.nova-lite-v1:0 (vision)
# - anthropic.claude-3-5-sonnet-20241022-v2:0 (reasoning)
```

---

## 📋 Hackathon Alignment

| Track | Requirement | Status |
|-------|-------------|--------|
| **Primary (Alexa+)** | Self-hosted MCP Server (Streamable HTTP) | ✅ |
| **AWS Builder** | Bedrock (Claude + Nova) integration | 🟡 Phase 2 |
| **Open Source** | `resonance-mcp-toolkit` package | ⏳ Phase 4 |
| **Design** | Visible agent reasoning (Streamlit) | ✅ |
| **Impact** | Proactive cognitive load management | ✅ |

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
- **AWS Bedrock** — Claude 3.5 Sonnet & Amazon Nova
- **Anthropic** — Constitutional AI principles
- **Streamlit** — Rapid dashboard prototyping

---

## 📞 Contact

- **Project Lead**: nou261102291@noun.edu.ng
- **Issues**: [GitHub Issues](https://github.com/nou261102291/Resonance/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nou261102291/Resonance/discussions)

---

> Built with ❤️ for the Alexa+ Hackathon — *"Making the invisible agent reasoning visible"*
