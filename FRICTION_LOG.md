# Friction Log — Project Resonance

> **Purpose**: Document specific tasks attempted, steps taken, expected vs. actual results, severity ratings, workarounds used, and actionable suggestions. Per hackathon rules, friction logs score up to 10% bonus in judging.

---

## Entry 1: MCP 1.x SDK API Mismatch

**Date**: 2026-10-02  
**Task**: Import and run `mcp_server.py` locally  
**Expected**: Server starts and registers MCP tools  
**Actual**: `AttributeError: 'Server' object has no attribute 'add_request_handler'` on import  
**Severity**: 🔴 Critical (blocks all local development and testing)  
**Root Cause**: Code written against assumed decorator API (`@mcp_server.list_tools()`, `@mcp_server.call_tool()`) that doesn't exist in MCP 1.11.0. The actual SDK uses `add_request_handler(method, request_type, handler)`.

**Steps Taken**:
1. Tried `python -c "import mcp_server"` → failed
2. Inspected MCP 1.11.0 SDK: `dir(Server)` shows `add_request_handler` but no decorators
3. Tested `add_request_handler` with correct signatures: `ListToolsRequest` for `tools/list`, `CallToolRequest` for `tools/call`
4. Rewrote `mcp_server.py` to use `add_request_handler()` with proper request types
5. Kept standalone handler functions for test compatibility

**Workaround**: Used `add_request_handler("tools/list", ListToolsRequest, handler)` and `add_request_handler("tools/call", CallToolRequest, handler)` instead of decorators.

**Actionable Suggestion**: MCP SDK documentation should clearly show the 1.x handler registration pattern. The decorator API appears to be from a different version or planned feature.

**Resolution**: ✅ Fixed in `mcp_server.py` — all 38 tests pass, server imports and runs.

---

## Entry 2: Invalid MCP Version Pin

**Date**: 2026-10-02  
**Task**: Install dependencies from `requirements.txt`  
**Expected**: `pip install -r requirements.txt` succeeds  
**Actual**: `ERROR: Could not find a version that satisfies the requirement mcp==2.2.0`  
**Severity**: 🔴 Critical (blocks environment setup)  
**Root Cause**: `requirements.txt` and `pyproject.toml` pinned `mcp==2.2.0` which doesn't exist on PyPI. Latest stable is 1.x.

**Steps Taken**:
1. Ran `pip install -r requirements.txt` → failed
2. Checked PyPI: `mcp` package versions are 1.x only
3. Updated both `requirements.txt` and `pyproject.toml` to `mcp==1.11.0`
4. Re-ran install → succeeded

**Workaround**: Manual version correction.

**Actionable Suggestion**: Add CI check that validates all pinned versions exist on PyPI before merge.

**Resolution**: ✅ Fixed in `requirements.txt` and `pyproject.toml`.

---

## Entry 3: Test Compatibility Layer for `handle_call_tool`

**Date**: 2026-10-02  
**Task**: Run existing `test_mcp.py` tests against new MCP 1.x handler  
**Expected**: All 11 MCP tests pass  
**Actual**: 4 dispatcher tests failed — tests pass `CallToolRequestParams` objects, but handler expected string name  
**Severity**: 🟡 High (breaks test suite)  
**Root Cause**: Tests written for old dispatcher signature `handle_call_tool(params: CallToolRequestParams)`, but MCP 1.x handler receives `(name: str, arguments: dict)`.

**Steps Taken**:
1. Ran `pytest test_mcp.py -v` → 4 failures in `TestHandleCallToolDispatcher`
2. Analyzed test code: tests construct `CallToolRequestParams(name="...", arguments={})` and pass directly
3. Updated `handle_call_tool` signature to `Union[str, CallToolRequestParams]` with runtime type detection
4. Re-ran tests → all 11 pass

**Workaround**: Dual-signature handler accepting both string (MCP) and `CallToolRequestParams` (tests).

**Actionable Suggestion**: MCP SDK should provide a test utility or standard interface for handler testing.

**Resolution**: ✅ Fixed in `mcp_server.py` — `handle_call_tool` now handles both signatures.

---

## Entry 4: Streamlit Cloud MCP Endpoint Not Functional

**Date**: 2026-10-02  
**Task**: Verify live MCP endpoint at `https://resonancev1.streamlit.app/mcp`  
**Expected**: JSON-RPC responses for `initialize`, `tools/list`, `tools/call`  
**Actual**: Returns Streamlit HTML (200 OK but wrong content-type)  
**Severity**: 🔴 Critical for judging (judges cannot test MCP server)  
**Root Cause**: Streamlit Cloud serves the Streamlit app at all paths. The MCP server (`mcp_server.py`) is not deployed there — only `streamlit_app.py` is deployed.

**Steps Taken**:
1. `GET https://resonancev1.streamlit.app/mcp` → 200 but returns HTML
2. `POST /mcp` with JSON-RPC `initialize` → 200 but returns HTML
3. Confirmed: Streamlit app mounts at `/`, catches all routes
4. MCP server must be deployed separately (ECS/Fargate, Cloud Run, etc.)

**Workaround**: Deploy MCP server to separate endpoint (see `deploy/` for ECS/Fargate stack). Update Streamlit app to point to external MCP URL.

**Actionable Suggestion**: 
- Hackathon should clarify: "self-hosted MCP server" means separate deployment, not same origin as frontend
- Provide reference architecture for MCP + Streamlit on AWS

**Resolution**: ⏳ Pending — need to deploy MCP server to `deploy/` ECS/Fargate stack and update Streamlit config.

---

## Entry 5: Missing `run_demo_scenario.py` Automation Script

**Date**: 2026-10-02  
**Task**: Run automated demo for video recording  
**Expected**: `python run_demo_scenario.py` feeds escalating panic attack data over 60s  
**Actual**: File doesn't exist (referenced in README and Implementation Guide)  
**Severity**: 🟡 Medium (blocks automated demo recording)  
**Root Cause**: Script was planned in Phase 4 but never created.

**Steps Taken**:
1. Checked repo — no `run_demo_scenario.py`
2. Referenced in README.md line 77 and Implementation Guide.md line 138
3. Need to create script that calls MCP tools with timed progression

**Workaround**: Manual demo via Streamlit UI buttons.

**Actionable Suggestion**: Create the automation script before submission for smooth video recording.

**Resolution**: ⏳ Pending — will create now.

---

## Entry 6: AWS Bedrock Model Access Blocked by SCP

**Date**: 2026-09-29 (from Implementation Guide)  
**Task**: Call Amazon Nova (vision) and Claude 3.5 Sonnet (reasoning) via Bedrock  
**Expected**: Real AWS responses  
**Actual**: `AccessDeniedException` or model not found errors  
**Severity**: 🟡 Medium (demo falls back to simulated reasoning)  
**Root Cause**: Organizational Service Control Policies (SCPs) block Bedrock model access in some AWS accounts.

**Steps Taken**:
1. Implemented `aws_services.py` with `analyze_image_context()` (Nova) and `run_agent()` (Claude)
2. Added fallback logic in `streamlit_app.py` and `agent.py` for when AWS calls fail
3. Tests mock AWS responses so CI passes without credentials

**Workaround**: Graceful degradation to simulated agent reasoning with visible trace.

**Actionable Suggestion**: 
- Hackathon should provide pre-configured AWS accounts with Bedrock access
- Document required IAM permissions for Bedrock model invocation

**Resolution**: ✅ Mitigated — fallback paths keep demo functional.

---

## Entry 7: MCP `initialize`/`ping` Handling Not Explicitly Tested

**Date**: 2026-10-02  
**Task**: Verify MCP protocol compliance  
**Expected**: Server handles `initialize`, `ping`, `tools/list`, `tools/call`  
**Actual**: SDK handles `initialize`/`ping` internally, but not explicitly tested  
**Severity**: 🟢 Low (SDK handles it, but good to verify)  
**Root Cause**: MCP 1.x `streamable_http_app()` manages session lifecycle internally.

**Steps Taken**:
1. Tested live local server: `initialize` and `ping` work via SDK
2. No explicit unit tests for these methods

**Workaround**: Trust SDK implementation.

**Actionable Suggestion**: Add integration test for full MCP handshake flow.

**Resolution**: ⏳ Could add test, but not blocking.

---

## Entry 8: Hardcoded Localhost in Streamlit App

**Date**: 2026-10-02  
**Task**: Connect Streamlit demo to MCP server  
**Expected**: Configurable MCP endpoint URL  
**Actual**: `streamlit_app.py` hardcodes `http://localhost:8000/mcp`  
**Severity**: 🟡 Medium (breaks when MCP deployed to different host)  
**Root Cause**: Development assumption of local-only deployment.

**Steps Taken**:
1. Found hardcoded URL in `streamlit_app.py` (two locations)
2. Need to make configurable via environment variable or Streamlit config

**Workaround**: Manual code change before deployment.

**Actionable Suggestion**: Use `st.secrets` or environment variable for MCP endpoint URL.

**Resolution**: ⏳ Pending — will fix in `streamlit_app.py`.

---

## Summary

| Entry | Severity | Status |
|-------|----------|--------|
| 1. MCP API Mismatch | 🔴 Critical | ✅ Fixed |
| 2. Invalid Version Pin | 🔴 Critical | ✅ Fixed |
| 3. Test Compatibility | 🟡 High | ✅ Fixed |
| 4. Streamlit MCP Endpoint | 🔴 Critical | ⏳ Pending (deploy separately) |
| 5. Missing Demo Script | 🟡 Medium | ⏳ Pending (creating now) |
| 6. Bedrock SCP Block | 🟡 Medium | ✅ Mitigated |
| 7. MCP Handshake Tests | 🟢 Low | ⏳ Optional |
| 8. Hardcoded Localhost | 🟡 Medium | ⏳ Pending |

**Total Critical**: 3 (2 fixed, 1 pending deployment)  
**Total High/Medium**: 4 (2 fixed, 2 pending)  
**Total Low**: 1 (optional)

---

## Actionable Suggestions for Hackathon Organizers

1. **MCP SDK Version Clarity**: Publish clear migration guide from 0.x to 1.x, including handler registration patterns.
2. **Reference Deployment**: Provide CloudFormation/CDK template for "MCP Server + Streamlit Frontend" on AWS.
3. **Bedrock Access**: Offer hackathon-specific AWS accounts with pre-enabled Bedrock model access.
3. **MCP Testing Utilities**: Include test helpers in SDK for handler unit testing.
4. **Streamlit + MCP Guidance**: Document that MCP server must be separate origin from Streamlit app for CORS/protocol compliance.